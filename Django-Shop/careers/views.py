from django.shortcuts import redirect, render
from django.views import View

from .forms import CareerApplicationForm


class CareerApplicationView(View):
    def get(self, request):
        form = CareerApplicationForm()
        return render(request, 'careers/career_form.html', {'form': form})

    def post(self, request):
        form = CareerApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('careers:success')
        return render(request, 'careers/career_form.html', {'form': form})

def career_success(request):
    return render(request, 'careers/career_success.html')
