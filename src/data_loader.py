from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "data" / "Retail_Transaction_Dataset.csv"


@lru_cache(maxsize=1)
def load_transactions(csv_path: Path | None = None) -> list[dict[str, Any]]:
    """Load the retail transaction dataset into a list of row dictionaries."""
    path = csv_path or DATASET_PATH

    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return list(reader)


def clear_transaction_cache() -> None:
    load_transactions.cache_clear()


def summarize_dataset(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a few high-signal summary stats for quick inspection."""
    columns = list(rows[0].keys()) if rows else []
    null_counts = {column: 0 for column in columns}

    for row in rows:
        for column, value in row.items():
            if value is None or str(value).strip() == "":
                null_counts[column] += 1

    return {
        "row_count": len(rows),
        "columns": columns,
        "null_counts": null_counts,
        "unique_customers": len({row["CustomerID"] for row in rows}),
        "unique_products": len({row["ProductID"] for row in rows}),
        "unique_categories": len({row["ProductCategory"] for row in rows}),
    }
