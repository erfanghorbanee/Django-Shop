from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image

from .exceptions import CannotDeleteOnlyAddress, CannotDemoteOnlyPrimary
from .managers import CustomUserManager


def validate_image(file):
    """
    Validates that an uploaded image:
    1. Is a readable, non-corrupt image file.
    2. Is one of the allowed formats (e.g., JPEG or PNG).
    3. Does not exceed the maximum size.
    """
    max_size = 5 * 1024 * 1024  # 5 MB

    # Check file size
    if file.size > max_size:
        raise ValidationError("Image size must be no more than 5 MB.")

    # Attempt to open and verify the image
    try:
        image = Image.open(file)
        image.verify()
    except Exception:
        raise ValidationError("Uploaded file is not a valid or readable image.")
    finally:
        file.seek(0)  # Reset file pointer after reading

    # Check format after verify() — image.format is preserved in the object
    allowed_formats = ["JPEG", "PNG"]
    if image.format not in allowed_formats:
        raise ValidationError(
            "Unsupported image format. Only JPEG and PNG are allowed."
        )


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(("email address"), unique=True)
    USERNAME_FIELD = "email"

    # will be required when creating a superuser and must contain all required fields on your user model.
    # https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#django.contrib.auth.models.CustomUser.REQUIRED_FIELDS
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "phone",
    ]

    objects = CustomUserManager()
    phone = PhoneNumberField(unique=True, null=True)

    # TODO: Process image before saving
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        default="profile_pictures/default1.png",
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png"]),
            validate_image,
        ],
    )

    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    PREFER_NOT_TO_SAY = "X"

    GENDER_CHOICES = [
        (MALE, "Male"),
        (FEMALE, "Female"),
        (OTHER, "Other"),
        (PREFER_NOT_TO_SAY, "Prefer not to say"),
    ]

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default=PREFER_NOT_TO_SAY,
    )

    def __str__(self):
        return self.email


class Address(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="addresses"
    )
    street_address = models.CharField(max_length=255)
    apartment_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ["-is_primary", "-created_at"]
        # Ensure at most one primary address per user at the DB level
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(is_primary=True),
                name="uniq_primary_address_per_user",
            )
        ]
        # Common query patterns: filter by user / primary flag, list recent
        indexes = [
            models.Index(fields=["user", "is_primary"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.street_address}, {self.city}"

    def save(self, *args, **kwargs):
        """Maintain primary address invariants and rely on DB constraint for uniqueness.

        - First address for a user becomes primary.
        - Prevent unmarking the only existing primary (keeps at least one primary).
                - If a primary is explicitly demoted while other addresses exist, automatically
                    promote another address to remain primary.
        - When saving a primary, demote any other primaries inside an atomic block.
        - Any IntegrityError (rare concurrent promotion) is allowed to bubble up for the view
          to handle gracefully.
        """

        # 1. First address automatically primary.
        if self._state.adding and not Address.objects.filter(user=self.user).exists():
            self.is_primary = True

        # Determine prior primary status (before current changes)
        was_primary = False
        if self.pk:
            was_primary = Address.objects.filter(pk=self.pk, is_primary=True).exists()

        # 2. Prevent unsetting the last remaining primary (would leave zero primaries) OR
        #    auto-promote another address if demoting this primary while others exist.
        if not self._state.adding and was_primary and not self.is_primary:
            # Are there other addresses?
            qs_others = Address.objects.filter(user=self.user).exclude(pk=self.pk)
            if not qs_others.exists():
                # No others: cannot demote; raise explicit domain error so caller can show message.
                raise CannotDemoteOnlyPrimary()
            else:
                # There are others: we will demote this one and promote a candidate.
                with transaction.atomic():
                    # Save this instance as non-primary first.
                    super(Address, self).save(*args, **kwargs)
                    candidate = qs_others.order_by("-is_primary", "-created_at").first()
                    if candidate and not candidate.is_primary:
                        candidate.is_primary = True
                        # candidate.save will demote others (already demoted current).
                        candidate.save()
                return

        # 3. Demote existing primary rows if this is (or stays) primary.
        with transaction.atomic():
            if self.is_primary:
                (
                    Address.objects.select_for_update()
                    .filter(user=self.user, is_primary=True)
                    .exclude(pk=self.pk)
                    .update(is_primary=False)
                )
            super().save(*args, **kwargs)


class Wishlist(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="wishlist"
    )
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "product"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email}'s wishlist - {self.product.name}"


# --- Signals for Address invariants (model-centric deletion handling) ---


@receiver(pre_delete, sender=Address)
def prevent_deleting_only_address(sender, instance, **kwargs):
    """Block deletion if this is the user's only address.

    Keeps invariant: user always has at least one address (and therefore a primary).
    Raises a domain-specific exception so the view can present a tailored message.
    """
    siblings_exist = (
        Address.objects.filter(user=instance.user).exclude(pk=instance.pk).exists()
    )
    if not siblings_exist:
        raise CannotDeleteOnlyAddress()


@receiver(post_delete, sender=Address)
def promote_new_primary_after_deletion(sender, instance, **kwargs):
    """After deleting a primary address, promote another if needed.

    Runs only if the deleted address was primary and others remain. Chooses the most
    recently created (ordering already -is_primary, -created_at) non-primary candidate.
    """
    if not instance.is_primary:
        return
    candidate = (
        Address.objects.filter(user=instance.user)
        .order_by("-is_primary", "-created_at")
        .first()
    )
    if candidate and not candidate.is_primary:
        candidate.is_primary = True
        # Use save() to reuse demotion logic (safe—only one will become primary).
        candidate.save()
