from uuid import uuid4

import pytest
from cart.models import Cart
from django.contrib.auth import get_user_model
from model_bakery import baker
from products.models import Category, Product

User = get_user_model()


@pytest.fixture
def user(db):
    return baker.make(
        User,
        email="u@example.com",
        phone="+15550000001",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def category(db) -> Category:
    """A basic category."""
    return baker.make(Category)


@pytest.fixture
def product(db, category: Category) -> Product:
    """An available in-stock product."""
    return baker.make(Product, category=category, stock=10, is_available=True)


@pytest.fixture
def cart(db) -> Cart:
    """A session-bound cart."""
    return baker.make(Cart, session_key=f"sk-{uuid4().hex[:8]}")


@pytest.fixture
def product_factory(db, category: Category):
    """Factory function to create products with sensible defaults."""

    def _make(**overrides) -> Product:
        defaults = dict(category=category, stock=10, is_available=True)
        defaults.update(overrides)
        return baker.make(Product, **defaults)

    return _make


@pytest.fixture
def ajax(client):
    """Helper to POST as AJAX with JSON-acceptable headers."""

    def _post(url, data=None, **extra):
        headers = {
            "HTTP_X_REQUESTED_WITH": "XMLHttpRequest",
            "HTTP_ACCEPT": "application/json",
        }
        headers.update(extra)
        return client.post(url, data or {}, **headers)

    return _post
