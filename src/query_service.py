from __future__ import annotations

from typing import Any

from src.data_loader import load_transactions


CUSTOMER_FIELD_LABELS = {
    "discount": "discount",
    "store_location": "store location",
    "payment_method": "payment method",
    "transaction_date": "transaction date",
    "product_id": "product id",
    "product_category": "product category",
    "quantity": "quantity",
    "price": "price",
    "total_amount": "total amount",
}

CUSTOMER_FIELD_TO_COLUMN = {
    "discount": "DiscountApplied(%)",
    "store_location": "StoreLocation",
    "payment_method": "PaymentMethod",
    "transaction_date": "TransactionDate",
    "product_id": "ProductID",
    "product_category": "ProductCategory",
    "quantity": "Quantity",
    "price": "Price",
    "total_amount": "TotalAmount",
}


def _load_rows() -> list[dict[str, Any]]:
    return load_transactions()


def get_customer_purchase_history(customer_id: str) -> dict[str, Any]:
    customer_id = str(customer_id).strip()
    rows = [row for row in _load_rows() if row["CustomerID"] == customer_id]

    if not rows:
        return {
            "status": "not_found",
            "message": f"No transactions found for customer {customer_id}.",
            "customer_id": customer_id,
            "transactions": [],
        }

    return {
        "status": "ok",
        "customer_id": customer_id,
        "transaction_count": len(rows),
        "transactions": rows,
    }


def get_customer_total_spent(customer_id: str) -> dict[str, Any]:
    history = get_customer_purchase_history(customer_id)
    if history["status"] != "ok":
        return history

    total_spent = sum(float(row["TotalAmount"]) for row in history["transactions"])
    return {
        "status": "ok",
        "customer_id": history["customer_id"],
        "transaction_count": history["transaction_count"],
        "total_spent": round(total_spent, 2),
    }


def get_customer_field_values(customer_id: str, requested_fields: list[str]) -> dict[str, Any]:
    history = get_customer_purchase_history(customer_id)
    if history["status"] != "ok":
        return history

    normalized_fields = [field for field in requested_fields if field in CUSTOMER_FIELD_TO_COLUMN]
    if not normalized_fields:
        return {
            "status": "needs_clarification",
            "message": "No supported customer fields were requested.",
            "customer_id": customer_id,
            "requested_fields": [],
        }

    field_values: dict[str, list[Any]] = {}
    for field in normalized_fields:
        column = CUSTOMER_FIELD_TO_COLUMN[field]
        values = []
        for row in history["transactions"]:
            value = row[column]
            if value not in values:
                values.append(value)
        field_values[field] = values

    return {
        "status": "ok",
        "customer_id": customer_id,
        "transaction_count": history["transaction_count"],
        "requested_fields": normalized_fields,
        "field_values": field_values,
        "transactions": history["transactions"],
    }


def get_product_average_discount(product_id: str) -> dict[str, Any]:
    product_id = str(product_id).strip().upper()
    rows = [row for row in _load_rows() if row["ProductID"] == product_id]

    if not rows:
        return {
            "status": "not_found",
            "message": f"No transactions found for product {product_id}.",
            "product_id": product_id,
        }

    average_discount = sum(float(row["DiscountApplied(%)"]) for row in rows) / len(rows)
    return {
        "status": "ok",
        "product_id": product_id,
        "transaction_count": len(rows),
        "average_discount": round(average_discount, 2),
    }


def get_product_stores(product_id: str) -> dict[str, Any]:
    product_id = str(product_id).strip().upper()
    rows = [row for row in _load_rows() if row["ProductID"] == product_id]

    if not rows:
        return {
            "status": "not_found",
            "message": f"No transactions found for product {product_id}.",
            "product_id": product_id,
            "stores": [],
        }

    stores = sorted({row["StoreLocation"] for row in rows})
    return {
        "status": "ok",
        "product_id": product_id,
        "store_count": len(stores),
        "stores": stores,
    }


def get_total_revenue() -> dict[str, Any]:
    rows = _load_rows()
    total_revenue = sum(float(row["TotalAmount"]) for row in rows)
    return {
        "status": "ok",
        "total_revenue": round(total_revenue, 2),
        "total_transactions": len(rows),
    }
