from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_customer_total_spent_endpoint() -> None:
    response = client.get("/customer/109318/total-spent")
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["customer_id"] == "109318"


def test_invalid_product_endpoint_returns_404() -> None:
    response = client.get("/product/Z/average-discount")
    body = response.json()
    assert response.status_code == 404
    assert body["status"] == "not_found"


def test_parse_endpoint_returns_structured_intent() -> None:
    response = client.get("/parse", params={"q": "How much has customer C109318 spent in total?"})
    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "customer_total_spent"
    assert body["customer_id"] == "109318"


def test_chat_endpoint_returns_clarification_for_ambiguous_query() -> None:
    response = client.get("/chat", params={"q": "How much has this customer spent?"})
    body = response.json()
    assert response.status_code == 422
    assert body["status"] == "needs_clarification"
