import magic
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


def validate_pdf(file):
    """
    This performs two checks:
    1. Ensures the file size is within the allowed maximum (in bytes).
    2. Uses libmagic (via python-magic) to analyze the file's magic bytes and verify its actual MIME.
    """

    # Maximum allowed size (5 MB)
    max_size = 5 * 1024 * 1024

    # Check file size
    if file.size > max_size:
        raise ValidationError("File size must be 5 MB or less.")

    # Read the first 2048 bytes (recommendation from python-magic)
    sample = file.read(2048)

    # Reset the file pointer to the beginning, so Django can process the file later
    file.seek(0)

    # Detect file's actual MIME type based on content
    mime = magic.from_buffer(sample, mime=True)

    # Check if the detected MIME type is PDF
    if mime != "application/pdf":
        raise ValidationError("Uploaded file is not a valid PDF.")


class CareerApplication(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = PhoneNumberField(blank=True)
    resume = models.FileField(
        upload_to="resumes/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"]), validate_pdf],
    )
    cover_letter = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
