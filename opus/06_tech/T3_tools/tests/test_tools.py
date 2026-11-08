#!/usr/bin/env python3
import csv
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ledger  # noqa: E402
import yield_calc as yc  # noqa: E402


def write_csv(rows: list[dict]) -> Path:
    tmp = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="", encoding="utf-8")
    writer = csv.DictWriter(tmp, fieldnames=ledger.COLUMNS)
    writer.writeheader()
    for r in rows:
        writer.writerow({c: r.get(c, "") for c in ledger.COLUMNS})
    tmp.close()
    return Path(tmp.name)


class YieldCalcTests(unittest.TestCase):
    def test_monthly_equivalent_is_not_apy_over_12(self):
        m = yc.monthly_from_apy(0.12)
        self.assertAlmostEqual((1 + m) ** 12, 1.12, places=12)
        self.assertLess(m, 0.01)

    def test_apr_apy_roundtrip(self):
        apy = yc.apy_from_apr(0.05, 365)
        self.assertAlmostEqual(yc.apr_from_apy(apy, 365), 0.05, places=12)

    def test_csm_bond_curve(self):
        self.assertEqual(yc.csm_bond(0, 2.4, 1.3), 0.0)
        self.assertAlmostEqual(yc.csm_bond(1, 2.4, 1.3), 2.4)
        self.assertAlmostEqual(yc.csm_bond(10, 2.4, 1.3), 14.1)

    def test_v3_position_value_matches_capital_at_entry(self):
        x1, y1 = yc.v3_amounts(1.0, 2237, 2013, 2461)
        liq = 1000 / (x1 * 2237 + y1)
        x, y = yc.v3_amounts(liq, 2237, 2013, 2461)
        self.assertAlmostEqual(x * 2237 + y, 1000, places=6)

    def test_v3_out_of_range_holds_single_asset(self):
        x, y = yc.v3_amounts(10.0, 3000, 2013, 2461)
        self.assertEqual(x, 0.0)
        self.assertGreater(y, 0)
        x, y = yc.v3_amounts(10.0, 1500, 2013, 2461)
        self.assertGreater(x, 0)
        self.assertEqual(y, 0.0)

    def test_full_range_il_formula(self):
        r = 4.0
        self.assertAlmostEqual(2 * math.sqrt(r) / (1 + r) - 1, -0.2, places=12)


class LedgerTests(unittest.TestCase):
    def test_fifo_and_carryover(self):
        path = write_csv([
            {"date": "2026-01-01", "type": "buy", "asset": "ETH", "amount": "1", "price_usd": "1000",
             "source_of_funds": "x", "uah_rate": "40"},
            {"date": "2026-02-01", "type": "buy", "asset": "ETH", "amount": "1", "price_usd": "2000",
             "source_of_funds": "x", "uah_rate": "40"},
            {"date": "2026-03-01", "type": "swap", "asset": "ETH", "amount": "1", "price_usd": "3000",
             "to_asset": "USDC", "to_amount": "3000", "platform": "dex", "uah_rate": "40"},
            {"date": "2026-04-01", "type": "sell_fiat", "asset": "USDC", "amount": "3000", "price_usd": "1",
             "uah_rate": "40"},
        ])
        res = ledger.process(ledger.read_rows(path), "fmv")
        self.assertAlmostEqual(res["eco"].realized[2026], 2000.0)
        self.assertAlmostEqual(res["carry"].realized[2026], 2000.0)
        self.assertAlmostEqual(res["fiat_proceeds"][2026], 3000.0)
        eco_hold = res["eco"].holdings()
        self.assertAlmostEqual(eco_hold["ETH"][0], 1.0)
        self.assertAlmostEqual(eco_hold["ETH"][1], 2000.0)

    def test_swap_realizes_only_in_economic_book(self):
        path = write_csv([
            {"date": "2026-01-01", "type": "buy", "asset": "ETH", "amount": "1", "price_usd": "1000",
             "source_of_funds": "x", "uah_rate": "40"},
            {"date": "2026-03-01", "type": "swap", "asset": "ETH", "amount": "1", "price_usd": "3000",
             "to_asset": "USDC", "to_amount": "3000", "platform": "dex", "uah_rate": "40"},
        ])
        res = ledger.process(ledger.read_rows(path), "fmv")
        self.assertAlmostEqual(res["eco"].realized[2026], 2000.0)
        self.assertAlmostEqual(res["carry"].realized[2026], 0.0)
        self.assertAlmostEqual(res["carry"].holdings()["USDC"][1], 1000.0)

    def test_fee_in_asset_reduces_holdings(self):
        path = write_csv([
            {"date": "2026-01-01", "type": "buy", "asset": "ETH", "amount": "1", "price_usd": "1000",
             "source_of_funds": "x", "uah_rate": "40"},
            {"date": "2026-01-02", "type": "transfer", "asset": "ETH", "amount": "1", "fee_asset": "ETH",
             "fee_amount": "0.01", "fee_usd": "10", "tx_hash": "0x1"},
        ])
        res = ledger.process(ledger.read_rows(path), "fmv")
        amt, cost = res["eco"].holdings()["ETH"]
        self.assertAlmostEqual(amt, 0.99)
        self.assertAlmostEqual(cost, 990.0)
        self.assertAlmostEqual(res["eco"].realized[2026], -10.0)

    def test_oversell_produces_warning(self):
        path = write_csv([
            {"date": "2026-01-01", "type": "sell_fiat", "asset": "ETH", "amount": "1", "price_usd": "1000",
             "uah_rate": "40"},
        ])
        res = ledger.process(ledger.read_rows(path), "fmv")
        self.assertTrue(res["eco"].warnings)

    def test_validate_flags_missing_source(self):
        path = write_csv([
            {"date": "2026-01-01", "type": "buy", "asset": "ETH", "amount": "1", "price_usd": "1000",
             "uah_rate": "40"},
        ])
        problems = [p for r in ledger.read_rows(path) for p in ledger.validate_row(r)]
        self.assertTrue(any("source_of_funds" in p for p in problems))

    def test_example_file_is_consistent(self):
        example = Path(__file__).resolve().parents[1] / "ledger_example.csv"
        rows = ledger.read_rows(example)
        res = ledger.process(rows, "fmv")
        self.assertFalse(res["eco"].warnings)
        self.assertIn("WSTETH", res["eco"].holdings())


if __name__ == "__main__":
    unittest.main(verbosity=2)
