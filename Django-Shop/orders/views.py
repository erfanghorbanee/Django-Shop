from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView, View

from .models import Order, PaymentMethod

# Create your views here.


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


class PaymentMethodListView(LoginRequiredMixin, ListView):
    model = PaymentMethod
    template_name = "orders/payment_methods.html"
    context_object_name = "payment_methods"

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)


@method_decorator(require_POST, name="dispatch")
class PaymentMethodCreateView(LoginRequiredMixin, CreateView):
    model = PaymentMethod
    fields = [
        "payment_type",
        "card_number",
        "card_holder_name",
        "expiry_date",
        "is_default",
    ]
    success_url = reverse_lazy("orders:payment_methods")

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Store only last 4 digits of card number
        form.instance.card_number = form.cleaned_data["card_number"][-4:]
        response = super().form_valid(form)
        messages.success(self.request, "Payment method added successfully!")
        return response


@method_decorator(require_POST, name="dispatch")
class PaymentMethodDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        payment_method = get_object_or_404(PaymentMethod, pk=pk, user=request.user)
        payment_method.delete()
        messages.success(request, "Payment method deleted successfully!")
        return redirect("orders:payment_methods")


@method_decorator(require_POST, name="dispatch")
class SetDefaultPaymentMethodView(LoginRequiredMixin, UpdateView):
    model = PaymentMethod
    fields = ["is_default"]
    success_url = reverse_lazy("orders:payment_methods")

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)

    def form_valid(self, form):
        # Set all payment methods as non-default
        PaymentMethod.objects.filter(user=self.request.user).update(is_default=False)
        form.instance.is_default = True
        response = super().form_valid(form)
        messages.success(self.request, "Default payment method updated successfully!")
        return response
