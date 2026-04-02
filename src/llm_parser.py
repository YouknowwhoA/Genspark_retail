from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


load_dotenv(PROJECT_ROOT / ".env")


@dataclass
class LLMParserConfig:
    mode: str
    api_key: str | None
    model: str


def get_llm_parser_config() -> LLMParserConfig:
    return LLMParserConfig(
        mode=os.getenv("LLM_PARSER_MODE", "rule_based").strip().lower(),
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini").strip(),
    )


def is_llm_parser_enabled(config: LLMParserConfig | None = None) -> bool:
    config = config or get_llm_parser_config()
    return config.mode in {"openai_optional", "openai_required"} and bool(config.api_key)


def parse_query_with_openai(query: str) -> dict[str, Any]:
    config = get_llm_parser_config()
    if not config.api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "status": {"type": "string", "enum": ["ok", "needs_clarification"]},
            "intent": {
                "type": "string",
                "enum": [
                    "customer_field_lookup",
                    "customer_purchase_history",
                    "customer_total_spent",
                    "product_average_discount",
                    "product_stores",
                    "business_total_revenue",
                    "unknown",
                ],
            },
            "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
            "customer_id": {"type": ["string", "null"]},
            "product_id": {"type": ["string", "null"]},
            "requested_fields": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "discount",
                        "store_location",
                        "payment_method",
                        "transaction_date",
                        "product_id",
                        "product_category",
                        "quantity",
                        "price",
                        "total_amount",
                    ],
                },
            },
            "missing_fields": {
                "type": "array",
                "items": {"type": "string"},
            },
            "message": {"type": "string"},
        },
        "required": [
            "status",
            "intent",
            "confidence",
            "customer_id",
            "product_id",
            "requested_fields",
            "missing_fields",
            "message",
        ],
    }

    instructions = (
        "You classify retail analytics questions into JSON. "
        "Supported intents are customer_field_lookup, customer_purchase_history, customer_total_spent, "
        "product_average_discount, product_stores, business_total_revenue, and unknown. "
        "This dataset uses numeric customer IDs and single-letter product IDs A/B/C/D. "
        "If a customer query asks for specific fields like discount or store location, use customer_field_lookup and fill requested_fields. "
        "If the query is missing a required ID, return status='needs_clarification' and list the missing field. "
        "Always return JSON that matches the schema exactly."
    )

    payload = {
        "model": config.model,
        "instructions": instructions,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Classify this query and extract ids as JSON: {query}",
                    }
                ],
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "retail_query_parse",
                "strict": True,
                "schema": schema,
            }
        },
    }

    response = requests.post(
        OPENAI_RESPONSES_URL,
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    body = response.json()
    content_text = extract_output_text(body)
    parsed = normalize_llm_parse(json.loads(content_text))

    return {
        "status": parsed["status"],
        "parser_type": "openai_responses",
        "intent": parsed["intent"],
        "confidence": parsed["confidence"],
        "query": query,
        "customer_id": parsed.get("customer_id"),
        "product_id": parsed.get("product_id"),
        "requested_fields": parsed.get("requested_fields", []),
        "missing_fields": parsed.get("missing_fields", []),
        "message": parsed.get("message", ""),
        "model": config.model,
    }


def extract_output_text(body: dict[str, Any]) -> str:
    for item in body.get("output", []):
        if item.get("type") != "message":
            continue
        for content_item in item.get("content", []):
            if content_item.get("type") == "output_text":
                return content_item["text"]
    raise ValueError("No output_text found in OpenAI response.")


def normalize_llm_parse(parsed: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(parsed)
    intent = normalized.get("intent")
    missing_fields = normalized.get("missing_fields", [])
    requested_fields = normalized.get("requested_fields", [])

    if intent == "unknown":
        normalized["status"] = "needs_clarification"
        return normalized

    if intent == "customer_field_lookup" and not requested_fields:
        normalized["status"] = "needs_clarification"
        if "requested_fields" not in missing_fields:
            missing_fields.append("requested_fields")
        normalized["missing_fields"] = missing_fields
        return normalized

    if missing_fields:
        normalized["status"] = "needs_clarification"
        return normalized

    normalized["status"] = "ok"
    return normalized
