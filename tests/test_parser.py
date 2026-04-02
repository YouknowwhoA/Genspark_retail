from __future__ import annotations

from src.parser import (
    CUSTOMER_FIELD_LOOKUP_INTENT,
    BUSINESS_TOTAL_REVENUE_INTENT,
    CUSTOMER_TOTAL_SPENT_INTENT,
    PRODUCT_AVERAGE_DISCOUNT_INTENT,
    PRODUCT_STORES_INTENT,
    execute_query,
    parse_query,
)


def test_parse_customer_total_spent_query() -> None:
    parsed = parse_query("How much has customer C109318 spent in total?")
    assert parsed["status"] == "ok"
    assert parsed["intent"] == CUSTOMER_TOTAL_SPENT_INTENT
    assert parsed["customer_id"] == "109318"


def test_parse_product_discount_query() -> None:
    parsed = parse_query("What's the average discount for product A?")
    assert parsed["status"] == "ok"
    assert parsed["intent"] == PRODUCT_AVERAGE_DISCOUNT_INTENT
    assert parsed["product_id"] == "A"


def test_parse_business_query() -> None:
    parsed = parse_query("What is the total revenue?")
    assert parsed["status"] == "ok"
    assert parsed["intent"] == BUSINESS_TOTAL_REVENUE_INTENT


def test_parse_missing_customer_id_needs_clarification() -> None:
    parsed = parse_query("How much has this customer spent?")
    assert parsed["status"] == "needs_clarification"
    assert parsed["intent"] == CUSTOMER_TOTAL_SPENT_INTENT
    assert "customer_id" in parsed["missing_fields"]


def test_parse_customer_field_lookup_query() -> None:
    parsed = parse_query("customer 888163 discount and store location")
    assert parsed["status"] == "ok"
    assert parsed["intent"] == CUSTOMER_FIELD_LOOKUP_INTENT
    assert parsed["customer_id"] == "888163"
    assert parsed["requested_fields"] == ["discount", "store_location"]


def test_parse_missing_product_id_needs_clarification() -> None:
    parsed = parse_query("Which stores sell this product?")
    assert parsed["status"] == "needs_clarification"
    assert parsed["intent"] == PRODUCT_STORES_INTENT
    assert "product_id" in parsed["missing_fields"]


def test_execute_query_returns_answer_for_valid_query() -> None:
    result = execute_query("How much has customer C109318 spent in total?")
    assert result["status"] == "ok"
    assert "spent a total of" in result["answer"]


def test_execute_query_answers_customer_field_lookup() -> None:
    result = execute_query("customer 888163 discount and store location")
    assert result["status"] == "ok"
    assert "discount:" in result["answer"].lower()
    assert "store location:" in result["answer"].lower()


def test_execute_query_handles_invalid_product_id() -> None:
    result = execute_query("Which stores sell product Z?")
    assert result["status"] == "not_found"
    assert "No transactions found for product Z." == result["answer"]
