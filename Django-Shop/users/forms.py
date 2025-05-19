from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm
from phonenumber_field.formfields import SplitPhoneNumberField
from django import forms
from .models import CustomUser


class CustomSignupForm(SignupForm):
    phone = SplitPhoneNumberField()

    # Check if a user with the same phone number already exists
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exists():
            raise ValidationError("A user with this phone number already exists.")
        return phone

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.phone = self.cleaned_data['phone']
        user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Form for updating user profile information."""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone', 'gender', 'profile_picture']
        
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Check if another user already has this phone number
        if CustomUser.objects.exclude(id=self.instance.id).filter(phone=phone).exists():
            raise ValidationError("A user with this phone number already exists.")
        return phone
        
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        # The model validators will handle size and extension validation
        return profile_picture
