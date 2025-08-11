"""Cart domain exceptions."""


class CartError(Exception):
    """Base exception for cart domain errors."""

    pass


class ProductUnavailable(CartError):
    """Product is not available for purchase."""

    pass


class OutOfStock(CartError):
    """Requested quantity exceeds available stock."""

    pass


class MaxPerItemExceeded(CartError):
    """Requested quantity exceeds per-item maximum limit."""

    pass


class QuantityNotPositive(CartError):
    """Quantity must be positive for add operations."""

    pass
