from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "home/index.html"

class AboutView(TemplateView):
    template_name = "home/about/index.html"

class FAQView(TemplateView):
    template_name = "home/faq/index.html"

class PrivacyPolicyView(TemplateView):
    template_name = "home/privacy_policy/index.html"
