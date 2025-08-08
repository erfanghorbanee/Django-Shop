from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import IntegrityError, models, transaction
from django.db.models import Q
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image

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
        """Enforce single primary with DB constraint + transactional demotion.

        We optimistically (and atomically) demote any existing primary before saving this
        address as primary. Concurrency considerations:
        - Two requests might try to promote different addresses concurrently.
        - We lock the *current* primaries for the user (SELECT ... FOR UPDATE) inside a
          transaction so only one transaction can proceed with demotion at a time.
        - The partial unique constraint (user, condition=is_primary=True) in the DB is the
          final guard. If a race still slips through (extremely rare window), we retry once.
        - A bounded retry avoids infinite loops while providing a clean resolution path.
        """

        # Only need special handling if attempting / keeping primary state. Non-primary saves
        # can proceed normally (but we still go through unified logic for simplicity).
        attempts = 2  # initial try + 1 retry on IntegrityError
        while attempts:
            try:
                with transaction.atomic():
                    if self.is_primary:
                        # Lock any existing primary rows for this user to prevent a concurrent
                        # transaction from reading stale state and also trying to promote.
                        (
                            Address.objects.select_for_update()
                            .filter(user=self.user, is_primary=True)
                            .exclude(id=self.id)
                            .update(is_primary=False)
                        )
                    # Perform the actual insert/update. The partial unique constraint will
                    # raise IntegrityError if another transaction committed a primary first.
                    super().save(*args, **kwargs)
                # Success path: break out of retry loop.
                break
            except IntegrityError:
                attempts -= 1
                # Retry only if: (a) we were setting primary, (b) we still have a retry left.
                if not self.is_primary or attempts == 0:
                    raise
                # Loop to retry: another transaction won the race; on next iteration we will
                # lock and demote again based on the now-current state.
                continue


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
