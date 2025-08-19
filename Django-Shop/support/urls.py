from django.urls import path

from .views import SupportRequestView, support_success

app_name = 'support'
urlpatterns = [
    path('', SupportRequestView.as_view(), name='submit'),
    path('success/', support_success, name='success'),
] 