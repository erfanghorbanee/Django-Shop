from django import forms
from allauth.account.forms import SignupForm
from phonenumber_field.formfields import SplitPhoneNumberField


class CustomSignupForm(SignupForm):
    phone = SplitPhoneNumberField()

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.phone = self.cleaned_data['phone']
        user.save()
        return user
