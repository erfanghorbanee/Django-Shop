from decimal import Decimal

import pytest
from django.test import override_settings
from django.urls import reverse

from cart.exceptions import (
    MaxPerItemExceeded,
    OutOfStock,
    ProductUnavailable,
    QuantityNotPositive,
)
from cart.models import Cart, CartItem

# Use module-level django_db so individual tests don't need the decorator
pytestmark = pytest.mark.django_db


# --- Domain tests ---


def test_add_product_happy_path(cart, product_factory):
    p = product_factory(stock=10, price=Decimal("90.00"))
    item, info = cart.add_product(p, 5)
    assert item.quantity == 5
    assert info["added_quantity"] == 5 and info["final_quantity"] == 5
    assert cart.total_quantity == 5
    # unit pricing via discounted_price
    assert item.unit_price == p.discounted_price


def test_add_product_invalid_quantity_raises(cart, product_factory):
    p = product_factory()
    with pytest.raises(QuantityNotPositive):
        cart.add_product(p, 0)
    with pytest.raises(QuantityNotPositive):
        cart.add_product(p, -3)


def test_add_product_unavailable_or_out_of_stock(cart, product_factory):
    p1 = product_factory(is_available=False, stock=5)
    with pytest.raises(ProductUnavailable):
        cart.add_product(p1, 1)

    p2 = product_factory(stock=0)
    with pytest.raises(ProductUnavailable):
        cart.add_product(p2, 1)


def test_add_product_exceeds_stock_raises_but_keeps_existing(cart, product_factory):
    p = product_factory(stock=8)
    cart.add_product(p, 5)
    with pytest.raises(OutOfStock):
        cart.add_product(p, 6)
    # Still 5 in cart
    ci = CartItem.objects.get(cart=cart, product=p)
    assert ci.quantity == 5


@override_settings(CART_MAX_ITEM_QTY=5)
def test_add_product_exceeds_max_per_item(cart, product_factory):
    p = product_factory(stock=50)
    with pytest.raises(MaxPerItemExceeded):
        cart.add_product(p, 6)


def test_set_product_quantity_zero_removes(cart, product_factory):
    p = product_factory(stock=5)
    cart.add_product(p, 3)
    item, info = cart.set_product_quantity(p, 0)
    assert info.get("removed") is True
    assert not CartItem.objects.filter(cart=cart, product=p).exists()


def test_set_product_quantity_clamps_to_stock_and_max(cart, product_factory):
    p = product_factory(stock=8)
    # Request a very high quantity; should clamp to stock or max
    item, info = cart.set_product_quantity(p, 100)
    assert info["final_quantity"] == 8
    assert CartItem.objects.get(cart=cart, product=p).quantity == 8


def test_remove_product(cart, product_factory):
    p = product_factory(stock=3)
    cart.add_product(p, 2)
    resp = cart.remove_product(p)
    assert resp["removed"] is True
    assert not CartItem.objects.filter(cart=cart, product=p).exists()


def test_cart_item_pricing_properties(cart, product_factory):
    p = product_factory(price=Decimal("100.00"), discount_percent=Decimal("10"))
    cart.add_product(p, 2)
    item = CartItem.objects.get(cart=cart, product=p)
    assert item.unit_price == Decimal("90.0") or item.unit_price == Decimal("90.00")
    assert item.line_subtotal == item.unit_price * 2


# --- View tests (minimal) ---


def test_add_to_cart_ajax_returns_json(ajax, product_factory):
    p = product_factory(stock=10, price=Decimal("50.00"))
    url = reverse("cart:add", args=[p.id])
    r = ajax(url, {"quantity": 5})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "Added" in data["message"]
    assert data["total_quantity"] == 5
    assert Decimal(data["subtotal"]) == Decimal("250.00")


def test_add_to_cart_ajax_out_of_stock_returns_400(ajax, product_factory):
    p = product_factory(stock=3, price=Decimal("10.00"))
    url = reverse("cart:add", args=[p.id])
    # First add 3
    ajax(url, {"quantity": 3})
    # Then attempt +5 -> should fail
    r = ajax(url, {"quantity": 5})
    assert r.status_code == 400
    data = r.json()
    assert data["ok"] is False
    assert "Only" in data["message"]


def test_set_quantity_form_redirects_and_updates(client, product_factory):
    p = product_factory(stock=10, price=Decimal("10.00"))
    add_url = reverse("cart:add", args=[p.id])
    set_url = reverse("cart:set", args=[p.id])
    # Add 1 first (HTML form path)
    client.post(add_url, {"quantity": 1})
    # Update to 4 via non-AJAX
    r = client.post(set_url, {"quantity": 4})
    assert r.status_code in (302, 303)
    # Inspect cart by session key
    session_key = client.session.session_key
    cart = Cart.objects.get(session_key=session_key, user__isnull=True)
    item = cart.cart_items.get(product=p)
    assert item.quantity == 4


def test_remove_and_clear_redirect_and_effect(client, product_factory):
    p1 = product_factory(name="P1", stock=5, price=Decimal("10.00"))
    p2 = product_factory(name="P2", stock=5, price=Decimal("10.00"))
    add1 = reverse("cart:add", args=[p1.id])
    add2 = reverse("cart:add", args=[p2.id])
    client.post(add1, {"quantity": 2})
    client.post(add2, {"quantity": 3})

    # Remove p1
    remove_url = reverse("cart:remove", args=[p1.id])
    r1 = client.post(remove_url)
    assert r1.status_code in (302, 303)

    session_key = client.session.session_key
    cart = Cart.objects.get(session_key=session_key, user__isnull=True)
    assert not cart.cart_items.filter(product=p1).exists()
    assert cart.cart_items.filter(product=p2).exists()

    # Clear
    clear_url = reverse("cart:clear")
    r2 = client.post(clear_url)
    assert r2.status_code in (302, 303)
    cart.refresh_from_db()
    assert cart.cart_items.count() == 0


# --- Merge on login tests ---


def test_merge_session_cart_into_user_cart_on_login(client, user, product_factory):
    p1 = product_factory(name="M1", stock=10, price=Decimal("10.00"))
    p2 = product_factory(name="M2", stock=10, price=Decimal("20.00"))

    # Anonymous adds items to session cart
    client.post(reverse("cart:add", args=[p1.id]), {"quantity": 2})
    client.post(reverse("cart:add", args=[p2.id]), {"quantity": 3})

    session_key = client.session.session_key
    anon_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
    assert anon_cart.cart_items.count() == 2

    # Login without rotating the session key to preserve the anon session cart
    # (force_login/login may rotate the session; here we authenticate by setting session keys)
    session = client.session
    session["_auth_user_id"] = str(user.pk)
    session["_auth_user_backend"] = "django.contrib.auth.backends.ModelBackend"
    session["_auth_user_hash"] = user.get_session_auth_hash()
    session.save()
    # Hit cart page to trigger get_or_create_for_request merge logic
    r = client.get(reverse("cart:detail"))
    assert r.status_code == 200

    user_cart = Cart.objects.get(user=user)
    assert user_cart.cart_items.count() == 2
    assert user_cart.cart_items.get(product=p1).quantity == 2
    assert user_cart.cart_items.get(product=p2).quantity == 3

    # Anonymous cart should be deleted after merge
    assert not Cart.objects.filter(session_key=session_key, user__isnull=True).exists()


def test_merge_adds_quantities_when_user_cart_already_has_items(
    client, user, product_factory
):
    p = product_factory(stock=20, price=Decimal("15.00"))

    # Anonymous adds 3 of the product
    client.post(reverse("cart:add", args=[p.id]), {"quantity": 3})
    anon_session_key = client.session.session_key

    # Pre-create a user cart with 4 of the same product
    user_cart = Cart.objects.create(user=user)
    user_cart.add(product=p, quantity=4)

    # Login without rotating the session key to preserve the anon session cart
    session = client.session
    session["_auth_user_id"] = str(user.pk)
    session["_auth_user_backend"] = "django.contrib.auth.backends.ModelBackend"
    session["_auth_user_hash"] = user.get_session_auth_hash()
    session.save()
    # Trigger merge
    r = client.get(reverse("cart:detail"))
    assert r.status_code == 200

    user_cart.refresh_from_db()
    item = user_cart.cart_items.get(product=p)
    assert item.quantity == 7  # 4 existing + 3 from session cart

    # Anonymous cart should be gone
    assert not Cart.objects.filter(
        session_key=anon_session_key, user__isnull=True
    ).exists()


def test_merge_survives_session_rotation_on_login(client, user, product_factory):
    """Anon cart should merge even if session key rotates before login."""
    p1 = product_factory(name="R1", stock=10, price=Decimal("11.00"))
    p2 = product_factory(name="R2", stock=10, price=Decimal("22.00"))

    # Anonymous adds items to session cart
    client.post(reverse("cart:add", args=[p1.id]), {"quantity": 1})
    client.post(reverse("cart:add", args=[p2.id]), {"quantity": 2})

    session_key_before = client.session.session_key
    anon_cart = Cart.objects.get(session_key=session_key_before, user__isnull=True)
    # Our implementation stores a sticky cart_id in session
    assert client.session.get("cart_id") == anon_cart.pk

    # Perform a real login that rotates the session and preserves data
    user.set_password("testpass123")
    user.save()
    ok = client.login(email=user.email, password="testpass123")
    assert ok is True
    session_key_after = client.session.session_key
    assert session_key_after != session_key_before

    # Trigger merge
    r = client.get(reverse("cart:detail"))
    assert r.status_code == 200

    user_cart = Cart.objects.get(user=user)
    assert user_cart.cart_items.count() == 2
    assert user_cart.cart_items.get(product=p1).quantity == 1
    assert user_cart.cart_items.get(product=p2).quantity == 2
    # Old anon cart should be gone
    assert not Cart.objects.filter(pk=anon_cart.pk).exists()
