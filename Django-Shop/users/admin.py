from django.contrib import admin

from .models import Address, CustomUser, Wishlist

admin.site.register(CustomUser)
admin.site.register(Address)
admin.site.register(Wishlist)
