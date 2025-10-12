import uuid

def test_projects_crud_extended(client):
    # create
    name = f"demo-{uuid.uuid4().hex[:8]}"
    r = client.post("/api/projects/", json={"name": name})
    assert r.status_code == 201, r.text
    created = r.json()
    pid = created["id"]

    # get/{id}
    r = client.get(f"/api/projects/{pid}")
    assert r.status_code == 200
    assert r.json()["name"] == name

    # put/{id}
    new_name = name + "-updated"
    r = client.put(f"/api/projects/{pid}", json={"name": new_name})
    assert r.status_code == 200
    assert r.json()["name"] == new_name

    # list (should contain updated)
    r = client.get("/api/projects/")
    assert r.status_code == 200
    assert any(it["id"] == pid and it["name"] == new_name for it in r.json())

    # delete/{id}
    r = client.delete(f"/api/projects/{pid}")
    assert r.status_code == 204

    # get after delete -> 404
    r = client.get(f"/api/projects/{pid}")
    assert r.status_code == 404
