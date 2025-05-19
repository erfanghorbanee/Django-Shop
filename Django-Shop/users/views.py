from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from .models import CustomUser, Address, Wishlist

# Create your views here.

class ProfileView(LoginRequiredMixin, View):
    template_name = 'users/profile.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.gender = request.POST.get('gender', user.gender)
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('users:profile')

class PrivacySettingsView(LoginRequiredMixin, View):
    template_name = 'users/privacy_settings.html'

    def get(self, request):
        return render(request, self.template_name)

class TwoFactorAuthView(LoginRequiredMixin, View):
    template_name = 'users/two_factor_auth.html'

    def get(self, request):
        return render(request, self.template_name)

class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'users/wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

@method_decorator(require_POST, name='dispatch')
class RemoveFromWishlistView(LoginRequiredMixin, DeleteView):
    model = Wishlist
    success_url = reverse_lazy('users:wishlist')

    def get_object(self, queryset=None):
        return get_object_or_404(Wishlist, id=self.kwargs['item_id'], user=self.request.user)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Item removed from wishlist.')
        return response

class AddressesView(LoginRequiredMixin, ListView):
    model = Address
    template_name = 'users/addresses.html'
    context_object_name = 'addresses'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class AddAddressView(LoginRequiredMixin, CreateView):
    model = Address
    template_name = 'users/add_address.html'
    fields = ['street_address', 'apartment_address', 'city', 'state', 'zip_code', 'country', 'is_primary']
    success_url = reverse_lazy('users:addresses')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        if form.instance.is_primary:
            Address.objects.filter(user=self.request.user).exclude(id=form.instance.id).update(is_primary=False)
        
        messages.success(self.request, 'Address added successfully!')
        return response

class EditAddressView(LoginRequiredMixin, UpdateView):
    model = Address
    template_name = 'users/edit_address.html'
    fields = ['street_address', 'apartment_address', 'city', 'state', 'zip_code', 'country', 'is_primary']
    success_url = reverse_lazy('users:addresses')

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        
        if form.instance.is_primary:
            Address.objects.filter(user=self.request.user).exclude(id=form.instance.id).update(is_primary=False)
        
        messages.success(self.request, 'Address updated successfully!')
        return response

@method_decorator(require_POST, name='dispatch')
class DeleteAddressView(LoginRequiredMixin, DeleteView):
    model = Address
    success_url = reverse_lazy('users:addresses')

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Address deleted successfully!')
        return response

@method_decorator(require_POST, name='dispatch')
class SetPrimaryAddressView(LoginRequiredMixin, View):
    def post(self, request, address_id):
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        # Set all addresses as non-primary
        Address.objects.filter(user=request.user).update(is_primary=False)
        
        # Set the selected address as primary
        address.is_primary = True
        address.save()
        
        messages.success(request, 'Primary address updated successfully!')
        return redirect('users:addresses')
