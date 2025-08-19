from django.urls import path

from .views import AboutView, FAQView, HomePageView, PrivacyPolicyView

app_name = 'home'
urlpatterns = [
    path('', HomePageView.as_view(), name='index'),
    path('about/', AboutView.as_view(), name='about'),
    path('faq/', FAQView.as_view(), name='faq'),
    path('privacy/', PrivacyPolicyView.as_view(), name='privacy'),
]