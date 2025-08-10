from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.db.models import Q
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
        """
        Responsibilities kept here (fat model, explicit logic):
        - First address auto primary.
        - Disallow demoting the only address (raise domain error).

        Promotion of another address after deleting or demoting a primary address
        is handled by dedicated methods (switch_primary / delete override).
        """

        # Automatically set first address as primary
        if self._state.adding and not Address.objects.filter(user=self.user).exists():
            self.is_primary = True

        # Check if we are updating an existing address
        if self.pk:
            was_primary = Address.objects.filter(pk=self.pk, is_primary=True).exists()
            # Prevent leaving user with zero primaries by demoting the only one directly.
            if was_primary and not self.is_primary:
                others_exist = (
                    Address.objects.filter(user=self.user).exclude(pk=self.pk).exists()
                )
                if not others_exist:
                    raise CannotDemoteOnlyPrimary()

        with transaction.atomic():
            if self.is_primary:
                (
                    Address.objects.select_for_update()
                    .filter(user=self.user, is_primary=True)
                    .exclude(pk=self.pk)
                    .update(is_primary=False)
                )
            super().save(*args, **kwargs)

    # --- Explicit domain operations (preferred over signals) ---
    @classmethod
    def switch_primary(cls, user, new_primary_id):
        """Set given address (by id) as primary for user.

        Demotes any existing primary, promotes the target. Returns the updated address.
        """
        with transaction.atomic():
            target = cls.objects.select_for_update().get(pk=new_primary_id, user=user)
            if target.is_primary:
                return target
            cls.objects.filter(user=user, is_primary=True).update(is_primary=False)
            target.is_primary = True
            target.save(update_fields=["is_primary", "updated_at"])
            return target

    def delete(self, *args, **kwargs):
        """Override delete to maintain invariants explicitly.

        - Block deleting the only address.
        - If deleting a primary and others remain, promote the most recent other (created_at).
        """
        siblings = Address.objects.filter(user=self.user).exclude(pk=self.pk)
        if not siblings.exists():
            raise CannotDeleteOnlyAddress()
        promote_candidate = None
        if self.is_primary:
            promote_candidate = siblings.order_by("-is_primary", "-created_at").first()
        with transaction.atomic():
            result = super().delete(*args, **kwargs)
            if promote_candidate and not promote_candidate.is_primary:
                promote_candidate.is_primary = True
                promote_candidate.save(update_fields=["is_primary", "updated_at"])
        return result


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
