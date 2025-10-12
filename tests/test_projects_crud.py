def test_projects_crud(client):
    r = client.post("/api/projects/", json={"name":"demo"})
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "demo"
    assert "id" in data

    r = client.get("/api/projects/")
    assert r.status_code == 200
    items = r.json()
    assert any(it["name"] == "demo" for it in items)
