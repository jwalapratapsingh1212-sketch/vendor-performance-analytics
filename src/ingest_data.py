"""Load the project's CSV files into SQLite using bounded-memory chunks."""
from __future__ import annotations

import argparse
import logging
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data"
DEFAULT_DB = ROOT / "database" / "inventory.db"
EXPECTED_TABLES = {
    "purchases.csv", "purchase_prices.csv", "vendor_invoice.csv",
    "begin_inventory.csv", "end_inventory.csv", "sales.csv",
}


def safe_table_name(filename: str) -> str:
    return Path(filename).stem.lower().replace("-", "_")


def ingest_csv(path: Path, conn: sqlite3.Connection, chunksize: int = 100_000) -> int:
    table = safe_table_name(path.name)
    first = True
    rows = 0
    for chunk in pd.read_csv(path, chunksize=chunksize, low_memory=False):
        chunk.columns = [str(column).strip() for column in chunk.columns]
        chunk.to_sql(table, conn, if_exists="replace" if first else "append", index=False)
        first = False
        rows += len(chunk)
    if first:
        raise ValueError(f"No rows found in {path}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--chunksize", type=int, default=100_000)
    args = parser.parse_args()
    if args.chunksize < 1:
        parser.error("--chunksize must be positive")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    missing = sorted(name for name in EXPECTED_TABLES if not (args.data_dir / name).is_file())
    if missing:
        raise FileNotFoundError(
            f"Missing expected CSV files in {args.data_dir}: {', '.join(missing)}"
        )

    args.db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(args.db) as conn:
        for filename in sorted(EXPECTED_TABLES):
            count = ingest_csv(args.data_dir / filename, conn, args.chunksize)
            logging.info("Loaded %-22s %s rows", filename, f"{count:,}")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_purchases_vendor_brand ON purchases(VendorNumber, Brand)",
            "CREATE INDEX IF NOT EXISTS idx_sales_vendor_brand ON sales(VendorNo, Brand)",
            "CREATE INDEX IF NOT EXISTS idx_prices_vendor_brand ON purchase_prices(VendorNumber, Brand)",
            "CREATE INDEX IF NOT EXISTS idx_invoice_vendor ON vendor_invoice(VendorNumber)",
        ]
        for statement in indexes:
            conn.execute(statement)
        conn.commit()
    logging.info("Database ready: %s", args.db)


if __name__ == "__main__":
    main()
