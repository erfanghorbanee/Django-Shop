from django.contrib import messages
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, View
from products.models import Product

from .models import Cart


class CartDetailView(TemplateView):
    template_name = "cart/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cart"] = Cart.get_or_create_for_request(self.request)
        return ctx


class CartActionMixin(View):
    """Shared logic for cart-mutating POST views."""

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() != "post":
            return HttpResponseNotAllowed(["POST"])
        self.cart = Cart.get_or_create_for_request(request)
        return super().dispatch(request, *args, **kwargs)

    def respond(self, message):
        request = self.request
        cart = self.cart
        # Detect AJAX/JSON intent. HttpRequest has no 'accepts' method; use headers.
        accept = request.headers.get("Accept", "")
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
        wants_json = "application/json" in accept or "json" in accept
        if request.headers.get("HX-Request") or is_ajax or wants_json:
            return JsonResponse(
                {
                    "ok": True,
                    "message": message,
                    "total_quantity": cart.total_quantity,
                    "subtotal": str(cart.subtotal),
                }
            )
        messages.success(request, message)
        return redirect("cart:detail")


class AddToCartView(CartActionMixin):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        try:
            qty = int(request.POST.get("quantity", 1))
        except ValueError:
            qty = 1
        self.cart.add(product, quantity=max(1, qty))
        return self.respond(f"Added {product.name} to cart")


class RemoveFromCartView(CartActionMixin):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        self.cart.set(product, 0)
        return self.respond(f"Removed {product.name} from cart")


class SetQuantityView(CartActionMixin):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        try:
            qty = int(request.POST.get("quantity", 1))
        except ValueError:
            qty = 1
        self.cart.set(product, max(0, qty))
        return self.respond(f"Updated {product.name} quantity")


class ClearCartView(CartActionMixin):
    def post(self, request):
        self.cart.clear()
        return self.respond("Cart cleared")
