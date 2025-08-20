from decimal import Decimal

from cart.models import Cart
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from payments import RedirectNeeded, get_payment_model
from users.models import Address

from .models import Order

# Create your views here.


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


@login_required
def start_payment(request, order_id: int):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    Payment = get_payment_model()
    # GET should not create or mutate state; only reuse existing in-progress payment
    payment = (
        Payment.objects.filter(order=order, variant="stripe")
        .exclude(status="confirmed")
        .order_by("-created")
        .first()
    )
    if not payment:
        messages.error(
            request,
            "No active payment session for this order. Please checkout again.",
        )
        return redirect("cart:detail")
    try:
        form = payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))
    # Provider wants a form POST
    return render(
        request, "orders/payment_form.html", {"form": form, "payment": payment}
    )


@login_required
def payment_success(request, order_id: int):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    messages.success(request, f"Payment confirmed for Order #{order.order_number}.")
    return render(request, "orders/payment_success.html", {"order": order})


@login_required
def payment_failed(request, order_id: int):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    messages.error(
        request, f"Payment failed for Order #{order.order_number}. Please try again."
    )
    return render(request, "orders/payment_failed.html", {"order": order})


@login_required
@require_POST
def checkout_from_cart(request):
    cart = Cart.get_or_create_for_request(request)
    if not cart.total_quantity:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:detail")

    # Require at least one address
    user_addresses = Address.objects.filter(user=request.user)
    if not user_addresses.exists():
        messages.error(
            request, ("You need to add at least one address before checking out.")
        )
        return redirect("users:addresses")

    order = Order.create_from_cart(cart=cart, user=request.user)
    # Create a payment in POST (safe from CSRF); GET view will only present/redirect
    Payment = get_payment_model()
    payment = (
        Payment.objects.filter(order=order, variant="stripe")
        .exclude(status="confirmed")
        .order_by("-created")
        .first()
    )
    if not payment:
        Payment.objects.create(
            variant="stripe",
            description=f"Order #{order.order_number}",
            total=Decimal(order.total_amount),
            currency="USD",  # Adjust if needed
            billing_email=getattr(order, "user", None) and order.user.email or "",
            order=order,
        )
    cart.clear()
    return redirect("orders:start_payment", order_id=order.id)
