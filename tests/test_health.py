def test_health_smoke(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
