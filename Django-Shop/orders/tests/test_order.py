import pytest
from model_bakery import baker
from payments import PaymentStatus

from orders.models import Order, Payment

pytestmark = pytest.mark.django_db


def test_stock_decrements_on_payment_confirmation(user, product_factory):
    "Test that product stock is decremented when payment is confirmed."

    product = product_factory(stock=10)
    order = baker.make(Order, user=user, total_amount=100)
    order_item = order.items.create(product=product, quantity=2, price=product.price)
    initial_stock = product.stock
    payment = baker.make(Payment, order=order, status=PaymentStatus.WAITING)

    # Act: confirm the payment (simulate webhook or admin action)
    payment.status = PaymentStatus.CONFIRMED
    payment.save()
    product.refresh_from_db()

    # Assert: stock is decremented by order item quantity
    assert product.stock == initial_stock - order_item.quantity
