from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, View

from products.models import Product

from .exceptions import CartError
from .models import Cart


class CartDetailView(TemplateView):
    template_name = "cart/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cart"] = Cart.get_or_create_for_request(self.request)
        return ctx


@method_decorator(require_POST, name="dispatch")
class CartActionMixin(View):
    """Shared logic for cart-mutating POST views."""

    def dispatch(self, request, *args, **kwargs):
        self.cart = Cart.get_or_create_for_request(request)
        return super().dispatch(request, *args, **kwargs)

    def respond(self, message, *, ok=True):
        """Return JSON for AJAX requests, or HTML redirect for POST requests."""

        # Check if the request wants JSON (AJAX detected via X-Requested-With)
        wants_json = (
            self.request.headers.get("X-Requested-With", "").lower() == "xmlhttprequest"
        )
        if wants_json:
            return JsonResponse(
                {
                    "ok": ok,
                    "message": message,
                    "total_quantity": self.cart.total_quantity,
                    "subtotal": str(self.cart.subtotal),
                },
                status=400 if not ok else 200,
            )

        if ok:
            messages.success(self.request, message)
        else:
            messages.error(self.request, message)
        return redirect("cart:detail")


class AddToCartView(CartActionMixin):
    def post(self, request, product_id):
        product = get_object_or_404(
            Product.objects.select_related("category"), pk=product_id
        )

        try:
            quantity = self.cart._parse_quantity(request.POST.get("quantity", 1))
            item, info = self.cart.add_product(product, quantity)
            message = f"Added {info['added_quantity']} × {product.name} to cart."
            return self.respond(message)
        except CartError as e:
            return self.respond(str(e), ok=False)


class RemoveFromCartView(CartActionMixin):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        self.cart.remove_product(product)
        return self.respond(f"Removed {product.name} from cart")


class SetQuantityView(CartActionMixin):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)

        try:
            quantity = self.cart._parse_quantity(
                request.POST.get("quantity", 0), default=0
            )
            item, info = self.cart.set_product_quantity(product, quantity)
            if info.get("removed"):
                message = f"Removed {product.name} from cart"
            else:
                message = f"Updated {product.name} quantity"
            return self.respond(message)
        except CartError as e:
            return self.respond(str(e), ok=False)


class ClearCartView(CartActionMixin):
    def post(self, request):
        self.cart.clear()
        return self.respond("Cart cleared")
