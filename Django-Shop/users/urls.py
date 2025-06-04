from django.urls import path
from .views import (
    ProfileView,
    PrivacySettingsView,
    TwoFactorAuthView,
    WishlistView,
    AddressesView,
    AddAddressView,
    EditAddressView,
    DeleteAddressView,
    SetPrimaryAddressView,
    RemoveFromWishlistView,
)
from users.api.views import WishlistToggleAPIView

app_name = 'users'
urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('privacy-settings/', PrivacySettingsView.as_view(), name='privacy_settings'),
    path('two-factor-auth/', TwoFactorAuthView.as_view(), name='two_factor_auth'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('addresses/', AddressesView.as_view(), name='addresses'),
    path('addresses/add/', AddAddressView.as_view(), name='add_address'),
    path('addresses/edit/<int:address_id>/', EditAddressView.as_view(), name='edit_address'),
    path('addresses/delete/<int:address_id>/', DeleteAddressView.as_view(), name='delete_address'),
    path('addresses/set-primary/<int:address_id>/', SetPrimaryAddressView.as_view(), name='set_primary_address'),
    path('api/v1/wishlist/toggle/', WishlistToggleAPIView.as_view(), name='api_wishlist_toggle'),
    path('wishlist/remove/<int:item_id>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
] 