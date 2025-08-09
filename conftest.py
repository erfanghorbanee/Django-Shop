import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker

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
