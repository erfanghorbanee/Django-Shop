from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse

from .exceptions import CannotDeleteOnlyAddress
from .models import Address, CustomUser, Wishlist


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user__email",
        "street_address",
        "city",
        "state",
        "country",
        "zip_code",
        "is_primary",
        "created_at",
    )
    list_filter = ("is_primary", "city", "country")
    search_fields = (
        "street_address",
        "city",
        "country",
        "state",
        "zip_code",
        "user__email",
    )

    def delete_view(self, request, object_id, extra_context=None):
        # Let Django render confirmation page on GET; only catch domain error on POST.
        if request.method == "POST":
            try:
                return super().delete_view(
                    request, object_id, extra_context=extra_context
                )
            except CannotDeleteOnlyAddress as e:
                self.message_user(request, str(e), level=messages.ERROR)
                change_url = reverse("admin:users_address_change", args=[object_id])
                return redirect(change_url)
        return super().delete_view(request, object_id, extra_context=extra_context)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "created_at")
    search_fields = ("user__email", "product__name")
