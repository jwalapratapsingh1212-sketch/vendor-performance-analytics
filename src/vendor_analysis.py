"""Build a vendor/brand performance table from SQLite source tables."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "database" / "inventory.db"
DEFAULT_OUT = ROOT / "outputs" / "vendor_brand_performance.csv"

SUMMARY_SQL = """
WITH purchase_summary AS (
    SELECT p.VendorNumber,
           MAX(TRIM(p.VendorName)) AS VendorName,
           p.Brand,
           MAX(TRIM(p.Description)) AS Description,
           SUM(COALESCE(p.Quantity, 0)) AS TotalPurchaseQuantity,
           SUM(COALESCE(p.Dollars, 0)) AS TotalPurchaseDollars,
           CASE WHEN SUM(COALESCE(p.Quantity, 0)) <> 0
                THEN SUM(COALESCE(p.PurchasePrice, 0) * COALESCE(p.Quantity, 0))
                     / SUM(COALESCE(p.Quantity, 0)) END AS WeightedPurchaseUnitCost
    FROM purchases p
    GROUP BY p.VendorNumber, p.Brand
),
price_summary AS (
    SELECT VendorNumber, Brand,
           MAX(Price) AS RetailUnitPrice,
           MAX(PurchasePrice) AS ListedPurchasePrice,
           MAX(Volume) AS Volume
    FROM purchase_prices
    GROUP BY VendorNumber, Brand
),
sales_summary AS (
    SELECT VendorNo AS VendorNumber, Brand,
           SUM(COALESCE(SalesQuantity, 0)) AS TotalSalesQuantity,
           SUM(COALESCE(SalesDollars, 0)) AS TotalSalesDollars,
           SUM(COALESCE(ExciseTax, 0)) AS TotalExciseTax
    FROM sales
    GROUP BY VendorNo, Brand
),
freight_summary AS (
    SELECT VendorNumber,
           SUM(COALESCE(Freight, 0)) AS VendorTotalFreight
    FROM vendor_invoice
    GROUP BY VendorNumber
)
SELECT ps.VendorNumber, ps.VendorName, ps.Brand, ps.Description,
       ps.TotalPurchaseQuantity, ps.TotalPurchaseDollars,
       ps.WeightedPurchaseUnitCost, pr.RetailUnitPrice,
       pr.ListedPurchasePrice, pr.Volume,
       COALESCE(ss.TotalSalesQuantity, 0) AS TotalSalesQuantity,
       COALESCE(ss.TotalSalesDollars, 0) AS TotalSalesDollars,
       COALESCE(ss.TotalExciseTax, 0) AS TotalExciseTax,
       COALESCE(fs.VendorTotalFreight, 0) AS VendorTotalFreight
FROM purchase_summary ps
LEFT JOIN price_summary pr
  ON ps.VendorNumber = pr.VendorNumber AND ps.Brand = pr.Brand
LEFT JOIN sales_summary ss
  ON ps.VendorNumber = ss.VendorNumber AND ps.Brand = ss.Brand
LEFT JOIN freight_summary fs
  ON ps.VendorNumber = fs.VendorNumber
ORDER BY ps.TotalPurchaseDollars DESC
"""


def build_summary(conn: sqlite3.Connection) -> pd.DataFrame:
    required = {"purchases", "purchase_prices", "sales", "vendor_invoice"}
    present = {
        row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    missing = sorted(required - present)
    if missing:
        raise RuntimeError(
            f"Database missing tables: {', '.join(missing)}. Run src/ingest_data.py first."
        )

    df = pd.read_sql_query(SUMMARY_SQL, conn)
    money_cols = ["TotalPurchaseDollars", "TotalSalesDollars", "VendorTotalFreight"]
    for column in money_cols:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    df["GrossProfitBeforeFreight"] = (
        df["TotalSalesDollars"] - df["TotalPurchaseDollars"]
    )
    df["GrossMarginPctBeforeFreight"] = np.where(
        df["TotalSalesDollars"] > 0,
        100 * df["GrossProfitBeforeFreight"] / df["TotalSalesDollars"],
        np.nan,
    )
    df["SalesToPurchaseValueRatio"] = np.where(
        df["TotalPurchaseDollars"] > 0,
        df["TotalSalesDollars"] / df["TotalPurchaseDollars"],
        np.nan,
    )
    df["SellThroughQtyRatio"] = np.where(
        df["TotalPurchaseQuantity"] > 0,
        df["TotalSalesQuantity"] / df["TotalPurchaseQuantity"],
        np.nan,
    )
    # Freight is vendor-grain data. Do not repeat it as additive brand-level freight.
    return df.replace([np.inf, -np.inf], np.nan)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    if not args.db.exists():
        raise FileNotFoundError(f"Database not found: {args.db}. Run src/ingest_data.py first.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(args.db) as conn:
        summary = build_summary(conn)
    summary.to_csv(args.output, index=False)
    print(f"Saved {len(summary):,} vendor-brand rows to {args.output}")


if __name__ == "__main__":
    main()
