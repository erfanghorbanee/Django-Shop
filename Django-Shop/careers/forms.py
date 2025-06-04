from django import forms
from .models import CareerApplication

class CareerApplicationForm(forms.ModelForm):
    class Meta:
        model = CareerApplication
        fields = ['name', 'email', 'phone', 'resume', 'cover_letter'] 