from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
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
        image.verify()  # Verifies that it's a valid, complete image
    except Exception:
        raise ValidationError("Uploaded file is not a valid or readable image.")
    finally:
        file.seek(0)  # Reset file pointer after reading

    # Check format after verify() — image.format is preserved in the object
    allowed_formats = ['JPEG', 'PNG']
    if image.format not in allowed_formats:
        raise ValidationError("Unsupported image format. Only JPEG and PNG are allowed.")


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(("email address"), unique=True)
    USERNAME_FIELD = "email"

    # will be required when creating a superuser and must contain all required fields on your user model.
    # https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#django.contrib.auth.models.CustomUser.REQUIRED_FIELDS
    REQUIRED_FIELDS = ["first_name", "last_name", "phone",]

    objects = CustomUserManager()
    phone = PhoneNumberField(unique=True)

    # TODO: Process image before saving
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        default='profile_pictures/default1.png',
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
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
        verbose_name_plural = 'Addresses'
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.street_address}, {self.city}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Set all other addresses as non-primary
            Address.objects.filter(user=self.user).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email}'s wishlist - {self.product.name}"
