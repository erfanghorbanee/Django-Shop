import re

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_set_language_sets_cookie(client):
    # Post to set_language to switch to Italian
    url = reverse("set_language")
    response = client.post(url, {"language": "it", "next": "/"}, follow=False)
    # Django sets a session or language cookie; check for response cookies
    cookie_keys = list(response.cookies.keys())
    assert any(k.lower().startswith("django_language") for k in cookie_keys) or any(
        k.lower().startswith("sessionid") for k in cookie_keys
    )


@pytest.mark.django_db
def test_translated_navbar_renders_in_german(client):
    # Switch to German, then load home page and expect German word for Categories
    client.post(reverse("set_language"), {"language": "de", "next": "/"})
    resp = client.get(reverse("home:index"))
    content = resp.content.decode()
    # Check for 'Kategorien' or the German translation of 'Categories'
    assert re.search(r"Kategorien", content)
