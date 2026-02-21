from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_list_hospitals_shape():
    # If DB is empty, this still validates response shape.
    r = client.get("/hospitals?limit=10&offset=0")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data and "limit" in data and "offset" in data and "total" in data

def test_stats_shape():
    r = client.get("/stats/ratings")
    assert r.status_code == 200
    data = r.json()
    assert "total_hospitals" in data
    assert "rating_counts" in data