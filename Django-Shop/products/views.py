from django.shortcuts import render
from django.views.generic import ListView
from .models import Product

class ProductListView(ListView):
    model = Product
    template_name = "products/index.html"
    context_object_name = "products"
    paginate_by = 12  # Set number of products per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_paginated"] = self.paginate_by < self.get_queryset().count()
        return context
