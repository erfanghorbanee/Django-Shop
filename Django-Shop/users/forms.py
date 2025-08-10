from allauth.account.forms import SignupForm
from django import forms
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import SplitPhoneNumberField

from .models import Address, CustomUser


class CustomSignupForm(SignupForm):
    phone = SplitPhoneNumberField()

    # Check if a user with the same phone number already exists
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if CustomUser.objects.filter(phone=phone).exists():
            raise ValidationError("A user with this phone number already exists.")
        return phone

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.phone = self.cleaned_data["phone"]
        user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Form for updating user profile information."""

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone", "gender", "profile_picture"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        # Check if another user already has this phone number
        if CustomUser.objects.exclude(id=self.instance.id).filter(phone=phone).exists():
            raise ValidationError("A user with this phone number already exists.")
        return phone

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get("profile_picture")
        # The model validators will handle size and extension validation
        return profile_picture


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "street_address",
            "apartment_address",
            "city",
            "state",
            "zip_code",
            "country",
        ]
        widgets = {
            "street_address": forms.TextInput(attrs={"class": "form-control"}),
            "apartment_address": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "zip_code": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super().save(commit=False)
        if not obj.pk:
            obj.user = self.user
        if commit:
            obj.save()
        return obj
