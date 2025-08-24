from django import forms
from phonenumber_field.formfields import SplitPhoneNumberField

from .models import CareerApplication


class CareerApplicationForm(forms.ModelForm):
    phone = SplitPhoneNumberField(required=False)

    class Meta:
        model = CareerApplication
        fields = ["name", "email", "phone", "resume", "cover_letter"]
