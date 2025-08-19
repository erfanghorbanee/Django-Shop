from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product
from users.models import Wishlist

from .serializers import WishlistSerializer


class WishlistToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'Product ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
        if wishlist_item:
            wishlist_item.delete()
            return Response({'status': 'removed'})
        else:
            wishlist_item = Wishlist.objects.create(user=request.user, product=product)
            serializer = WishlistSerializer(wishlist_item)
            return Response({'status': 'added', 'item': serializer.data})