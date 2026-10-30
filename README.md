# Vendor Performance & Retail Analytics

An end-to-end Python, SQLite, and Power BI portfolio project for analyzing vendor purchasing, retail sales, and inventory signals.

## Business questions
- Which vendors contribute the largest share of purchasing?
- Which vendor/brand combinations have high purchase value but weak sales?
- How do sales quantities compare with purchased quantities?
- Which products may need pricing, promotion, replenishment, or inventory review?

## Repository structure
```
data/                 # Place source CSVs here locally (excluded from Git)
database/             # Generated SQLite database (excluded from Git)
outputs/              # Generated analysis outputs (excluded from Git)
src/ingest_data.py    # Chunked CSV-to-SQLite ingestion
src/vendor_analysis.py# Vendor/brand metrics
tests/                # Unit tests
.github/workflows/    # GitHub Actions checks
```

## Required input files
Place these six CSVs inside `data/`: `purchases.csv`, `purchase_prices.csv`, `vendor_invoice.csv`, `begin_inventory.csv`, `end_inventory.csv`, and `sales.csv`.

**Data licensing:** Raw source data is intentionally not committed. Obtain it from the original provider and verify redistribution rights before sharing. Never commit personal, confidential, or restricted data.

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

python src/ingest_data.py --data-dir data --db database/inventory.db
python src/vendor_analysis.py --db database/inventory.db --output outputs/vendor_brand_performance.csv
python -m unittest discover -s tests -v
```

CSV ingestion is chunked (100,000 rows by default). Adjust with `--chunksize`.

## Metric definitions and cautions
| Metric | Definition | Caution |
|---|---|---|
| Gross profit before freight | Sales dollars - purchase dollars | Not net profit; excludes freight and operating costs |
| Gross margin before freight | Gross profit / sales dollars * 100 | Undefined when sales are zero |
| Sales-to-purchase value ratio | Sales dollars / purchase dollars | Descriptive ratio; timing and opening stock matter |
| Sell-through quantity ratio | Sales quantity / purchased quantity | Can exceed 1 when opening or prior-period stock is sold |
| Vendor total freight | Sum of freight by vendor | Vendor-grain value; do not sum repeatedly across brand rows |

## Modeling decisions
- Aggregate purchases, sales, and freight independently before joining to prevent row multiplication.
- Join purchase-price reference data on both vendor number and brand.
- Preserve undefined ratios as null rather than infinity or arbitrary zero.
- Keep freight at vendor grain unless an explicit allocation method is documented.
- Revalidate any historical report figures against the source data before external use.

## Current scope and limitations
This repository currently contains the reproducible ingestion/analysis scripts, tests, and CI workflow. Original notebooks, the historical PDF report, and the Power BI dashboard are not yet included in this GitHub repository. They should be added only after checking that their embedded data and contents are safe and licensed for public distribution.

No license is declared for third-party datasets or artifacts. Add a repository license only after confirming rights.

## Author
Jwala Pratap Singh
