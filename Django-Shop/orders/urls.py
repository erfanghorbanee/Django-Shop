from django.urls import path

from .views import (
    OrderListView,
    checkout_from_cart,
    payment_failed,
    payment_success,
    start_payment,
)

app_name = "orders"
urlpatterns = [
    path("", OrderListView.as_view(), name="order_list"),
    path("<int:order_id>/pay/", start_payment, name="start_payment"),
    path("<int:order_id>/payment/success/", payment_success, name="payment_success"),
    path("<int:order_id>/payment/failed/", payment_failed, name="payment_failed"),
    path("checkout/", checkout_from_cart, name="checkout"),
]
