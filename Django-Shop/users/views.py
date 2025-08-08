from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View

from .forms import ProfileForm
from .models import Address, Wishlist

# Create your views here.


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


class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = "users/wishlist.html"
    context_object_name = "wishlist_items"

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


class AddressesView(LoginRequiredMixin, ListView):
    model = Address
    template_name = "users/addresses.html"
    context_object_name = "addresses"

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddAddressView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Address
    template_name = "users/add_address.html"
    fields = [
        "street_address",
        "apartment_address",
        "city",
        "state",
        "zip_code",
        "country",
        "is_primary",
    ]
    success_url = reverse_lazy("users:addresses")
    success_message = "Address added successfully!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class EditAddressView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Address
    template_name = "users/edit_address.html"
    pk_url_kwarg = "address_id"
    fields = [
        "street_address",
        "apartment_address",
        "city",
        "state",
        "zip_code",
        "country",
        "is_primary",
    ]
    success_url = reverse_lazy("users:addresses")
    success_message = "Address updated successfully!"

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


@method_decorator(require_POST, name="dispatch")
class DeleteAddressView(LoginRequiredMixin, DeleteView):
    model = Address
    success_url = reverse_lazy("users:addresses")
    pk_url_kwarg = "address_id"

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Address deleted successfully!")
        return response


@method_decorator(require_POST, name="dispatch")
class SetPrimaryAddressView(LoginRequiredMixin, View):
    def post(self, request, address_id):
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.is_primary = True  # model save() will demote others
        address.save()
        messages.success(request, "Primary address updated successfully!")
        return redirect("users:addresses")


class RemoveFromWishlistView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        wishlist_item = get_object_or_404(Wishlist, id=item_id, user=request.user)
        wishlist_item.delete()
        messages.success(request, "Item removed from wishlist.")
        return redirect("users:wishlist")
