from __future__ import annotations

from src.llm_parser import extract_output_text
from src.parser import parse_query


def test_extract_output_text_reads_openai_response_shape() -> None:
    body = {
        "output": [
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": '{"status":"ok","intent":"business_total_revenue"}',
                    }
                ],
            }
        ]
    }
    assert extract_output_text(body) == '{"status":"ok","intent":"business_total_revenue"}'


def test_parse_query_uses_rule_based_fallback_when_llm_is_disabled(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PARSER_MODE", "rule_based")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    parsed = parse_query("What's the average discount for product A?")
    assert parsed["status"] == "ok"
    assert parsed["parser_type"] == "rule_based"
    assert parsed["product_id"] == "A"


def test_parse_query_supports_customer_field_lookup_in_rule_based_mode(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PARSER_MODE", "rule_based")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    parsed = parse_query("customer 888163 discount and store location")
    assert parsed["status"] == "ok"
    assert parsed["intent"] == "customer_field_lookup"
    assert parsed["requested_fields"] == ["discount", "store_location"]
