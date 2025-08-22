from django.core.cache import cache
from django.db.models import Sum
from django.views.generic import TemplateView
from orders.models import OrderItem
from products.models import Product


class HomePageView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Special Discounts: cache for 10 minutes
        special_discounts = cache.get("special_discounts")
        if special_discounts is None:
            special_discounts = list(
                Product.objects.filter(
                    is_available=True, discount_percent__gt=0
                ).order_by("-discount_percent", "-updated_at")[:8]
            )
            cache.set("special_discounts", special_discounts, 600)
        context["special_discounts"] = special_discounts

        # Most Bought Products: cache for 10 minutes
        most_bought_products = cache.get("most_bought_products")
        if most_bought_products is None:
            most_bought = (
                OrderItem.objects.values("product")
                .annotate(total_sold=Sum("quantity"))
                .order_by("-total_sold")[:8]
            )
            ids = [x["product"] for x in most_bought]
            product_map = Product.objects.in_bulk(ids)
            most_bought_products = [
                product_map[pid] for pid in ids if pid in product_map
            ]
            cache.set("most_bought_products", most_bought_products, 600)
        context["most_bought_products"] = most_bought_products

        return context


class AboutView(TemplateView):
    template_name = "home/about/index.html"


class FAQView(TemplateView):
    template_name = "home/faq/index.html"


class PrivacyPolicyView(TemplateView):
    template_name = "home/privacy_policy/index.html"
