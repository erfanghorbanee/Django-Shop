from django.urls import path

from .views import ProductDetailView, ProductListView, add_review, delete_review

app_name = "products"
urlpatterns = [
    path("", ProductListView.as_view(), name="index"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
    path("<slug:product_slug>/review/", add_review, name="add_review"),
    path("review/<int:review_id>/delete/", delete_review, name="delete_review"),
]
