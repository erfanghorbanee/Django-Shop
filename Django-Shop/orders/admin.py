from django.contrib import admin

from .models import Order, OrderItem, Payment


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
    raw_id_fields = ("user", "shipping_address", "billing_address")
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "variant", "status", "total", "currency", "created")
    list_filter = ("variant", "status", "currency", "created")
    search_fields = ("id", "order__order_number", "description")
