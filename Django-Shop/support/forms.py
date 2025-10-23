from django import forms
from django.utils.translation import gettext_lazy as _

from .models import SupportRequest


class SupportRequestForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ["name", "email", "subject", "message"]
        labels = {
            "name": _("Name"),
            "email": _("Email"),
            "subject": _("Subject"),
            "message": _("Message"),
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": _("Enter your name")}),
            "email": forms.EmailInput(attrs={"placeholder": _("Enter your email")}),
            "subject": forms.TextInput(attrs={"placeholder": _("How can we help?")}),
            "message": forms.Textarea(attrs={"placeholder": _("Describe your issue...")}),
        }
