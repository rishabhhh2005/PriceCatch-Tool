def test_list_products_returns_paginated_structure(client, auth_headers):
    res = client.get("/api/products", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data

def test_filter_products_by_source(client, auth_headers):
    res = client.get("/api/products?source=grailed", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert item["source"] == "grailed"

def test_filter_products_by_price_range(client, auth_headers):
    res = client.get("/api/products?min_price=100&max_price=500", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert 100 <= item["current_price"] <= 500

def test_get_product_not_found_returns_404(client, auth_headers):
    res = client.get("/api/products/99999", headers=auth_headers)
    assert res.status_code == 404
