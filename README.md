# Vendor Performance & Retail Analytics

An end-to-end vendor analytics project using Python, SQL/SQLite, exploratory data analysis, statistical testing, and Power BI. The objective is to evaluate vendor contribution, purchasing efficiency, brand-level sales performance, inventory turnover, and working capital tied up in unsold stock.

## Project objectives

- Measure vendor-wise purchasing and sales contribution.
- Identify brands with low sales but comparatively high profit margins.
- Analyze vendor and brand performance using descriptive statistics and visualizations.
- Examine purchasing patterns, stock turnover, and unsold inventory value.
- Compare profit margins between higher- and lower-sales groups using statistical testing.
- Present business findings through a PDF report and Power BI dashboard.

## Repository structure

```text
vendor-performance-analytics/
├── data/                       # Place original source CSVs here locally
├── database/                   # SQLite database generated locally
├── dashboard/                  # Power BI dashboard artifact (pending upload)
├── notebooks/                  # Jupyter notebooks (pending upload)
├── reports/                    # PDF report (pending upload)
├── outputs/                    # Generated outputs
├── src/
│   ├── ingestion_db.py          # Load CSV files into SQLite
│   ├── get_vendor_summary.py    # Build and clean vendor summary
│   ├── ingest_data.py           # Chunked CSV-to-SQLite ingestion
│   └── vendor_analysis.py       # Vendor/brand performance metrics
├── tests/
├── requirements.txt
└── README.md
```

## Dataset files

The original project expects these source files under `data/`:

- `purchases.csv`
- `purchase_prices.csv`
- `vendor_invoice.csv`
- `begin_inventory.csv`
- `end_inventory.csv`
- `sales.csv`

The source data archive is not committed to this public repository. It is large, and redistribution rights have not been established. Obtain the files from their original provider and verify the license/terms before using or sharing them. Do not commit confidential or restricted data.

## Tools and technologies

- **Python:** pandas, NumPy, Matplotlib, Seaborn, SciPy
- **Database:** SQLite and SQL
- **Analysis:** Jupyter Notebook, descriptive statistics, correlation analysis, outlier analysis, hypothesis testing
- **Visualization:** Power BI, Matplotlib, Seaborn

## Setup

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Place the six CSV files inside `data/` before running the ingestion scripts.

### Original ingestion workflow

```bash
python src/ingestion_db.py
python src/get_vendor_summary.py
```

The original scripts use `inventory.db` in the project root and create a `vendor_sales_summary` table.

### Reproducible chunked workflow

```bash
python src/ingest_data.py --data-dir data --db database/inventory.db
python src/vendor_analysis.py --db database/inventory.db --output outputs/vendor_brand_performance.csv
python -m unittest discover -s tests -v
```

The chunked workflow uses bounded-memory CSV ingestion. Its output and metric definitions are documented in the relevant source modules.

## Analysis workflow

1. Load source CSV files into SQLite.
2. Inspect table structure, record counts, data types, missing values, and vendor-level records.
3. Aggregate purchases, sales, and freight to appropriate grains.
4. Build a vendor/brand summary for analysis.
5. Calculate gross profit, profit margin, stock turnover, and sales-to-purchase ratio.
6. Perform descriptive analysis, distributions, outlier checks, and correlation analysis.
7. Identify low-sales/high-margin brands and compare vendor performance.
8. Estimate unsold inventory value and examine vendor concentration.
9. Use statistical testing to compare profit margins across sales groups.
10. Communicate findings through the report and dashboard.

## Important metric caveats

- **Gross profit** in the original project is calculated as sales dollars minus purchase dollars. It is not net profit.
- **Profit margin** is undefined when sales dollars are zero. Avoid interpreting infinity or silently replacing undefined ratios with zero.
- **Stock turnover** in the original analysis is sales quantity divided by purchase quantity. It is a proxy and can be affected by opening stock and the analysis period.
- **Freight cost** is aggregated at vendor level. It must not be summed repeatedly across brand-level rows unless a documented allocation method is applied.
- The original purchase-price join uses brand as the join key. Validate whether vendor number should also be part of the key to avoid unintended duplicate matches.
- Recalculate historical figures from the source data before using them in a business decision or external presentation.

## Files from the supplied project archive

The uploaded source archive contains the following main project artifacts:

- `ingestion_db.py`
- `get_vendor_summary.py`
- `Exploratory Data Analysis.ipynb`
- `Vendor Performance Analysis.ipynb`
- `vendor_sales_summary.csv`
- `Vendor Performance Report.pdf`
- `vendor_performance.pbix`

The two Python source scripts have been added under `src/`. The notebooks, generated summary CSV, PDF report, and PBIX dashboard are **not yet present in this GitHub repository**. They should be uploaded after checking that the derived data and embedded dashboard data are appropriate for public release. macOS `__MACOSX` metadata files are not project deliverables and should be excluded.

## Limitations and future improvements

- Add data validation for duplicate keys, missing values, negative quantities, and date coverage.
- Validate join cardinality before merging vendor, brand, and price data.
- Allocate vendor freight to brands using a clearly documented method before comparing fully loaded profitability.
- Reconcile beginning inventory + purchases − sales with ending inventory.
- Add time-based vendor scorecards for purchase concentration, sales contribution, and stock movement.
- Re-run the full analysis and reconcile the notebook, PDF, dashboard, and Python pipeline outputs.

## Author

Jwala Pratap Singh
