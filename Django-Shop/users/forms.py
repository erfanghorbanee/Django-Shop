from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm
from phonenumber_field.formfields import SplitPhoneNumberField
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
