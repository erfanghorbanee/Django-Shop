from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import EmptyPage
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from .models import Product, Category, Review


class ProductListView(ListView):
    model = Product
    template_name = "products/index.html"
    context_object_name = "products"
    paginate_by = 12  # Set number of products per page

    def get_queryset(self):
        """Return the queryset of products, filtered by category if specified."""
        queryset = super().get_queryset()
        
        # Get category from URL query parameter
        category_slug = self.request.GET.get('category')
        
        # Filter by category if provided
        if category_slug:
            # Find the category by slug
            category = get_object_or_404(Category, slug=category_slug)
            
            if category.is_parent:
                # If it's a parent category, include products from all its subcategories
                subcategory_ids = category.children.filter(is_active=True).values_list('id', flat=True)
                queryset = queryset.filter(
                    Q(category=category) | Q(category_id__in=subcategory_ids)
                )
            else:
                # If it's a subcategory, just show products from that subcategory
                queryset = queryset.filter(category=category)
            
        return queryset

    def get_context_data(self, **kwargs):
        """Provide context data including pagination info."""
        context = super().get_context_data(**kwargs)
        context["has_more"] = self.has_next_page(context['page_obj'])
        
        # Add current category to context if filtering by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)
            
            # If this is a parent category, get its subcategories
            if context['current_category'].is_parent:
                context['subcategories'] = context['current_category'].children.filter(is_active=True)
            # If this is a subcategory, get its parent
            elif context['current_category'].parent:
                context['parent_category'] = context['current_category'].parent
                context['sibling_categories'] = context['current_category'].parent.children.filter(is_active=True).exclude(
                    id=context['current_category'].id
                )
            
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
        
        # Add category information for breadcrumbs
        context['category'] = product.category
        if product.category.parent:
            context['parent_category'] = product.category.parent
            
        # Get product reviews with pagination
        reviews = product.reviews.all().select_related('user')
        context['reviews'] = reviews
        context['review_count'] = reviews.count()
        
        # Check if current user has already reviewed this product
        if self.request.user.is_authenticated:
            context['user_review'] = product.reviews.filter(user=self.request.user).first()
        
        return context


@login_required
@require_POST
def add_review(request, product_slug):
    """Add a review to a product or update existing review"""
    product = get_object_or_404(Product, slug=product_slug)
    rating = int(request.POST.get('rating', 0))
    comment = request.POST.get('comment', '').strip()
    
    if not (1 <= rating <= 5) or not comment:
        messages.error(request, 'Please provide a rating (1-5) and a comment.')
        return redirect('products:product_detail', slug=product_slug)
    
    # Check if user already reviewed this product
    review, created = Review.objects.update_or_create(
        user=request.user,
        product=product,
        defaults={
            'rating': rating,
            'comment': comment
        }
    )
    
    if created:
        messages.success(request, 'Thank you for your review!')
    else:
        messages.success(request, 'Your review has been updated.')
        
    return redirect('products:product_detail', slug=product_slug)


@login_required
def delete_review(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, id=review_id)
    
    # Check if the user is the owner of the review
    if review.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this review")
    
    product_slug = review.product.slug
    review.delete()
    messages.success(request, 'Your review has been deleted.')
    
    return redirect('products:product_detail', slug=product_slug)
