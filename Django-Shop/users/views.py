from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView, View

from .exceptions import CannotDeleteOnlyAddress
from .forms import AddressForm, ProfileForm
from .models import Address, Wishlist


class ProfileView(LoginRequiredMixin, View):
    template_name = "users/profile.html"

    def get(self, request):
        form = ProfileForm(instance=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("users:profile")
        return render(request, self.template_name, {"form": form})


class PrivacySettingsView(LoginRequiredMixin, View):
    template_name = "users/privacy_settings.html"

    def get(self, request):
        return render(request, self.template_name)


class TwoFactorAuthView(LoginRequiredMixin, View):
    template_name = "users/two_factor_auth.html"

    def get(self, request):
        return render(request, self.template_name)


class AddressesView(LoginRequiredMixin, ListView):
    model = Address
    template_name = "users/addresses.html"
    context_object_name = "addresses"

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddAddressView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = "users/add_address.html"
    form_class = AddressForm
    success_url = reverse_lazy("users:addresses")
    success_message = "Address added successfully!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class EditAddressView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "users/edit_address.html"
    pk_url_kwarg = "address_id"
    form_class = AddressForm
    success_url = reverse_lazy("users:addresses")
    success_message = "Address updated successfully!"

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


@method_decorator(require_POST, name="dispatch")
class DeleteAddressView(LoginRequiredMixin, View):
    def post(self, request, address_id):
        address = get_object_or_404(Address, pk=address_id, user=request.user)
        try:
            address.delete()
            messages.success(request, "Address deleted successfully.")
        except CannotDeleteOnlyAddress as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(request, "Could not delete address.")
        return redirect("users:addresses")


@method_decorator(require_POST, name="dispatch")
class SetPrimaryAddressView(LoginRequiredMixin, View):
    def post(self, request, address_id):
        address = get_object_or_404(Address, id=address_id, user=request.user)
        try:
            Address.switch_primary(request.user, address.pk)
            messages.success(request, "Primary address updated successfully!")
        except IntegrityError:
            # Handle rare race or DB constraint violation gracefully
            messages.error(
                request,
                "Could not set address as primary due to a conflict. Please try again.",
            )
        return redirect("users:addresses")


class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = "users/wishlist.html"
    context_object_name = "wishlist_items"

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


class RemoveFromWishlistView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        wishlist_item = get_object_or_404(Wishlist, id=item_id, user=request.user)
        wishlist_item.delete()
        messages.success(request, "Item removed from wishlist.")
        return redirect("users:wishlist")
