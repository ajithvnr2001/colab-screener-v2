from __future__ import annotations

import py_compile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FULL_JSON_SCRIPT = ROOT / "screener-colab-appsheet-json.py"
FULL_JSON_LAUNCHER = ROOT / "main scanner" / "screener-colab-appsheet-json-full.py"


class FullJsonCloneStaticTest(unittest.TestCase):
    def test_full_json_clone_compiles_without_importing_dependencies(self) -> None:
        py_compile.compile(str(FULL_JSON_SCRIPT), doraise=True)
        py_compile.compile(str(FULL_JSON_LAUNCHER), doraise=True)

    def test_full_json_clone_uses_json_outputs(self) -> None:
        source = FULL_JSON_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('S3_JSON_KEY  = "reports/gas_stock_tracker.json"', source)
        self.assertIn('S3_DASHBOARD_JSON_KEY = "reports/gas_stock_tracker_dashboard.json"', source)
        self.assertIn('S3_DASHBOARD_DB_KEY = "reports/dashboard_snapshots.json"', source)
        self.assertIn('LOCAL_JSON_FILE = "gas_stock_tracker.json"', source)
        self.assertIn('LOCAL_DASHBOARD_JSON_FILE = "gas_stock_tracker_dashboard.json"', source)
        self.assertIn('DASHBOARD_DB_FILE         = "dashboard_snapshots.json"', source)
        self.assertIn('ContentType="application/json"', source)
        self.assertIn("def tg_send_document", source)
        self.assertIn("main(max_iterations=1)", source)
        self.assertNotIn("application/x-sqlite3", source)
        self.assertNotIn("dashboard_snapshots.db", source)
        self.assertNotIn("put_object(Bucket=S3_BUCKET, Key=S3_EXCEL_KEY, Body=data,\n                             ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\")", source)


if __name__ == "__main__":
    unittest.main()
