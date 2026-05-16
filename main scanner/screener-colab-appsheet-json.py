#!/usr/bin/env python3
"""Compatibility entrypoint for the JSON tracker."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener_json_tracker import main


if __name__ == "__main__":
    main()
    # main(max_iterations=1)
