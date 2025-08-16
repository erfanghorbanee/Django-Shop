from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from payments import PaymentStatus

from .models import Payment


@receiver(post_save, sender=Payment)
def sync_order_payment_status(sender, instance: Payment, **kwargs):
    order = instance.order
    new_status = instance.status

    updated_fields = set()

    if getattr(order, "payment_status", None) != new_status:
        order.payment_status = new_status
        updated_fields.add("payment_status")

    if new_status == PaymentStatus.CONFIRMED and not getattr(order, "paid_at", None):
        order.paid_at = timezone.now()
        updated_fields.add("paid_at")
        # Advance order status from pending -> processing on first payment confirmation
        if getattr(order, "status", None) == "pending":
            order.status = "processing"
            updated_fields.add("status")

    if updated_fields:
        updated_fields.add("updated_at")
        order.save(update_fields=list(updated_fields))
