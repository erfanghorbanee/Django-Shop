from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from payments import PaymentStatus

from .exceptions import OrderOutOfStock
from .models import Payment


@receiver(post_save, sender=Payment)
def sync_order_payment_status(sender, instance: Payment, **kwargs):
    order = instance.order
    new_status = instance.status

    updated_fields = set()

    if getattr(order, "payment_status", None) != new_status:
        order.payment_status = new_status
        updated_fields.add("payment_status")

    # Decrement stock on first payment confirmation
    if new_status == PaymentStatus.CONFIRMED and not getattr(order, "paid_at", None):
        from django.db import transaction

        try:
            with transaction.atomic():
                for item in order.items.select_related("product").select_for_update():
                    product = item.product
                    if product.stock < item.quantity:
                        raise OrderOutOfStock(product, product.stock, item.quantity)
                # Decrement stock
                for item in order.items.select_related("product").select_for_update():
                    product = item.product
                    product.stock -= item.quantity
                    product.save(update_fields=["stock"])
        except OrderOutOfStock as e:
            # Mark order/payment as failed, set error message
            order.status = "cancelled"
            order.payment_status = PaymentStatus.ERROR
            order.save(update_fields=["status", "payment_status", "updated_at"])
            instance.status = PaymentStatus.ERROR
            instance.message = str(e)
            instance.save(update_fields=["status", "message", "modified"])
            return
        order.paid_at = timezone.now()
        updated_fields.add("paid_at")
        # Advance order status from pending -> processing on first payment confirmation
        if getattr(order, "status", None) == "pending":
            order.status = "processing"
            updated_fields.add("status")

    if updated_fields:
        updated_fields.add("updated_at")
        order.save(update_fields=list(updated_fields))
