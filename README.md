# Retail Data Analytics Chat System

A small interview project that answers retail analytics questions from a transaction dataset through a chat-style interface.

## Repository Deliverables
- Complete project code for local setup and demo
- Streamlit chat UI and FastAPI backend
- Dataset setup instructions
- Environment variable instructions
- Example queries
- Screenshots of the system in action

## What It Supports
- Customer purchase history queries
- Customer total spend queries
- Product average discount queries
- Product store availability queries
- Aggregated business metrics such as total revenue
- A Streamlit chat UI
- A FastAPI backend
- Rule-based intent parsing with optional OpenAI-powered parsing

## Project Structure
```text
genspark_retail_chat/
├── app.py
├── data/
├── docs/
├── notes/
├── scripts/
├── src/
└── tests/
```

## Dataset Notes
- File used: `data/Retail_Transaction_Dataset.csv`
- The dataset contains `100,000` rows.
- `ProductID` values are `A/B/C/D`, not `P1234`-style IDs from the homework examples.
- There were no empty values in the first inspection pass.

## Dataset Download / Setup
1. Download the Kaggle Retail Transaction Dataset:
   `https://www.kaggle.com/datasets/fahadrehman07/retail-transaction-dataset/data`
2. Place the CSV file at:
   `data/Retail_Transaction_Dataset.csv`
3. If the file is already present in the repository, no extra dataset setup is required.

## Setup
```bash
cd '/Users/dzwlalala/Documents/New project/genspark_retail_chat'
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

## Environment Variables
The project supports both rule-based parsing and optional OpenAI-powered parsing.

Required only if you want OpenAI parsing:
```bash
LLM_PARSER_MODE=openai_optional
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.4-mini
```

Modes:
- `rule_based`: always use the local parser
- `openai_optional`: try OpenAI first, then fall back safely
- `openai_required`: require OpenAI parsing and surface API/parser failure directly

## Run The App
Streamlit UI:
```bash
cd '/Users/dzwlalala/Documents/New project/genspark_retail_chat'
PYTHONPATH=. ./.venv/bin/streamlit run app.py
```

FastAPI server:
```bash
cd '/Users/dzwlalala/Documents/New project/genspark_retail_chat'
PYTHONPATH=. ./.venv/bin/uvicorn src.api:app --reload
```

## Run Tests
```bash
cd '/Users/dzwlalala/Documents/New project/genspark_retail_chat'
PYTHONPATH=. ./.venv/bin/pytest -q
```

## Example Queries
- `How much has customer C109318 spent in total?`
- `What has customer 109318 purchased?`
- `customer 888163 discount and store location`
- `What's the average discount for product A?`
- `Which stores sell product B?`
- `What is the total revenue?`

## Architecture Summary
1. The dataset is loaded from CSV and cached in memory.
2. Query functions answer customer, product, and business questions.
3. The parser turns natural language into a structured intent.
4. Field-aware customer queries can request specific values like discount or store location.
5. The UI and API both call the same parser and query layer.
6. If the optional LLM parser is enabled, the system tries that first and falls back when needed.

## Screenshots
Overview screen:

![Overview UI](docs/screenshots/overview.png)

Conversation and result screen:

![Conversation UI](docs/screenshots/conversation.png)

## Notes For Review
- The default experience works without any API key through the rule-based parser.
- Optional OpenAI parsing improves natural-language flexibility but is not required to run the project.
- The bug-fix journey and debugging notes are recorded in `notes/bug_journal.md`.
