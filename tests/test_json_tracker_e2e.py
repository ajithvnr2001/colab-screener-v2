from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "screener_json_tracker.py"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import screener_json_tracker


def make_bars(start: date, count: int, base: float, step: float) -> list[dict[str, float | int | str]]:
    bars = []
    current = start
    produced = 0
    while produced < count:
        if current.weekday() < 5:
            close = base + (produced * step)
            bars.append(
                {
                    "date": current.isoformat(),
                    "open": round(close - 0.4, 2),
                    "high": round(close + 1.1, 2),
                    "low": round(close - 1.0, 2),
                    "close": round(close, 2),
                    "volume": 1_000_000 + produced * 1000,
                }
            )
            produced += 1
        current += timedelta(days=1)
    return bars


class RecordingTelegramHandler(BaseHTTPRequestHandler):
    requests_seen: list[str] = []

    def do_POST(self) -> None:  # noqa: N802 - http.server API
        length = int(self.headers.get("content-length", "0"))
        self.rfile.read(length)
        self.__class__.requests_seen.append(self.path)
        body = b'{"ok": true, "result": {"message_id": 1}}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


class JsonTrackerE2ETest(unittest.TestCase):
    def setUp(self) -> None:
        RecordingTelegramHandler.requests_seen = []

    def test_tracker_writes_json_and_sends_to_telegram_each_iteration(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            source_path = temp_path / "source.json"
            output_dir = temp_path / "out"
            source = {
                "scanners": [
                    {
                        "id": "Variant-D-1",
                        "url": "https://example.test/scanner/daily",
                        "symbols": [
                            {"symbol": "ALPHA", "name": "Alpha Industries"},
                            {"symbol": "BETA", "name": "Beta Finance"},
                        ],
                    },
                    {
                        "id": "Variant-W-1",
                        "url": "https://example.test/scanner/weekly",
                        "symbols": [{"symbol": "ALPHA", "name": "Alpha Industries"}],
                    },
                ],
                "market_data": {
                    "ALPHA": make_bars(date(2025, 1, 1), 280, 100.0, 0.45),
                    "BETA": make_bars(date(2025, 1, 1), 280, 180.0, -0.08),
                },
            }
            source_path.write_text(json.dumps(source), encoding="utf-8")

            server = ThreadingHTTPServer(("127.0.0.1", 0), RecordingTelegramHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            api_base = f"http://127.0.0.1:{server.server_port}"
            try:
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--source-json",
                        str(source_path),
                        "--output-dir",
                        str(output_dir),
                        "--max-iterations",
                        "2",
                        "--sleep-sec",
                        "0",
                        "--no-yahoo",
                        "--telegram-api-base",
                        api_base,
                        "--telegram-bot-token",
                        "TEST_TOKEN",
                        "--telegram-chat-id",
                        "12345",
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=True,
                    timeout=30,
                )
            finally:
                server.shutdown()
                server.server_close()

            summary = json.loads(completed.stdout)
            self.assertEqual(len(summary["iterations"]), 2)
            self.assertTrue((output_dir / "gas_stock_tracker.json").exists())
            self.assertTrue((output_dir / "gas_stock_tracker_dashboard.json").exists())
            self.assertFalse(list(output_dir.glob("*.xlsx")))
            self.assertEqual(len(RecordingTelegramHandler.requests_seen), 6)
            self.assertEqual(RecordingTelegramHandler.requests_seen.count("/botTEST_TOKEN/sendDocument"), 4)
            self.assertEqual(RecordingTelegramHandler.requests_seen.count("/botTEST_TOKEN/sendMessage"), 2)

            full = json.loads((output_dir / "gas_stock_tracker.json").read_text(encoding="utf-8"))
            dashboard = json.loads((output_dir / "gas_stock_tracker_dashboard.json").read_text(encoding="utf-8"))
            self.assertEqual(full["format_version"], "json-tracker-v1")
            self.assertEqual(dashboard["format_version"], "json-tracker-v1")
            self.assertEqual(full["telegram"]["status"], "sent")
            self.assertEqual(dashboard["telegram"]["status"], "sent")
            self.assertEqual(full["validation"][-1]["Status"], "PASS")
            self.assertEqual(len(full["dashboard"]), 2)
            self.assertEqual(len(full["price_history"]), 6)
            self.assertEqual(len(full["dashboard_history"]), 4)
            self.assertEqual(list(full["dashboard"][0].keys()), full["schema"]["dashboard_columns"])
            for rows in full["scanners"].values():
                for row in rows:
                    self.assertEqual(len(row), 60)
                    self.assertIn("Screener Link", row)

    def test_programmatic_main_accepts_max_iterations_keyword(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "programmatic"
            old_env = {
                key: os.environ.get(key)
                for key in ("MAX_ITERATIONS", "SCREENER_OUTPUT_DIR", "SCREENER_SOURCE_JSON", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
            }
            try:
                os.environ.pop("MAX_ITERATIONS", None)
                os.environ.pop("SCREENER_SOURCE_JSON", None)
                os.environ.pop("TELEGRAM_BOT_TOKEN", None)
                os.environ.pop("TELEGRAM_CHAT_ID", None)
                os.environ["SCREENER_OUTPUT_DIR"] = str(output_dir)
                with contextlib.redirect_stdout(io.StringIO()):
                    summary = screener_json_tracker.main(max_iterations=1)
            finally:
                for key, value in old_env.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

            self.assertEqual(len(summary["iterations"]), 1)
            self.assertEqual(summary["iterations"][0]["validation_status"], "SKIP")
            self.assertTrue((output_dir / "gas_stock_tracker.json").exists())
            self.assertTrue((output_dir / "gas_stock_tracker_dashboard.json").exists())

    def test_copy_paste_colab_launcher_args_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "colab"
            old_argv = sys.argv[:]
            old_env = {
                key: os.environ.get(key)
                for key in ("MAX_ITERATIONS", "SCREENER_OUTPUT_DIR", "SCREENER_SOURCE_JSON", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
            }
            try:
                sys.argv = [
                    "colab_kernel_launcher.py",
                    "-f",
                    "/root/.local/share/jupyter/runtime/kernel-test.json",
                ]
                os.environ["MAX_ITERATIONS"] = "1"
                os.environ["SCREENER_OUTPUT_DIR"] = str(output_dir)
                os.environ.pop("SCREENER_SOURCE_JSON", None)
                os.environ.pop("TELEGRAM_BOT_TOKEN", None)
                os.environ.pop("TELEGRAM_CHAT_ID", None)
                with contextlib.redirect_stdout(io.StringIO()):
                    summary = screener_json_tracker.main()
            finally:
                sys.argv = old_argv
                for key, value in old_env.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

            self.assertEqual(len(summary["iterations"]), 1)
            self.assertEqual(summary["iterations"][0]["validation_status"], "SKIP")
            self.assertTrue((output_dir / "gas_stock_tracker.json").exists())


if __name__ == "__main__":
    unittest.main()
