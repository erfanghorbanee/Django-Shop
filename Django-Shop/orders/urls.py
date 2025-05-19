from django.urls import path
from .views import (
    OrderListView,
    PaymentMethodListView,
    PaymentMethodCreateView,
    PaymentMethodDeleteView,
    SetDefaultPaymentMethodView,
)

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('payment-methods/', PaymentMethodListView.as_view(), name='payment_methods'),
    path('payment-methods/add/', PaymentMethodCreateView.as_view(), name='add_payment_method'),
    path('payment-methods/<int:pk>/delete/', PaymentMethodDeleteView.as_view(), name='delete_payment_method'),
    path('payment-methods/<int:pk>/set-default/', SetDefaultPaymentMethodView.as_view(), name='set_default_payment_method'),
] 