def test_missing_api_key_returns_401(client):
    res = client.get("/api/products")
    assert res.status_code == 401

def test_invalid_api_key_returns_401(client):
    res = client.get("/api/products", headers={"X-API-Key": "wrong-key"})
    assert res.status_code == 401

def test_valid_api_key_returns_200(client, auth_headers):
    res = client.get("/api/products", headers=auth_headers)
    assert res.status_code == 200
