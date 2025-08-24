from django.shortcuts import redirect, render
from django.views import View

from .forms import SupportRequestForm

# Create your views here.


class SupportRequestView(View):
    def get(self, request):
        form = SupportRequestForm()
        return render(request, "support/support_form.html", {"form": form})

    def post(self, request):
        form = SupportRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("support:success")
        return render(request, "support/support_form.html", {"form": form})


def support_success(request):
    return render(request, "support/support_success.html")
