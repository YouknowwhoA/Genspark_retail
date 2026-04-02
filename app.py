from __future__ import annotations

import pandas as pd
import streamlit as st

from src.llm_parser import get_llm_parser_config, is_llm_parser_enabled
from src.parser import execute_query


st.set_page_config(
    page_title="Retail Atelier",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


SAMPLE_PROMPTS = [
    "Customer 888163 discount and store location",
    "How much did customer 109318 pay altogether?",
    "Can you tell me where I can buy item C?",
    "What is the total revenue?",
]


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #F6F3EE;
            --surface-2: #EFE9E1;
            --surface-3: #E4DDD2;
            --text: #2F2A25;
            --text-soft: #7A7268;
            --accent: #C6A97A;
            --accent-hover: #B89664;
            --border: #E0D8CD;
            --divider: #D6CEC2;
            --shadow: 0 10px 24px rgba(47, 42, 37, 0.035);
            --radius-lg: 24px;
            --radius-md: 16px;
            --space-1: 8px;
            --space-2: 12px;
            --space-3: 16px;
            --space-4: 24px;
            --space-5: 32px;
            --space-6: 48px;
        }

        .stApp {
            background: var(--bg);
            color: var(--text);
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        div[data-testid="collapsedControl"],
        [data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            max-width: 1180px;
            padding-top: 20px;
            padding-bottom: 64px;
        }

        .frame {
            max-width: 980px;
            margin: 0 auto;
        }

        .topline {
            padding: 20px 0 32px;
            border-bottom: 1px solid var(--divider);
            margin-bottom: 48px;
        }

        .brand {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 24px;
            flex-wrap: wrap;
        }

        .brand-name {
            font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
            font-size: 1.05rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: var(--text);
        }

        .brand-note {
            color: var(--text-soft);
            font-size: 0.84rem;
            line-height: 1.6;
        }

        .hero {
            padding-bottom: 40px;
        }

        .eyebrow {
            color: var(--text-soft);
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.74rem;
            margin-bottom: 20px;
        }

        .hero-title {
            font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
            font-size: clamp(2.7rem, 4vw, 4.6rem);
            line-height: 0.98;
            letter-spacing: -0.035em;
            color: var(--text);
            max-width: 9ch;
            margin-bottom: 20px;
        }

        .hero-copy {
            color: var(--text-soft);
            font-size: 1rem;
            line-height: 1.95;
            max-width: 58ch;
        }

        .composer {
            background: var(--surface-2);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 28px;
            margin-bottom: 48px;
        }

        .section-title {
            font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
            color: var(--text);
            font-size: 1.4rem;
            letter-spacing: -0.02em;
            margin-bottom: 8px;
        }

        .section-copy {
            color: var(--text-soft);
            font-size: 0.95rem;
            line-height: 1.8;
            margin-bottom: 20px;
            max-width: 54ch;
        }

        div[data-baseweb="textarea"] {
            border-radius: var(--radius-md) !important;
            border: 1px solid var(--divider) !important;
            background: var(--bg) !important;
            box-shadow: none !important;
        }

        div[data-baseweb="textarea"] textarea {
            color: var(--text) !important;
            font-size: 1rem !important;
            line-height: 1.85 !important;
            background: transparent !important;
            padding: 10px 4px !important;
        }

        div[data-baseweb="textarea"] textarea::placeholder {
            color: var(--text-soft) !important;
        }

        .stFormSubmitButton > button,
        .stButton > button {
            min-height: 46px !important;
            border-radius: 999px !important;
            font-size: 0.94rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.01em !important;
            padding: 0 22px !important;
        }

        .stFormSubmitButton > button {
            background: var(--accent) !important;
            color: var(--text) !important;
            border: 1px solid var(--accent) !important;
            box-shadow: none !important;
        }

        .stFormSubmitButton > button:hover {
            background: var(--accent-hover) !important;
            border-color: var(--accent-hover) !important;
        }

        .quiet-secondary button {
            background: transparent !important;
            color: var(--text) !important;
            border: 1px solid var(--divider) !important;
            box-shadow: none !important;
        }

        .quiet-secondary button:hover {
            background: var(--surface-3) !important;
        }

        .conversation {
            padding-top: 8px;
        }

        .conversation-heading {
            margin-bottom: 24px;
        }

        div[data-testid="stChatMessage"] {
            background: var(--surface-2);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 18px 18px 12px;
            margin-bottom: 16px;
            box-shadow: none;
        }

        div[data-testid="stChatMessage"] p {
            color: var(--text);
            line-height: 1.85;
            font-size: 1rem;
        }

        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
            margin-bottom: 8px;
        }

        .chip {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            border: 1px solid var(--divider);
            background: var(--bg);
            color: var(--text-soft);
            font-size: 0.76rem;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        }

        [data-testid="stExpander"] {
            border-radius: 16px !important;
            border: 1px solid var(--border) !important;
            overflow: hidden !important;
            background: var(--bg) !important;
        }

        .stDataFrame {
            border-radius: 16px !important;
            overflow: hidden !important;
            border: 1px solid var(--border) !important;
        }

        .empty-state {
            border-top: 1px solid var(--divider);
            padding-top: 24px;
            color: var(--text-soft);
            line-height: 1.9;
            max-width: 52ch;
        }

        @media (max-width: 768px) {
            .block-container {
                padding-top: 16px;
                padding-bottom: 48px;
            }

            .topline {
                margin-bottom: 36px;
            }

            .hero-title {
                max-width: none;
            }

            .composer {
                padding: 20px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "prompt_input" not in st.session_state:
        st.session_state.prompt_input = ""


def render_header() -> None:
    config = get_llm_parser_config()
    parser_note = f"OpenAI parsing enabled with {config.model}" if is_llm_parser_enabled(config) else "Rule-based parsing active"
    st.markdown(
        f"""
        <div class="frame">
            <div class="topline">
                <div class="brand">
                    <div class="brand-name">Retail Atelier</div>
                    <div class="brand-note">{parser_note}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="frame">
            <div class="hero">
                <div class="eyebrow">Quiet Retail Intelligence</div>
                <div class="hero-title">Ask one clear question.</div>
                <div class="hero-copy">
                    A restrained interface for customer, product, and business answers.
                    The experience favors tone, spacing, and precision over visible feature density.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def handle_user_input(prompt: str) -> None:
    clean_prompt = prompt.strip()
    if not clean_prompt:
        return

    st.session_state.messages.append({"role": "user", "content": clean_prompt})
    result = execute_query(clean_prompt)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "result": result,
        }
    )


def render_prompt_section() -> None:
    st.markdown('<div class="frame"><div class="composer">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Compose</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Customer details, product availability, and business totals are all supported. Keep the phrasing natural.</div>',
        unsafe_allow_html=True,
    )

    with st.form("luxury_query_form", clear_on_submit=True):
        prompt = st.text_area(
            "Ask",
            key="prompt_input",
            height=110,
            placeholder="Customer 888163 discount and store location",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Analyze")

    if submitted:
        handle_user_input(prompt)
        st.rerun()

    with st.expander("Sample prompts", expanded=False):
        for sample in SAMPLE_PROMPTS:
            st.code(sample, language=None)

    if st.session_state.messages:
        st.markdown('<div class="quiet-secondary">', unsafe_allow_html=True)
        if st.button("Clear conversation"):
            st.session_state.messages = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)


def summarize_data(data: dict | None) -> tuple[str | None, pd.DataFrame | None]:
    if not data:
        return None, None

    if "transactions" in data:
        frame = pd.DataFrame(data["transactions"])
        return f"{len(frame)} record(s)", frame.head(20)

    if "stores" in data:
        frame = pd.DataFrame({"StoreLocation": data["stores"][:100]})
        return f"{len(data['stores'])} store row(s)", frame

    if "field_values" in data:
        rows = []
        for field, values in data["field_values"].items():
            rows.append(
                {
                    "Field": field.replace("_", " "),
                    "Values": ", ".join(str(value).replace("\n", ", ") for value in values[:5]),
                }
            )
        return "Field summary", pd.DataFrame(rows)

    scalar_fields = {
        key: value
        for key, value in data.items()
        if key not in {"status", "message"} and not isinstance(value, (list, dict))
    }
    if scalar_fields:
        return "Summary", pd.DataFrame([scalar_fields])

    return None, None


def render_assistant_details(result: dict) -> None:
    parsed = result["parsed_query"]
    chip_values = [
        f"intent={parsed.get('intent')}",
        f"status={parsed.get('status')}",
        f"confidence={parsed.get('confidence')}",
    ]
    if parsed.get("customer_id"):
        chip_values.append(f"customer_id={parsed['customer_id']}")
    if parsed.get("product_id"):
        chip_values.append(f"product_id={parsed['product_id']}")
    if parsed.get("requested_fields"):
        chip_values.append(f"fields={','.join(parsed['requested_fields'])}")

    chips = "".join(f'<span class="chip">{value}</span>' for value in chip_values)
    st.markdown(f'<div class="chip-row">{chips}</div>', unsafe_allow_html=True)

    preview_title, preview_frame = summarize_data(result.get("data"))
    if preview_frame is not None:
        with st.expander(preview_title or "Details", expanded=False):
            st.dataframe(preview_frame, use_container_width=True, hide_index=True)

    with st.expander("Structured parse", expanded=False):
        st.json(parsed)


def render_conversation() -> None:
    st.markdown('<div class="frame"><div class="conversation">', unsafe_allow_html=True)
    st.markdown('<div class="conversation-heading"><div class="section-title">Result</div></div>', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown(
            """
            <div class="empty-state">
                Begin with one focused prompt. Secondary system detail stays tucked away below each answer so the page remains calm and editorial.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant":
                    render_assistant_details(message["result"])

    st.markdown("</div></div>", unsafe_allow_html=True)


def main() -> None:
    apply_styles()
    init_state()
    render_header()
    render_hero()
    render_prompt_section()
    render_conversation()


if __name__ == "__main__":
    main()
