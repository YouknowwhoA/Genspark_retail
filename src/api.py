from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.parser import execute_query, parse_query
from src.query_service import (
    get_customer_purchase_history,
    get_customer_total_spent,
    get_product_average_discount,
    get_product_stores,
    get_total_revenue,
)


app = FastAPI(title="Retail Data Analytics Chat System")


def build_response(payload: dict) -> JSONResponse:
    status_code = 200 if payload.get("status") == "ok" else 404
    return JSONResponse(status_code=status_code, content=payload)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/customer/{customer_id}/history")
def customer_history(customer_id: str) -> JSONResponse:
    return build_response(get_customer_purchase_history(customer_id))


@app.get("/customer/{customer_id}/total-spent")
def customer_total_spent(customer_id: str) -> JSONResponse:
    return build_response(get_customer_total_spent(customer_id))


@app.get("/product/{product_id}/average-discount")
def product_average_discount(product_id: str) -> JSONResponse:
    return build_response(get_product_average_discount(product_id))


@app.get("/product/{product_id}/stores")
def product_stores(product_id: str) -> JSONResponse:
    return build_response(get_product_stores(product_id))


@app.get("/business/total-revenue")
def business_total_revenue() -> JSONResponse:
    return build_response(get_total_revenue())


@app.get("/parse")
def parse_user_query(q: str) -> JSONResponse:
    parsed = parse_query(q)
    status_code = 200 if parsed.get("status") == "ok" else 422
    return JSONResponse(status_code=status_code, content=parsed)


@app.get("/chat")
def chat_query(q: str) -> JSONResponse:
    result = execute_query(q)
    status_code = 200 if result.get("status") == "ok" else 422
    return JSONResponse(status_code=status_code, content=result)
