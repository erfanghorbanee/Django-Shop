from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class Cart(models.Model):
    """Persistent cart. Anonymous users temporarily use session key until login.

    When an anonymous user logs in, their session cart can be merged into their user cart.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=40, db_index=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["session_key"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                name="uniq_active_cart_per_user",
                condition=models.Q(user__isnull=False),
            )
        ]

    def __str__(self):
        owner = self.user.email if self.user else self.session_key
        return f"Cart<{owner}>"

    @property
    def items(self):  # qs alias for consistency
        return self.cart_items.select_related("product").prefetch_related(
            "product__images"
        )

    @property
    def total_quantity(self) -> int:
        return sum(item.quantity for item in self.items)

    @property
    def subtotal(self) -> Decimal:
        return sum(item.line_subtotal for item in self.items)

    @property
    def total(self) -> Decimal:  # hook for taxes / shipping later
        return self.subtotal

    @classmethod
    def get_or_create_for_request(cls, request):
        """Return a cart bound to user or session.

        - If user authenticated: ensure a user cart exists and merge session cart.
        - Else: use/create session cart identified by request.session.session_key.
        """
        if request.user.is_authenticated:
            cart, _ = cls.objects.get_or_create(user=request.user)
            # Merge any session cart
            session_key = request.session.session_key
            if session_key:
                try:
                    anon_cart = cls.objects.get(
                        session_key=session_key, user__isnull=True
                    )
                except cls.DoesNotExist:
                    return cart
                if anon_cart.pk != cart.pk:
                    cart.merge_from(anon_cart)
                    anon_cart.delete()
            return cart
        # anonymous path
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = cls.objects.get_or_create(session_key=session_key, user__isnull=True)
        return cart

    def merge_from(self, other: "Cart"):
        """Merge items from another cart into this cart (quantity additive)."""
        if other == self:
            return
        with transaction.atomic():
            for item in other.items:
                self.add(product=item.product, quantity=item.quantity, commit=False)
            self.save(update_fields=["updated_at"])

    def add(self, product, quantity=1, commit=True):
        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=self, product=product, defaults={"quantity": 0}
        )
        item.quantity += quantity
        if item.quantity <= 0:
            item.delete()
        else:
            item.save(update_fields=["quantity", "updated_at"])
        if commit:
            self.save(update_fields=["updated_at"])
        return item

    def set(self, product, quantity):
        if quantity <= 0:
            CartItem.objects.filter(cart=self, product=product).delete()
        else:
            CartItem.objects.update_or_create(
                cart=self,
                product=product,
                defaults={"quantity": quantity, "updated_at": timezone.now()},
            )
        self.save(update_fields=["updated_at"])

    def clear(self):
        self.items.all().delete()
        self.save(update_fields=["updated_at"])


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "product")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def unit_price(self):
        return self.product.discounted_price

    @property
    def line_subtotal(self):
        return self.unit_price * self.quantity
