from django.contrib import admin

from .models import Order, OrderItem, PaymentMethod


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "status",
        "shipping_address",
        "billing_address",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "order_number",
        "user__email",
        "shipping_address__street_address",
        "billing_address__street_address",
    )
    raw_id_fields = ("user", "shipping_address", "billing_address", "payment_method")
    inlines = [OrderItemInline]


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "payment_type",
        "card_holder_name",
        "is_default",
        "created_at",
    )
    list_filter = ("payment_type", "is_default", "created_at")
    search_fields = ("user__email", "card_holder_name")
