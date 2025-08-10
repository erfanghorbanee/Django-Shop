import pytest
from django.db import transaction

from users.exceptions import CannotDeleteOnlyAddress, CannotDemoteOnlyPrimary
from users.models import Address


def make_address(user, **overrides):
    base = dict(
        user=user,
        street_address="123 A St",
        apartment_address="",
        city="City",
        state="State",
        zip_code="12345",
        country="Country",
    )
    base.update(overrides)
    return Address.objects.create(**base)


def test_first_address_auto_primary(user):
    a1 = make_address(user)
    """First created address should automatically be primary."""
    assert a1.is_primary, "First address should automatically be primary"


def test_second_address_non_primary_then_promote(user):
    a1 = make_address(user)
    a2 = make_address(user, is_primary=False)
    # Use model method to switch primary explicitly
    Address.switch_primary(user, a2.pk)
    a1.refresh_from_db()
    a2.refresh_from_db()
    assert a2.is_primary, "Second address should be primary after promotion"
    assert not a1.is_primary, "Original primary should have been demoted"


def test_demote_primary_with_other_address_auto_promotes_other(user):
    """Switching primary explicitly moves primary flag to another address."""
    a1 = make_address(user)  # initial primary
    a2 = make_address(user, is_primary=False)
    Address.switch_primary(user, a2.pk)
    a1.refresh_from_db()
    a2.refresh_from_db()
    assert not a1.is_primary, "Original primary should have been demoted"
    assert a2.is_primary, "New address should now be primary"
    assert Address.objects.filter(user=user, is_primary=True).count() == 1


def test_cannot_demote_primary_when_only_address(user):
    """Attempting to demote the only address should raise domain exception."""
    a1 = make_address(user)
    a1.is_primary = False
    with pytest.raises(CannotDemoteOnlyPrimary):
        a1.save()
    a1.refresh_from_db()
    assert a1.is_primary, "Single address must remain primary"


def test_delete_only_address_blocked(user):
    """Deleting the only address must be blocked with domain exception."""
    a1 = make_address(user)
    with pytest.raises(CannotDeleteOnlyAddress):
        with transaction.atomic():
            a1.delete()
    assert Address.objects.filter(user=user).count() == 1, (
        "Only address should not have been deleted"
    )


def test_delete_primary_with_other_promotes_new_primary(user):
    """Deleting current primary should promote remaining address to primary."""
    a1 = make_address(user)
    a2 = make_address(user, is_primary=False)
    a1.delete()
    a2.refresh_from_db()
    assert a2.is_primary, "Remaining address should become primary after deletion"


def test_unique_primary_constraint_enforced(user):
    """Creating a second primary should demote the first ensuring uniqueness."""
    a1 = make_address(user)
    a2 = make_address(user, is_primary=True)
    a1.refresh_from_db()
    a2.refresh_from_db()
    assert a2.is_primary, "Newly created address marked primary should be primary"
    assert not a1.is_primary, "Original primary must be demoted automatically"
    assert Address.objects.filter(user=user, is_primary=True).count() == 1, (
        "There must be exactly one primary address"
    )
