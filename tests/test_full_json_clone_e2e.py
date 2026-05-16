from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from collections import defaultdict
from datetime import timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FULL_JSON_SCRIPT = ROOT / "screener-colab-appsheet-json.py"


_MISSING = object()


class FakeCell:
    def __init__(self, value=None):
        self.value = value
        self.fill = None
        self.font = None
        self.alignment = None
        self.border = None


class FakeWorksheet:
    def __init__(self, title: str):
        self.title = title
        self._cells: dict[tuple[int, int], FakeCell] = {}
        self.freeze_panes = None
        self.auto_filter = types.SimpleNamespace(ref=None)
        self.column_dimensions = defaultdict(types.SimpleNamespace)
        self.row_dimensions = defaultdict(types.SimpleNamespace)

    @property
    def max_row(self) -> int:
        return max((row for row, _ in self._cells), default=1)

    @property
    def max_column(self) -> int:
        return max((col for _, col in self._cells), default=1)

    def cell(self, row: int, column: int, value=_MISSING) -> FakeCell:
        key = (row, column)
        cell = self._cells.setdefault(key, FakeCell())
        if value is not _MISSING:
            cell.value = value
        return cell


class FakeWorkbook:
    def __init__(self):
        self._sheets: dict[str, FakeWorksheet] = {}
        self.active = self.create_sheet("Sheet")

    @property
    def sheetnames(self) -> list[str]:
        return list(self._sheets)

    def create_sheet(self, title: str) -> FakeWorksheet:
        ws = FakeWorksheet(title)
        self._sheets[title] = ws
        self.active = ws
        return ws

    def __getitem__(self, name: str) -> FakeWorksheet:
        return self._sheets[name]

    def __delitem__(self, name: str) -> None:
        del self._sheets[name]


class FakeStyle:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class FakeClientError(Exception):
    def __init__(self, code: str = "NoSuchKey"):
        self.response = {"Error": {"Code": code}}
        super().__init__(code)


def _get_column_letter(index: int) -> str:
    out = ""
    while index:
        index, rem = divmod(index - 1, 26)
        out = chr(65 + rem) + out
    return out or "A"


def _install_import_stubs():
    old_modules = {}
    names = [
        "boto3",
        "botocore",
        "botocore.client",
        "botocore.exceptions",
        "numpy",
        "openai",
        "openpyxl",
        "openpyxl.styles",
        "openpyxl.utils",
        "pandas",
        "pytz",
        "yfinance",
    ]
    for name in names:
        old_modules[name] = sys.modules.get(name)

    boto3 = types.ModuleType("boto3")
    boto3.client = lambda *args, **kwargs: None

    botocore = types.ModuleType("botocore")
    botocore_client = types.ModuleType("botocore.client")
    botocore_client.Config = FakeStyle
    botocore_exceptions = types.ModuleType("botocore.exceptions")
    botocore_exceptions.ClientError = FakeClientError

    np = types.ModuleType("numpy")
    np.integer = int
    np.floating = float
    np.nan = float("nan")

    openai = types.ModuleType("openai")
    openai.OpenAI = FakeStyle

    openpyxl = types.ModuleType("openpyxl")
    openpyxl.Workbook = FakeWorkbook
    openpyxl_styles = types.ModuleType("openpyxl.styles")
    for name in ("PatternFill", "Font", "Alignment", "Border", "Side"):
        setattr(openpyxl_styles, name, FakeStyle)
    openpyxl_utils = types.ModuleType("openpyxl.utils")
    openpyxl_utils.get_column_letter = _get_column_letter

    pandas = types.ModuleType("pandas")

    pytz = types.ModuleType("pytz")
    pytz.timezone = lambda _name: timezone(timedelta(hours=5, minutes=30))

    sys.modules.update(
        {
            "boto3": boto3,
            "botocore": botocore,
            "botocore.client": botocore_client,
            "botocore.exceptions": botocore_exceptions,
            "numpy": np,
            "openai": openai,
            "openpyxl": openpyxl,
            "openpyxl.styles": openpyxl_styles,
            "openpyxl.utils": openpyxl_utils,
            "pandas": pandas,
            "pytz": pytz,
            "yfinance": types.ModuleType("yfinance"),
        }
    )
    return old_modules


def _restore_import_stubs(old_modules) -> None:
    for name, old in old_modules.items():
        if old is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = old


def _load_full_json_module():
    old_modules = _install_import_stubs()
    module_name = "full_json_clone_under_test"
    try:
        spec = importlib.util.spec_from_file_location(module_name, FULL_JSON_SCRIPT)
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load full JSON script")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module, old_modules
    except Exception:
        _restore_import_stubs(old_modules)
        sys.modules.pop(module_name, None)
        raise


class FakeS3Client:
    def __init__(self):
        self.puts: list[dict[str, object]] = []
        self.copies: list[dict[str, object]] = []

    def head_object(self, **kwargs):
        return {"ContentLength": 0}

    def copy_object(self, **kwargs):
        self.copies.append(kwargs)
        return {}

    def put_object(self, **kwargs):
        self.puts.append(kwargs)
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    def generate_presigned_url(self, *args, **kwargs):
        return "https://example.test/download.json"


class FakeResponse:
    status_code = 200
    text = '{"ok": true}'

    def json(self):
        return {"ok": True}


class FakeRequests:
    def __init__(self):
        self.posts: list[dict[str, object]] = []

    def post(self, url, **kwargs):
        self.posts.append({"url": url, **kwargs})
        return FakeResponse()


def _make_workbook(module) -> FakeWorkbook:
    wb = FakeWorkbook()
    del wb["Sheet"]

    dash = wb.create_sheet("Dashboard")
    for ci, header in enumerate(module.DASHBOARD_HEADERS, 1):
        dash.cell(row=1, column=ci, value=header)
    values = {
        "Symbol": "NSE:ALPHA",
        "Name": "Alpha Industries",
        "Quick Action": "BUY",
        "Consensus Score": 8.5,
        "Signal": "BUY",
        "AI Decision": "BUY",
        "AI Conf%": 91,
    }
    for header, value in values.items():
        dash.cell(row=2, column=module.DC[header] + 1, value=value)

    scanner = wb.create_sheet("Variant-D-1")
    scanner.cell(row=1, column=1, value="Symbol")
    scanner.cell(row=1, column=2, value="Name")
    scanner.cell(row=2, column=1, value="NSE:ALPHA")
    scanner.cell(row=2, column=2, value="Alpha Industries")
    return wb


class FullJsonCloneE2ETest(unittest.TestCase):
    def test_full_clone_writes_json_uploads_json_and_sends_telegram_document(self) -> None:
        module, old_modules = _load_full_json_module()
        try:
            with tempfile.TemporaryDirectory() as temp:
                s3 = FakeS3Client()
                requests = FakeRequests()
                module._script_base_dir = lambda: temp
                module._s3 = lambda: s3
                module.requests = requests
                module.ensure_dashboard_sheet = lambda wb: wb["Dashboard"]

                wb = _make_workbook(module)
                self.assertTrue(module.s3_upload_excel(wb, backup=False))
                self.assertTrue(module.s3_upload_dashboard_excel(wb))
                rows, snapshot_path = module.append_dashboard_snapshot_to_db(
                    wb,
                    iteration=1,
                    snapshot_at="2026-05-15 12:00:00",
                )
                self.assertEqual(rows, 1)
                self.assertTrue(module.s3_upload_dashboard_db(snapshot_path))
                self.assertTrue(
                    module.tg_send_document(
                        os.path.join(temp, module.LOCAL_JSON_FILE),
                        "Full JSON test",
                    )
                )

                full_path = Path(temp) / "gas_stock_tracker.json"
                dash_path = Path(temp) / "gas_stock_tracker_dashboard.json"
                snapshots_path = Path(temp) / "dashboard_snapshots.json"
                self.assertTrue(full_path.exists())
                self.assertTrue(dash_path.exists())
                self.assertTrue(snapshots_path.exists())
                self.assertFalse(list(Path(temp).glob("*.xlsx")))
                self.assertFalse(list(Path(temp).glob("*.db")))

                full = json.loads(full_path.read_text(encoding="utf-8"))
                dashboard = json.loads(dash_path.read_text(encoding="utf-8"))
                snapshots = json.loads(snapshots_path.read_text(encoding="utf-8"))

                self.assertEqual(full["format_version"], "colab-screener-json-v1")
                self.assertIn("Dashboard", full["sheets"])
                self.assertIn("Variant-D-1", full["sheets"])
                self.assertEqual(dashboard["sheet_order"], ["Dashboard"])
                self.assertEqual(
                    dashboard["sheets"]["Dashboard"]["rows"][0]["Symbol"],
                    "NSE:ALPHA",
                )
                self.assertEqual(snapshots["format_version"], "colab-screener-dashboard-snapshots-json-v1")
                self.assertEqual(snapshots["snapshots"][0]["symbol"], "NSE:ALPHA")
                self.assertEqual(snapshots["snapshots"][0]["payload"]["Name"], "Alpha Industries")

                put_keys = [put["Key"] for put in s3.puts]
                self.assertIn("reports/gas_stock_tracker.json", put_keys)
                self.assertIn("reports/gas_stock_tracker_dashboard.json", put_keys)
                self.assertIn("reports/dashboard_snapshots.json", put_keys)
                self.assertTrue(all(put["ContentType"] == "application/json" for put in s3.puts))
                self.assertEqual(len(requests.posts), 1)
                self.assertTrue(str(requests.posts[0]["url"]).endswith("/sendDocument"))
                self.assertIn("document", requests.posts[0]["files"])
        finally:
            _restore_import_stubs(old_modules)
            sys.modules.pop("full_json_clone_under_test", None)


if __name__ == "__main__":
    unittest.main()
