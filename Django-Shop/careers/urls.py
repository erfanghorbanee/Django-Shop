from django.urls import path
from .views import CareerApplicationView, career_success

app_name = 'careers'

urlpatterns = [
    path('apply/', CareerApplicationView.as_view(), name='apply'),
    path('success/', career_success, name='success'),
] 