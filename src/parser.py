from __future__ import annotations

import re
from typing import Any

from src.llm_parser import get_llm_parser_config, is_llm_parser_enabled, parse_query_with_openai
from src.query_service import (
    CUSTOMER_FIELD_LABELS,
    get_customer_field_values,
    get_customer_purchase_history,
    get_customer_total_spent,
    get_product_average_discount,
    get_product_stores,
    get_total_revenue,
)


CUSTOMER_HISTORY_INTENT = "customer_purchase_history"
CUSTOMER_TOTAL_SPENT_INTENT = "customer_total_spent"
CUSTOMER_FIELD_LOOKUP_INTENT = "customer_field_lookup"
PRODUCT_AVERAGE_DISCOUNT_INTENT = "product_average_discount"
PRODUCT_STORES_INTENT = "product_stores"
BUSINESS_TOTAL_REVENUE_INTENT = "business_total_revenue"
UNKNOWN_INTENT = "unknown"

VALID_PRODUCT_IDS = {"A", "B", "C", "D"}
FIELD_PATTERNS = {
    "discount": ["discount", "discounts", "discount applied"],
    "store_location": ["store location", "location", "store", "stores", "where did", "where does", "where", "shop", "shopped"],
    "payment_method": ["payment method", "paid with", "payment"],
    "transaction_date": ["date", "when", "transaction date", "time"],
    "product_id": ["product id", "product", "item"],
    "product_category": ["category", "product category"],
    "quantity": ["quantity", "how many"],
    "price": ["price", "unit price"],
    "total_amount": ["total amount", "amount", "total", "paid"],
}


def _normalize_query(query: str) -> str:
    return " ".join(query.strip().lower().split())


def _extract_customer_id(query: str) -> str | None:
    prefixed_match = re.search(r"\bc(\d{2,})\b", query, re.IGNORECASE)
    if prefixed_match:
        return prefixed_match.group(1)

    customer_context_match = re.search(
        r"\bcustomer\s*#?\s*(\d{2,})\b",
        query,
        re.IGNORECASE,
    )
    if customer_context_match:
        return customer_context_match.group(1)

    return None


def _extract_product_id(query: str) -> str | None:
    prefixed_match = re.search(r"\bp(\d{2,})\b", query, re.IGNORECASE)
    if prefixed_match:
        return prefixed_match.group(1).upper()

    contextual_match = re.search(
        r"\bproduct\s*#?\s*([a-z])\b",
        query,
        re.IGNORECASE,
    )
    if contextual_match:
        product_id = contextual_match.group(1).upper()
        return product_id if product_id in VALID_PRODUCT_IDS else product_id

    standalone_match = re.search(r"\b(?:product|item)\s+([a-z])\b", query, re.IGNORECASE)
    if standalone_match:
        product_id = standalone_match.group(1).upper()
        return product_id if product_id in VALID_PRODUCT_IDS else product_id

    return None


def _extract_requested_fields(normalized_query: str) -> list[str]:
    requested_fields: list[str] = []
    for field, patterns in FIELD_PATTERNS.items():
        if any(pattern in normalized_query for pattern in patterns):
            requested_fields.append(field)
    return requested_fields


def _detect_intent(normalized_query: str) -> str:
    has_customer = "customer" in normalized_query
    has_product = "product" in normalized_query or "item" in normalized_query
    has_spent = any(
        keyword in normalized_query
        for keyword in ["spent", "spend", "total spent", "pay altogether", "paid altogether", "pay in total", "paid in total"]
    )
    has_history = any(
        keyword in normalized_query
        for keyword in ["purchase history", "purchased", "bought", "buy", "transactions", "orders", "history"]
    )
    has_discount = "discount" in normalized_query
    has_store = any(
        keyword in normalized_query
        for keyword in ["store", "stores", "sell", "sells", "where can i buy", "where i can buy", "buy item", "buy product"]
    )
    has_revenue = any(
        keyword in normalized_query
        for keyword in ["revenue", "total revenue", "sales", "total sales", "business", "transactions overall"]
    )
    customer_field_request = any(
        keyword in normalized_query
        for keyword in [
            "discount",
            "store location",
            "location",
            "payment method",
            "paid with",
            "date",
            "when",
            "category",
            "quantity",
            "price",
            "shop",
            "shopped",
        ]
    )

    if has_customer and has_spent:
        return CUSTOMER_TOTAL_SPENT_INTENT
    if has_customer and customer_field_request:
        return CUSTOMER_FIELD_LOOKUP_INTENT
    if has_customer and has_history:
        return CUSTOMER_HISTORY_INTENT
    if has_product and has_discount:
        return PRODUCT_AVERAGE_DISCOUNT_INTENT
    if has_product and has_store:
        return PRODUCT_STORES_INTENT
    if has_revenue:
        return BUSINESS_TOTAL_REVENUE_INTENT

    if has_customer:
        return CUSTOMER_HISTORY_INTENT
    if has_product:
        return PRODUCT_STORES_INTENT if has_store else PRODUCT_AVERAGE_DISCOUNT_INTENT

    return UNKNOWN_INTENT


def parse_query_rule_based(query: str) -> dict[str, Any]:
    normalized_query = _normalize_query(query)
    customer_id = _extract_customer_id(query)
    product_id = _extract_product_id(query)
    requested_fields = _extract_requested_fields(normalized_query)
    intent = _detect_intent(normalized_query)

    missing_fields: list[str] = []
    if intent in {CUSTOMER_HISTORY_INTENT, CUSTOMER_TOTAL_SPENT_INTENT, CUSTOMER_FIELD_LOOKUP_INTENT} and not customer_id:
        missing_fields.append("customer_id")
    if intent in {PRODUCT_AVERAGE_DISCOUNT_INTENT, PRODUCT_STORES_INTENT} and not product_id:
        missing_fields.append("product_id")
    if intent == CUSTOMER_FIELD_LOOKUP_INTENT and not requested_fields:
        missing_fields.append("requested_fields")

    confidence = "high"
    if intent == UNKNOWN_INTENT:
        confidence = "low"
    elif missing_fields:
        confidence = "medium"

    if intent == UNKNOWN_INTENT:
        return {
            "status": "needs_clarification",
            "parser_type": "rule_based",
            "intent": intent,
            "confidence": confidence,
            "query": query,
            "message": "I could not confidently classify this query yet.",
            "missing_fields": [],
            "customer_id": customer_id,
            "product_id": product_id,
            "requested_fields": requested_fields,
        }

    if missing_fields:
        return {
            "status": "needs_clarification",
            "parser_type": "rule_based",
            "intent": intent,
            "confidence": confidence,
            "query": query,
            "message": f"Missing required field(s): {', '.join(missing_fields)}.",
            "missing_fields": missing_fields,
            "customer_id": customer_id,
            "product_id": product_id,
            "requested_fields": requested_fields,
        }

    return {
        "status": "ok",
        "parser_type": "rule_based",
        "intent": intent,
        "confidence": confidence,
        "query": query,
        "customer_id": customer_id,
        "product_id": product_id,
        "missing_fields": [],
        "requested_fields": requested_fields,
    }


def parse_query(query: str) -> dict[str, Any]:
    config = get_llm_parser_config()
    if is_llm_parser_enabled(config):
        try:
            llm_parsed = parse_query_with_openai(query)
            llm_parsed["fallback_used"] = False
            return llm_parsed
        except Exception as exc:
            if config.mode == "openai_required":
                return {
                    "status": "needs_clarification",
                    "parser_type": "openai_responses",
                    "intent": UNKNOWN_INTENT,
                    "confidence": "low",
                    "query": query,
                    "message": f"LLM parser failed: {exc}",
                    "missing_fields": [],
                    "customer_id": None,
                    "product_id": None,
                    "requested_fields": [],
                    "fallback_used": False,
                }

    parsed = parse_query_rule_based(query)
    parsed["fallback_used"] = config.mode == "openai_optional"
    return parsed


def execute_query(query: str) -> dict[str, Any]:
    parsed = parse_query(query)
    if parsed["status"] != "ok":
        return {
            "status": parsed["status"],
            "parsed_query": parsed,
            "answer": parsed["message"],
            "data": None,
        }

    intent = parsed["intent"]
    if intent == CUSTOMER_HISTORY_INTENT:
        data = get_customer_purchase_history(parsed["customer_id"])
    elif intent == CUSTOMER_TOTAL_SPENT_INTENT:
        data = get_customer_total_spent(parsed["customer_id"])
    elif intent == CUSTOMER_FIELD_LOOKUP_INTENT:
        data = get_customer_field_values(parsed["customer_id"], parsed.get("requested_fields", []))
    elif intent == PRODUCT_AVERAGE_DISCOUNT_INTENT:
        data = get_product_average_discount(parsed["product_id"])
    elif intent == PRODUCT_STORES_INTENT:
        data = get_product_stores(parsed["product_id"])
    elif intent == BUSINESS_TOTAL_REVENUE_INTENT:
        data = get_total_revenue()
    else:
        return {
            "status": "needs_clarification",
            "parsed_query": parsed,
            "answer": "I could not route this question to a supported query yet.",
            "data": None,
        }

    answer = build_answer(parsed, data)
    return {
        "status": data.get("status", "ok"),
        "parsed_query": parsed,
        "answer": answer,
        "data": data,
    }


def build_answer(parsed: dict[str, Any], data: dict[str, Any]) -> str:
    if data.get("status") != "ok":
        return data.get("message", "No data found.")

    intent = parsed["intent"]
    if intent == CUSTOMER_HISTORY_INTENT:
        return (
            f"Customer {parsed['customer_id']} has {data['transaction_count']} transaction(s) "
            "in the dataset."
        )
    if intent == CUSTOMER_TOTAL_SPENT_INTENT:
        return (
            f"Customer {parsed['customer_id']} spent a total of "
            f"${data['total_spent']:,.2f} across {data['transaction_count']} transaction(s)."
        )
    if intent == CUSTOMER_FIELD_LOOKUP_INTENT:
        customer_id = parsed["customer_id"]
        transaction_count = data["transaction_count"]
        parts = []
        for field in data["requested_fields"]:
            values = data["field_values"].get(field, [])
            label = CUSTOMER_FIELD_LABELS.get(field, field.replace("_", " "))
            rendered_values = []
            for value in values[:3]:
                if field == "discount":
                    rendered_values.append(f"{float(value):.2f}%")
                elif field in {"price", "total_amount"}:
                    rendered_values.append(f"${float(value):,.2f}")
                else:
                    rendered_values.append(str(value).replace("\n", ", "))
            value_text = ", ".join(rendered_values) if rendered_values else "not available"
            if len(values) > 3:
                value_text += f", and {len(values) - 3} more"
            parts.append(f"{label}: {value_text}")

        return (
            f"For customer {customer_id}, I found {transaction_count} transaction(s). "
            + " ".join(parts)
        )
    if intent == PRODUCT_AVERAGE_DISCOUNT_INTENT:
        return (
            f"Product {parsed['product_id']} has an average discount of "
            f"{data['average_discount']:.2f}% across {data['transaction_count']} transaction(s)."
        )
    if intent == PRODUCT_STORES_INTENT:
        return (
            f"Product {parsed['product_id']} appears in {data['store_count']} store record(s) "
            "in this dataset."
        )
    if intent == BUSINESS_TOTAL_REVENUE_INTENT:
        return (
            f"Total revenue is ${data['total_revenue']:,.2f} across "
            f"{data['total_transactions']} transaction(s)."
        )

    return "I routed the query, but no answer template is defined yet."
