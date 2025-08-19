class OrderOutOfStock(Exception):
    """Raised when there is not enough stock to fulfill an order at payment confirmation."""

    def __init__(self, product, available, requested):
        self.product = product
        self.available = available
        self.requested = requested
        super().__init__(
            f"Insufficient stock for {product.name}: {available} left, {requested} requested."
        )
