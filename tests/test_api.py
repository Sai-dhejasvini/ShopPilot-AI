"""
ShopPilot AI - FastAPI Endpoints Test Suite
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_healthcheck():
    """Verify /health returns 200 OK and catalog stats."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["catalog_size"] > 0


def test_api_chat_endpoint():
    """Verify /api/chat processes query and returns structured response."""
    payload = {"message": "Find laptops under 70k for programming"}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "tools_used" in data
    assert len(data["tools_used"]) >= 2
    assert "products" in data


def test_api_search_endpoint():
    """Verify /api/search deterministic filtering."""
    payload = {"category": "Laptop", "max_price": 70000.0}
    response = client.post("/api/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert data["count"] > 0
    for p in data["products"]:
        assert p["price"] <= 70000.0


def test_api_compare_endpoint():
    """Verify /api/compare returns side-by-side matrix."""
    payload = {"product_ids": ["LAP001", "LAP004"]}
    response = client.post("/api/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["products_count"] == 2
    assert "comparison_matrix" in data


def test_api_products_list_and_details():
    """Verify /api/products and /api/products/{id}."""
    res_list = client.get("/api/products?limit=5")
    assert res_list.status_code == 200
    assert len(res_list.json()["products"]) <= 5

    res_detail = client.get("/api/products/LAP001")
    assert res_detail.status_code == 200
    assert res_detail.json()["product"]["product_id"] == "LAP001"

    res_404 = client.get("/api/products/NON_EXISTENT_999")
    assert res_404.status_code == 404


def test_api_analytics_endpoint():
    """Verify /api/analytics returns dashboard metrics."""
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "category_distribution" in data
    assert "budget_distribution" in data
    assert "catalog_gaps" in data
