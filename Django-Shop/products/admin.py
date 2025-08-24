from django.contrib import admin

from .models import Category, Product, ProductImage, Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Allows uploading multiple images
    min_num = 1  # At least one image is required
    verbose_name = "Product Image"
    verbose_name_plural = "Product Images"


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ("user", "rating", "comment", "created_at")
    can_delete = True
    max_num = 0  # Don't allow adding reviews in admin
    verbose_name = "Product Review"
    verbose_name_plural = "Product Reviews"


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "discount_percent",
        "discounted_price_display",
        "stock",
        "is_available",
        "avg_rating_display",
        "created_at",
    )
    list_filter = ("category", "is_available")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ReviewInline]
    ordering = ["-created_at", "name"]

    def discounted_price_display(self, obj):
        if obj.has_discount:
            return f"${obj.discounted_price:.2f} (${obj.price:.2f})"
        return f"${obj.price:.2f}"

    discounted_price_display.short_description = "Price"

    def avg_rating_display(self, obj):
        avg = obj.average_rating
        if avg > 0:
            return f"{avg:.1f}/5.0 ({obj.reviews.count()} reviews)"
        return "No ratings"

    avg_rating_display.short_description = "Rating"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active", "slug")
    list_filter = ("is_active", "parent")
    prepopulated_fields = {"slug": ("name",)}


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "comment_preview", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__name", "user__email", "comment")
    readonly_fields = ("created_at", "updated_at")

    def comment_preview(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment

    comment_preview.short_description = "Comment"


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)
