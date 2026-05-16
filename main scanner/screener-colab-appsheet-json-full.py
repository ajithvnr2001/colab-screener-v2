#!/usr/bin/env python3
"""Compatibility launcher for the full JSON-only tracker."""

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
runpy.run_path(str(ROOT / "screener-colab-appsheet-json.py"), run_name="__main__")
