# tests/test_artifact_route.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_head_and_get_artifact(hydrated_project_with_artifact):
    pid = hydrated_project_with_artifact.id

    r = client.head(f"/api/projects/{pid}/artifact")
    assert r.status_code == 200
    assert r.headers.get("content-type") == "application/zip"
    assert r.headers.get("etag")
    assert r.headers.get("last-modified")
    assert r.text == ""  # HEAD sin cuerpo

    r = client.get(f"/api/projects/{pid}/artifact")
    assert r.status_code == 200
    size = int(r.headers["content-length"])
    assert len(r.content) == size
