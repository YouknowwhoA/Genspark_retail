# Bug Journal

This file records notable implementation bugs, their symptoms, the root cause, and how we fixed them. It is useful both for debugging discipline and for interview discussion.

## Bug 1: Product keyword misread as product id
- Date: 2026-04-01
- Symptom: queries like `What's the average discount for product A?` were parsed with `product_id='RODUCT'`.
- Error pattern: the parser looked correct at a high level but returned obviously wrong ids in the parsed JSON.
- Root cause: the regex accepted any token starting with `p...`, so the word `product` itself matched the product-id extractor.
- Fix: narrowed the prefixed product regex and prioritized contextual extraction rules such as `product A` and `item C`.
- Interview takeaway: tests caught a realistic parser bug early, and the fix improved routing reliability without rewriting the parser.

## Bug 2: Natural-language customer queries collapsed into generic history
- Date: 2026-04-02
- Symptom: a query like `customer 888163 discount and store location` returned `Customer 888163 has 1 transaction(s)` instead of directly answering the requested fields.
- Error pattern: the system found the correct customer row but ignored the field-level ask.
- Root cause: the parser only supported coarse intents like `customer_purchase_history` and `customer_total_spent`, so field-level customer questions had no dedicated route.
- Fix: introduced `customer_field_lookup`, added `requested_fields` extraction, extended the query layer to return customer field values, and updated answer generation to respond directly with values like discount and store location.
- Interview takeaway: this is a good example of evolving from id-driven routing to field-aware intent parsing based on real user testing.

## Bug 3: Streamlit session-state mutation after widget instantiation
- Date: 2026-04-02
- Symptom: Streamlit raised `StreamlitAPIException: st.session_state.prompt_input cannot be modified after the widget with key prompt_input is instantiated`.
- Error pattern: the UI crashed right after submitting a query from the luxury redesign form.
- Root cause: the code used `st.text_area(key="prompt_input")` and then mutated `st.session_state.prompt_input` in the same execution cycle after the widget was already created.
- Fix: switched the form to `clear_on_submit=True` and removed the manual mutation of `st.session_state.prompt_input`.
- Interview takeaway: this shows awareness of framework-specific state rules and a clean fix that simplifies the form logic instead of adding workarounds.

## Bug 4: API key loaded but parser still showed local mode
- Date: 2026-04-03
- Symptom: the UI showed `API key loaded` but still labeled the system as `Local Mode` instead of the expected GPT live mode.
- Error pattern: it looked like the key was not being used, but the real issue was a mode mismatch rather than a missing secret.
- Root cause: `.env` contained an API key, but `LLM_PARSER_MODE` was still set to `rule_based`, so the app intentionally stayed on the local parser.
- Fix: clarified the UI so it shows a direct hint when the key is present but GPT mode is not enabled, and documented that `LLM_PARSER_MODE=openai_optional` is required to activate GPT parsing.
- Interview takeaway: environment flags matter as much as secrets; the system can be correctly configured with a valid key but still remain in fallback mode by design.
