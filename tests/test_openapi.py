def test_openapi_has_health_path(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    data = r.json()
    assert "paths" in data
    assert "/api/health" in data["paths"]
