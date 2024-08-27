from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from .managers import CustomUserManager


def validate_image_size(image):
    file_size = image.file.size
    limit_mb = 2
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError(f"Max size of file is {limit_mb} MB")


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(("email address"), unique=True)
    USERNAME_FIELD = "email"

    # will be required when creating a superuser.
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()
    phone = PhoneNumberField(null=False, blank=False)

    # TODO: Process image before saving
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        default='profile_pictures/default1.png',
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png"]),
            validate_image_size,
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
