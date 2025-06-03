from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "home/index.html"

class AboutView(TemplateView):
    template_name = "about/index.html"

class FAQView(TemplateView):
    template_name = "faq/index.html"

class PrivacyPolicyView(TemplateView):
    template_name = "privacy_policy/index.html"
