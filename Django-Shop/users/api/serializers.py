from rest_framework import serializers

from users.models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "user", "product", "created_at"]
        read_only_fields = ["id", "user", "created_at"]
