"""
Integration Test Suite - API & Service Health Gates
Candidate: Sai Nayan Mamilla (sainayanmamilla)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app, DB_STORE

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_database():
    """Ensure in-memory DB is clean before each integration test."""
    DB_STORE.clear()
    yield
    DB_STORE.clear()

def test_healthz_endpoint():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["version"] == "2.0.0"

def test_readyz_endpoint():
    response = client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True

def test_create_and_retrieve_item_lifecycle():
    payload = {
        "item_id": "ITM-9001",
        "name": "Cloud Enterprise Router",
        "quantity": 15,
        "unit_price": 450.00
    }
    # Step 1: Create Item
    create_res = client.post("/api/v1/items", json=payload)
    assert create_res.status_code == 201
    assert create_res.json()["item"]["item_id"] == "ITM-9001"

    # Step 2: Retrieve Item
    get_res = client.get("/api/v1/items/ITM-9001")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Cloud Enterprise Router"
    assert get_res.json()["quantity"] == 15

def test_create_duplicate_item_conflict():
    payload = {
        "item_id": "ITM-DUP-01",
        "name": "Redundant Power Supply",
        "quantity": 2,
        "unit_price": 120.00
    }
    res1 = client.post("/api/v1/items", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/items", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]

def test_get_nonexistent_item_404():
    res = client.get("/api/v1/items/NON_EXISTENT")
    assert res.status_code == 404
    assert res.json()["detail"] == "Item not found"

def test_process_order_pipeline_integration():
    payload = {
        "item_id": "ITM-ORDER-77",
        "name": "High Availability Switch",
        "quantity": 4,
        "unit_price": 250.00
    }
    res = client.post("/api/v1/orders/calculate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["item_id"] == "ITM-ORDER-77"
    assert data["total_cost"] == 1000.00
    assert data["tax"] == 180.00
    assert data["final_amount"] == 1180.00
    assert data["status"] == "CONFIRMED"
