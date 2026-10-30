"""Regression tests for metric denominator handling."""
import sqlite3
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vendor_analysis import build_summary  # noqa: E402


class VendorAnalysisTests(unittest.TestCase):
    def test_zero_sales_produces_null_margin(self):
        conn = sqlite3.connect(":memory:")
        conn.executescript("""
        CREATE TABLE purchases (VendorNumber INTEGER, VendorName TEXT, Brand INTEGER,
            Description TEXT, Quantity REAL, Dollars REAL, PurchasePrice REAL);
        CREATE TABLE purchase_prices (VendorNumber INTEGER, Brand INTEGER, Price REAL,
            PurchasePrice REAL, Volume REAL);
        CREATE TABLE sales (VendorNo INTEGER, Brand INTEGER, SalesQuantity REAL,
            SalesDollars REAL, ExciseTax REAL);
        CREATE TABLE vendor_invoice (VendorNumber INTEGER, Freight REAL);
        INSERT INTO purchases VALUES (10, 'Vendor A', 100, 'Product A', 5, 50, 10);
        INSERT INTO purchase_prices VALUES (10, 100, 15, 10, 750);
        INSERT INTO sales VALUES (10, 100, 0, 0, 0);
        INSERT INTO vendor_invoice VALUES (10, 4);
        """)
        try:
            result = build_summary(conn)
            self.assertEqual(len(result), 1)
            self.assertTrue(
                result.loc[0, "GrossMarginPctBeforeFreight"]
                != result.loc[0, "GrossMarginPctBeforeFreight"]
            )
            self.assertEqual(result.loc[0, "VendorTotalFreight"], 4)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
