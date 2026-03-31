def test_analytics_summary_returns_expected_keys(client, auth_headers):
    res = client.get("/api/analytics/summary", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_products" in data
    assert "by_source" in data
    assert "by_category" in data
    assert "avg_price_by_source" in data
    assert "avg_price_by_category" in data
    assert "price_changes_last_24h" in data
    assert "total_price_history_records" in data

def test_analytics_total_products_is_integer(client, auth_headers):
    res = client.get("/api/analytics/summary", headers=auth_headers)
    data = res.json()
    assert isinstance(data["total_products"], int)
    assert data["total_products"] >= 0
