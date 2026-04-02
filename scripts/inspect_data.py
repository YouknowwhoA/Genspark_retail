from __future__ import annotations

from collections import defaultdict

from src.data_loader import load_transactions, summarize_dataset


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def main() -> None:
    rows = load_transactions()
    summary = summarize_dataset(rows)

    print("=== Dataset Summary ===")
    print(f"Rows: {summary['row_count']}")
    print(f"Columns: {summary['columns']}")
    print(f"Null counts: {summary['null_counts']}")
    print(f"Unique customers: {summary['unique_customers']}")
    print(f"Unique products: {summary['unique_products']}")
    print(f"Unique categories: {summary['unique_categories']}")

    customer_id = "109318"
    product_id = "A"

    customer_history = [row for row in rows if row["CustomerID"] == customer_id]
    product_rows = [row for row in rows if row["ProductID"] == product_id]

    total_revenue = sum(float(row["TotalAmount"]) for row in rows)
    total_transactions = len(rows)
    avg_discount = (
        sum(float(row["DiscountApplied(%)"]) for row in product_rows) / len(product_rows)
        if product_rows
        else 0.0
    )

    stores = sorted({row["StoreLocation"].splitlines()[0] for row in product_rows})
    revenue_by_product = defaultdict(float)
    for row in rows:
        revenue_by_product[row["ProductID"]] += float(row["TotalAmount"])

    print("\n=== Manual Query Checks ===")
    print(f"Sample customer: {customer_id}")
    print(f"Purchase count: {len(customer_history)}")
    print(f"Customer history sample: {customer_history[:2]}")
    print(f"Customer total spent: {format_currency(sum(float(row['TotalAmount']) for row in customer_history))}")
    print(f"Sample product: {product_id}")
    print(f"Average discount for product {product_id}: {avg_discount:.2f}%")
    print(f"Stores selling product {product_id}: {stores[:5]}")
    print(f"Total revenue: {format_currency(total_revenue)}")
    print(f"Total transactions: {total_transactions}")
    print(f"Revenue by product: {dict(sorted(revenue_by_product.items()))}")


if __name__ == "__main__":
    main()

