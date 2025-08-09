from django.contrib.auth import get_user_model
from django.test import TestCase
from users.exceptions import (
    CannotDeleteOnlyAddress,
    CannotDemoteOnlyPrimary,
)
from users.models import Address

User = get_user_model()


class AddressInvariantTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="edge@example.com",
            password="testpass123",
            first_name="Edge",
            last_name="Case",
            phone="+1111111111",
        )

    def create_address(self, **kwargs):
        base = dict(
            user=self.user,
            street_address="123 A St",
            apartment_address="",
            city="City",
            state="State",
            zip_code="12345",
            country="Country",
        )
        base.update(kwargs)
        return Address.objects.create(**base)

    def test_first_address_auto_primary(self):
        """First address created should be primary by default."""

        a1 = self.create_address()
        self.assertTrue(a1.is_primary, "First address should auto-be primary")

    def test_second_address_non_primary_then_promote(self):
        a1 = self.create_address()
        a2 = self.create_address(is_primary=False)
        a2.is_primary = True
        a2.save()
        a1.refresh_from_db()
        a2.refresh_from_db()
        self.assertTrue(a2.is_primary, "Second address should be primary")
        self.assertFalse(a1.is_primary, "First address should no longer be primary")

    def test_demote_primary_with_other_address_auto_promotes_other(self):
        """Demoting primary address should promote another address if it exists."""

        a1 = self.create_address()  # primary
        a2 = self.create_address(is_primary=False)
        a1.is_primary = False
        a1.save()
        a1.refresh_from_db()
        a2.refresh_from_db()
        self.assertFalse(a1.is_primary)
        self.assertTrue(
            a2.is_primary,
            "Other address should be promoted when demoting current primary",
        )
        self.assertEqual(
            1,
            Address.objects.filter(user=self.user, is_primary=True).count(),
            "There should be exactly one primary address.",
        )

    def test_cannot_demote_primary_when_only_address(self):
        """Cannot demote primary address when it is the only address."""

        a1 = self.create_address()
        a1.is_primary = False

        # Attempting to demote primary when it is the only address should raise an error.
        with self.assertRaises(CannotDemoteOnlyPrimary):
            a1.save()
        a1.refresh_from_db()
        self.assertTrue(a1.is_primary, "Address should remain primary.")

    def test_delete_only_address_blocked(self):
        """Cannot delete the only address of a user."""

        a1 = self.create_address()
        with self.assertRaises(CannotDeleteOnlyAddress):
            a1.delete()
        self.assertEqual(
            1,
            Address.objects.filter(user=self.user).count(),
            "Address should not be deleted.",
        )

    def test_delete_primary_with_other_promotes_new_primary(self):
        """Deleting primary address with another should promote the other to primary."""

        a1 = self.create_address()
        a2 = self.create_address(is_primary=False)
        a1.delete()
        a2.refresh_from_db()
        self.assertTrue(a2.is_primary, "Second address should be primary")

    def test_unique_primary_constraint_enforced(self):
        """Ensure only one primary address exists per user."""

        a1 = self.create_address()
        a2 = self.create_address(is_primary=True)
        a1.refresh_from_db()
        a2.refresh_from_db()
        self.assertTrue(a2.is_primary, "Second address should be primary")
        self.assertFalse(a1.is_primary, "First address should no longer be primary")
        self.assertEqual(
            1,
            Address.objects.filter(user=self.user, is_primary=True).count(),
            "There should be exactly one primary address.",
        )
