from __future__ import annotations

from src.query_service import (
    get_customer_field_values,
    get_customer_total_spent,
    get_product_average_discount,
    get_product_stores,
    get_total_revenue,
)


def test_customer_total_spent_returns_ok_for_valid_customer() -> None:
    result = get_customer_total_spent("109318")
    assert result["status"] == "ok"
    assert result["customer_id"] == "109318"
    assert result["total_spent"] > 0


def test_product_average_discount_returns_ok_for_valid_product() -> None:
    result = get_product_average_discount("A")
    assert result["status"] == "ok"
    assert result["product_id"] == "A"
    assert result["average_discount"] > 0


def test_product_stores_returns_not_found_for_invalid_product() -> None:
    result = get_product_stores("Z")
    assert result["status"] == "not_found"
    assert result["stores"] == []


def test_total_revenue_is_positive() -> None:
    result = get_total_revenue()
    assert result["status"] == "ok"
    assert result["total_transactions"] == 100000
    assert result["total_revenue"] > 0


def test_customer_field_values_returns_requested_fields() -> None:
    result = get_customer_field_values("109318", ["discount", "store_location"])
    assert result["status"] == "ok"
    assert result["requested_fields"] == ["discount", "store_location"]
    assert "discount" in result["field_values"]
    assert "store_location" in result["field_values"]
