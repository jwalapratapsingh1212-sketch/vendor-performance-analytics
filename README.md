# Vendor Performance & Retail Analytics

An end-to-end analytics project for examining vendor purchasing, retail sales, product performance, and inventory signals. The repository combines a reproducible Python/SQLite pipeline with the supplied exploratory notebooks, report, and Power BI dashboard.

> **Data note:** The original source CSVs are deliberately not included. The supplied raw archive contains large datasets, and redistribution rights have not been established. Obtain the source files from their original provider and review the applicable terms before use. See [data/README.md](data/README.md).

## Business questions

- Which vendors account for the largest share of purchasing activity?
- Which vendor/brand combinations have high purchase value but weak sales value?
- How do sales quantities compare with purchased quantities?
- Which products may need pricing, promotion, replenishment, or inventory review?
- How should vendor freight be handled without double-counting it across brands?

## Repository structure

```text
vendor-performance-analytics/
├── data/                 # Add the six source CSVs locally; excluded from Git
├── dashboard/            # Supplied Power BI report (.pbix)
├── database/             # Generated SQLite database; excluded from Git
├── logs/                 # Runtime logs; excluded from Git
├── notebooks/            # Supplied exploratory and performance notebooks
├── outputs/              # Generated analysis outputs; excluded by default
├── reports/              # Supplied PDF report
├── src/
│   ├── ingest_data.py    # Chunked CSV -> SQLite ingestion
│   └── vendor_analysis.py# Vendor/brand summary and derived metrics
├── requirements.txt
└── README.md
```

## Source data expected

Place these six files inside `data/`:

1. `purchases.csv`
2. `purchase_prices.csv`
3. `vendor_invoice.csv`
4. `begin_inventory.csv`
5. `end_inventory.csv`
6. `sales.csv`

The pipeline currently uses `purchases.csv`, `purchase_prices.csv`, `sales.csv`, and `vendor_invoice.csv` to build the vendor/brand summary. The inventory snapshots are retained as inputs for future inventory-aging and stock-reconciliation extensions.

## Quick start

### 1. Create an environment

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Add the source CSV files

Copy the six CSV files into `data/`. Do not commit them unless their license explicitly permits public redistribution.

### 3. Ingest into SQLite

```bash
python src/ingest_data.py --data-dir data --db database/inventory.db
```

CSV files are read in chunks (100,000 rows by default) to reduce peak memory use. Change the chunk size with `--chunksize` if required.

### 4. Build the vendor/brand analysis

```bash
python src/vendor_analysis.py --db database/inventory.db --output outputs/vendor_brand_performance.csv
```

### 5. Explore the supplied artifacts

- `notebooks/exploratory_data_analysis.ipynb`
- `notebooks/vendor_performance_analysis.ipynb`
- `reports/vendor_performance_report.pdf`
- `dashboard/vendor_performance.pbix` (open with Microsoft Power BI Desktop)

The notebooks, PDF, and PBIX are supplied project artifacts. Their historical results should be treated as the original analysis, not as proof that the new scripts have reproduced every reported figure. Re-run the pipeline against the source data and reconcile results before using them for business decisions.

## Metric definitions and interpretation

| Metric | Definition | Interpretation caution |
|---|---|---|
| Gross profit before freight | Sales dollars − purchase dollars | Excludes operating expenses, tax treatment, discounts, returns, and freight allocation unless explicitly modeled. It is not net profit. |
| Gross margin before freight | Gross profit before freight ÷ sales dollars × 100 | Undefined when sales dollars are zero; the pipeline returns null rather than infinity. |
| Sales-to-purchase value ratio | Sales dollars ÷ purchase dollars | A descriptive ratio, not an accounting profit measure. Timing and opening stock can affect it. |
| Sell-through quantity ratio | Sales quantity ÷ purchased quantity | Can exceed 1 when opening inventory or prior-period stock contributes to sales. |
| Vendor total freight | Sum of freight by vendor | Vendor-level freight is not copied as an additive brand-level allocation. Allocate it using an explicit, documented rule before brand-level profitability comparisons. |

## Data quality and modeling decisions

- Join purchase and price reference data on **both vendor number and brand** to reduce accidental many-to-many matches.
- Aggregate purchase, sales, and freight independently before joining to avoid row multiplication.
- Keep zero-sales margin as null; do not replace an undefined ratio with infinity or an arbitrary zero.
- Vendor freight is vendor-grain data. The pipeline labels it `VendorTotalFreight` and warns against summing it over brand rows.
- The current gross-profit proxy excludes freight and other costs; do not describe it as net profit.
- Validate key uniqueness, date ranges, duplicate records, returns/negative quantities, and source-data coverage before production use.

## Historical report: findings to revalidate

The supplied PDF reports, among other findings, a 65.69% purchase contribution from the top 10 vendors, 198 brands in a lower-sales/higher-margin segment, and approximately $2.71M of unsold inventory capital. These are **reported historical results** from the supplied artifact; re-compute and verify them from the original raw files before citing them externally. The PDF also notes negative/infinite margin values and very large freight variation, which warrant careful denominator and aggregation checks.

## Reproducibility and limitations

- Python 3.10+ is recommended.
- SQLite is used for local, portable analysis; no cloud database is required.
- The ingestion script is chunked, but SQLite writes can still take time for multi-million-row CSVs.
- The provided PBIX may contain embedded imported data. Review its contents and data permissions before making this public repository visible.
- No license is declared for the underlying data or supplied third-party artifacts. Add a license only after confirming you have the rights to do so.

## Next analytical extensions

- Allocate vendor freight to brands using purchase-dollar or quantity weights and compare both approaches.
- Reconcile opening inventory + receipts − sales against ending inventory.
- Add time-aware vendor scorecards (fill rate, lead time, on-time payment, purchase concentration).
- Add unit tests for join cardinality, denominator handling, and reconciliation checks.

## Author

Prepared as a portfolio project. Update this section with your preferred public profile links before sharing widely.
