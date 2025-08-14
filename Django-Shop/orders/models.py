from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse
from payments import PurchasedItem
from payments.models import BasePayment
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order_set"
    )
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    shipping_address = models.ForeignKey(
        "users.Address",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_shipping_set",
    )
    billing_address = models.ForeignKey(
        "users.Address",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_billing_set",
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.ForeignKey(
        "PaymentMethod", on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_number}"

    @property
    def total(self) -> Decimal:
        # Keep a convenient property aligning with payments API naming
        return self.total_amount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ("credit_card", "Credit Card"),
        ("debit_card", "Debit Card"),
        ("paypal", "PayPal"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_payment_methods",
    )
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    card_number = models.CharField(max_length=16)  # Last 4 digits only
    card_holder_name = models.CharField(max_length=255)
    expiry_date = models.CharField(max_length=5)  # MM/YY format
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.get_payment_type_display()} - ****{self.card_number[-4:]}"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other payment methods as non-default
            PaymentMethod.objects.filter(user=self.user).exclude(id=self.id).update(
                is_default=False
            )
        super().save(*args, **kwargs)


class Payment(BasePayment):
    """Payment record managed by django-payments, attached to an Order."""

    order = models.ForeignKey(
        "orders.Order", on_delete=models.PROTECT, related_name="payments"
    )

    def get_failure_url(self) -> str:
        return reverse("orders:payment_failed", args=[self.order_id])

    def get_success_url(self) -> str:
        return reverse("orders:payment_success", args=[self.order_id])

    def get_purchased_items(self):
        # Charge the full order as a single line; keeps provider-agnostic and simple
        yield PurchasedItem(
            name=f"Order #{self.order.order_number}",
            sku=f"ORDER-{self.order_id}",
            quantity=1,
            price=Decimal(self.total),
            currency=self.currency,
        )
