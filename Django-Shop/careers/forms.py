from django import forms
from .models import CareerApplication
from phonenumber_field.formfields import SplitPhoneNumberField

class CareerApplicationForm(forms.ModelForm):
    phone = SplitPhoneNumberField(required=False)
    class Meta:
        model = CareerApplication
        fields = ['name', 'email', 'phone', 'resume', 'cover_letter'] 