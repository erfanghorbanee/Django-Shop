from django.urls import path

from .views import (
    OrderListView,
    PaymentMethodCreateView,
    PaymentMethodDeleteView,
    PaymentMethodListView,
    SetDefaultPaymentMethodView,
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
    path("payment-methods/", PaymentMethodListView.as_view(), name="payment_methods"),
    path(
        "payment-methods/add/",
        PaymentMethodCreateView.as_view(),
        name="add_payment_method",
    ),
    path(
        "payment-methods/<int:pk>/delete/",
        PaymentMethodDeleteView.as_view(),
        name="delete_payment_method",
    ),
    path(
        "payment-methods/<int:pk>/set-default/",
        SetDefaultPaymentMethodView.as_view(),
        name="set_default_payment_method",
    ),
]
