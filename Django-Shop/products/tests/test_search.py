import pytest
from django.urls import reverse
from model_bakery import baker
from products.models import Category, Product

pytestmark = pytest.mark.django_db


def search_url(**params):
    url = reverse("products:index")
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{url}?{query}"
    return url


def test_search_by_name(client):
    product = baker.make(Product, name="UniqueProductName")
    baker.make(Product, name="OtherProduct")
    resp = client.get(search_url(q="UniqueProductName"))
    assert resp.status_code == 200
    assert b"UniqueProductName" in resp.content
    assert b"OtherProduct" not in resp.content


def test_search_by_description(client):
    product = baker.make(
        Product, name="DescProduct", description="Special description text"
    )
    baker.make(Product, name="OtherProduct", description="Irrelevant")
    resp = client.get(search_url(q="Special description"))
    assert resp.status_code == 200
    assert b"DescProduct" in resp.content
    assert b"OtherProduct" not in resp.content


def test_search_by_category_name(client):
    cat = baker.make(Category, name="Electronics")
    product = baker.make(Product, category=cat)
    baker.make(Product)
    resp = client.get(search_url(q="Electronics"))
    assert resp.status_code == 200
    assert b"Electronics" in resp.content


def test_search_case_insensitive(client):
    product = baker.make(Product, name="CaseTestProduct")
    resp = client.get(search_url(q="casetestproduct"))
    assert resp.status_code == 200
    assert b"CaseTestProduct" in resp.content


def test_search_partial_match(client):
    product = baker.make(Product, name="SuperWidget")
    resp = client.get(search_url(q="Widget"))
    assert resp.status_code == 200
    assert b"SuperWidget" in resp.content


def test_search_no_results(client):
    baker.make(Product, name="SomethingElse")
    resp = client.get(search_url(q="NoSuchProduct"))
    assert resp.status_code == 200
    assert b"No products found" in resp.content


def test_search_with_category_filter(client):
    cat = baker.make(Category, name="Books", slug="books")
    product = baker.make(Product, name="BookTitle", category=cat)
    other_cat = baker.make(Category, name="Toys", slug="toys")
    baker.make(Product, name="ToyTitle", category=other_cat)
    resp = client.get(search_url(q="BookTitle", category="books"))
    assert resp.status_code == 200
    assert b"BookTitle" in resp.content
    assert b"ToyTitle" not in resp.content
