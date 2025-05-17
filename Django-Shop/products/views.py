from django.views.generic import ListView, DetailView
from .models import Product, Category
from django.core.paginator import EmptyPage
from django.shortcuts import get_object_or_404


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
    
    def get_context_data(self, **kwargs):
        """Provide enhanced context data for product detail."""
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get related products from the same category
        related_products = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id=product.id)[:4]
        
        # Add to context
        context['related_products'] = related_products
        
        # Get all categories for breadcrumb navigation
        context['categories'] = Category.objects.all()
        
        return context
