# Day 1 Findings

## Dataset basics
- File: `data/Retail_Transaction_Dataset.csv`
- Row count: 100000
- No empty values were found in the initial scan.

## Columns and likely meaning
- `CustomerID`: customer identifier
- `ProductID`: product identifier
- `Quantity`: quantity purchased in the transaction
- `Price`: unit price before discount
- `TransactionDate`: transaction timestamp
- `PaymentMethod`: payment type
- `StoreLocation`: store address text
- `ProductCategory`: high-level category
- `DiscountApplied(%)`: discount percentage
- `TotalAmount`: final transaction total

## Important observations
- `ProductID` only has four values: `A`, `B`, `C`, `D`
- `ProductCategory` also has four values: `Books`, `Clothing`, `Electronics`, `Home Decor`
- The dataset appears transaction-level and is enough to answer customer, product, and aggregated business queries.
- The homework prompt examples use IDs like `P1234`, but this dataset uses simpler product IDs. We should call that out in the README and demo.

## Manual query checks already verified
- Customer purchase history can be filtered by `CustomerID`
- Customer total spend can be computed from `TotalAmount`
- Product average discount can be computed from `DiscountApplied(%)`
- Product store list can be derived from `StoreLocation`
- Business metrics like total revenue and total transactions can be computed directly

## Example values from the first pass
- Sample customer checked: `109318`
- Sample product checked: `A`
- Total revenue across the dataset: about `$24,833,495.51`
- Total transactions: `100000`

## Today I moved the system forward by
- Creating the project folder and copying the dataset into it
- Running the first real data inspection
- Confirming that the dataset can support all three required query types

