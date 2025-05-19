from django.contrib import admin
from .models import Order, OrderItem, PaymentMethod

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__email')
    inlines = [OrderItemInline]

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_type', 'card_holder_name', 'is_default', 'created_at')
    list_filter = ('payment_type', 'is_default', 'created_at')
    search_fields = ('user__email', 'card_holder_name')
