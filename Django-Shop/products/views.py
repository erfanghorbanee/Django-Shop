from django.views.generic import ListView, DetailView
from .models import Product
from django.core.paginator import EmptyPage


class ProductListView(ListView):
    model = Product
    template_name = "products/index.html"
    context_object_name = "products"
    paginate_by = 12  # Set number of products per page

    def get_context_data(self, **kwargs):
        """Provide context data including pagination info."""
        context = super().get_context_data(**kwargs)
        context["has_more"] = self.has_next_page(context['page_obj'])
        return context

    def has_next_page(self, page_obj):
        """
        Check if there is a next page available.
        
        Args:
            page_obj (Page): The current page object.
        
        Returns:
            bool: True if there is a next page, False otherwise.
        """
        try:
            return page_obj.has_next()
        except (AttributeError, EmptyPage):
            return False


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
