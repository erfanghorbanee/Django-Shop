from .models import Cart


def cart_summary(request):
    try:
        cart = Cart.get_or_create_for_request(request)
        return {
            "cart_total_quantity": cart.total_quantity,
            "cart_subtotal": cart.subtotal,
        }
    except Exception:
        return {"cart_total_quantity": 0, "cart_subtotal": 0}
