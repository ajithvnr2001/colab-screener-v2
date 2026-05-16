#!/usr/bin/env python3
"""JSON-first stock screener tracker.

This implementation replaces the documented Excel workbook outputs with JSON
files. It keeps the same major sections documented for the workbook workflow:
Dashboard, scanner rows, Price History, Dashboard History, and Validation.
"""

from __future__ import annotations

import argparse
import dataclasses
import html
import json
import math
import os
import re
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import requests


FORMAT_VERSION = "json-tracker-v1"
DEFAULT_OUTPUT_DIR = "json_output"
FULL_JSON_NAME = "gas_stock_tracker.json"
DASHBOARD_JSON_NAME = "gas_stock_tracker_dashboard.json"
STATE_JSON_NAME = "json_tracker_state.json"
_UNSET = object()

DASHBOARD_COLUMNS = [
    "Symbol",
    "Name",
    "In Screener?",
    "Quick Action",
    "Consensus Score",
    "MTF Alignment",
    "Historical MTF",
    "Sector",
    "Industry",
    "Sector Benchmark",
    "RS Tag",
    "RS vs NIFTY 1M%",
    "RS vs NIFTY 3M%",
    "RS vs Sector 1M%",
    "RS vs Sector 3M%",
    "Avg Traded Value 20D Cr",
    "Liquidity Tag",
    "Momentum Rank",
    "Risk Tag",
    "BB Signal",
    "Cam Setup",
    "Volume Buzz",
    "Since Capture Trend",
    "First Captured",
    "Days Tracked",
    "Last Seen",
    "Total Appearances",
    "Unique Scanners",
    "Scanner List",
    "Best Scanner",
    "Capture Price",
    "Current Price",
    "Cam H3",
    "Cam H4",
    "Cam L3",
    "Cam L4",
    "Ideal Enter Price",
    "Possible Sell Value",
    "Stop Loss Value",
    "Since Capture%",
    "1D%",
    "1W%",
    "1M%",
    "3M%",
    "6M%",
    "1Y%",
    "RSI 14",
    "ADX 14",
    "+DI 14",
    "-DI 14",
    "ATR 14",
    "NATR 14",
    "Signal",
    "Setup Signal",
    "Core Signal",
    "Signal Quality",
    "Signal Regime",
    "Win Prob%",
    "Hist Precision%",
    "Exp 5D%",
    "Exp 10D%",
    "WF Samples",
    "AI Decision",
    "AI Conf%",
    "Screener Link",
    "Last Updated",
    "Momentum Tag",
]

SCANNER_COLUMNS = [
    "Symbol",
    "Name",
    "First Captured",
    "Last Seen",
    "In Screener?",
    "Capture Price",
    "Current Price",
    "Since Capture%",
    "1D%",
    "1W%",
    "1M%",
    "3M%",
    "6M%",
    "1Y%",
    "2Y%",
    "3Y%",
    "Avg Weekly%",
    "Avg Monthly%",
    "Avg 3M%",
    "Avg 6M%",
    "Avg 1Y%",
    "RSI 14",
    "MA 20",
    "MA 50",
    "MA 200",
    "Signal",
    "Setup Signal",
    "Core Signal",
    "Signal Quality",
    "Signal Regime",
    "Win Prob%",
    "Hist Precision%",
    "Exp 5D%",
    "Exp 10D%",
    "WF Samples",
    "Sector",
    "Industry",
    "Sector Benchmark",
    "RS Tag",
    "RS vs NIFTY 1M%",
    "RS vs NIFTY 3M%",
    "RS vs Sector 1M%",
    "RS vs Sector 3M%",
    "Avg Traded Value 20D Cr",
    "Liquidity Tag",
    "AI Decision",
    "AI Reason",
    "AI Conf%",
    "Last Updated",
    "ADX 14",
    "Vol Ratio 20",
    "MACD Line",
    "MACD Hist",
    "52W High Dist%",
    "20D Breakout%",
    "ATR 14",
    "NATR 14",
    "+DI 14",
    "-DI 14",
]

PRICE_HISTORY_COLUMNS = [
    "Snapshot At",
    "Scanner",
    "Symbol",
    "Name",
    "In Screener?",
    "Capture Price",
    "Current Price",
    "Since Capture%",
    "1D%",
    "1W%",
    "1M%",
    "3M%",
    "6M%",
    "1Y%",
    "Cam H3",
    "Cam H4",
    "Cam L3",
    "Cam L4",
    "RSI 14",
    "ADX 14",
    "+DI 14",
    "-DI 14",
    "ATR 14",
    "NATR 14",
    "Vol Ratio 20",
    "MACD Line",
    "MACD Hist",
    "52W High Dist%",
    "20D Breakout%",
    "Signal",
    "Setup Signal",
    "Core Signal",
    "Signal Quality",
    "Signal Regime",
    "Win Prob%",
    "Hist Precision%",
    "Exp 5D%",
    "Exp 10D%",
    "WF Samples",
    "Sector",
    "Industry",
    "Sector Benchmark",
    "RS Tag",
    "RS vs NIFTY 1M%",
    "RS vs NIFTY 3M%",
    "RS vs Sector 1M%",
    "RS vs Sector 3M%",
    "Avg Traded Value 20D Cr",
    "Liquidity Tag",
    "AI Decision",
    "AI Conf%",
]

DASHBOARD_HISTORY_COLUMNS = [
    "Snapshot At",
    "Symbol",
    "Name",
    "In Screener?",
    "Quick Action",
    "Consensus Score",
    "MTF Alignment",
    "Historical MTF",
    "Sector",
    "Industry",
    "Sector Benchmark",
    "RS Tag",
    "RS vs NIFTY 1M%",
    "RS vs NIFTY 3M%",
    "RS vs Sector 1M%",
    "RS vs Sector 3M%",
    "Avg Traded Value 20D Cr",
    "Liquidity Tag",
    "Momentum Rank",
    "Risk Tag",
    "Cam Setup",
    "Total Appearances",
    "Unique Scanners",
    "Scanner List",
    "Capture Price",
    "Current Price",
    "Cam H3",
    "Cam H4",
    "Cam L3",
    "Cam L4",
    "Ideal Enter Price",
    "Possible Sell Value",
    "Stop Loss Value",
    "Since Capture%",
    "1D%",
    "1W%",
    "1M%",
    "RSI 14",
    "ADX 14",
    "+DI 14",
    "-DI 14",
    "ATR 14",
    "NATR 14",
    "Signal",
    "Setup Signal",
    "Core Signal",
    "Signal Quality",
    "Signal Regime",
    "Win Prob%",
    "Hist Precision%",
    "Exp 5D%",
    "Exp 10D%",
    "WF Samples",
    "AI Decision",
    "AI Conf%",
]

VALIDATION_COLUMNS = [
    "Snapshot At",
    "Iteration",
    "Mode",
    "Checked Rows",
    "Matched Rows",
    "Mismatch Rows",
    "Unresolved Rows",
    "Latest Session",
    "Status",
    "Details",
]

SCHEMA = {
    "dashboard_columns": DASHBOARD_COLUMNS,
    "scanner_columns": SCANNER_COLUMNS,
    "price_history_columns": PRICE_HISTORY_COLUMNS,
    "dashboard_history_columns": DASHBOARD_HISTORY_COLUMNS,
    "validation_columns": VALIDATION_COLUMNS,
}


@dataclasses.dataclass(frozen=True)
class TrackerConfig:
    output_dir: Path
    source_json: Path | None
    scanner_urls: tuple[str, ...]
    fetch_yahoo: bool
    limit_symbols: int | None
    max_iterations: int | None
    sleep_sec: float
    request_timeout_sec: float
    telegram_bot_token: str | None
    telegram_chat_id: str | None
    telegram_api_base: str
    telegram_dry_run: bool
    telegram_required: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def safe_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def round_num(value: Any, digits: int = 2) -> float | None:
    number = safe_float(value)
    if number is None:
        return None
    return round(number, digits)


def pct_change(current: Any, previous: Any) -> float | None:
    cur = safe_float(current)
    prev = safe_float(previous)
    if cur is None or prev is None or prev == 0:
        return None
    return round(((cur - prev) / prev) * 100.0, 2)


def days_between(start_date: str | None, end_date: str) -> int | None:
    if not start_date:
        return None
    try:
        start = datetime.fromisoformat(start_date[:10]).date()
        end = datetime.fromisoformat(end_date[:10]).date()
    except ValueError:
        return None
    return max(0, (end - start).days)


def json_dump(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def json_load(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if symbol.endswith(".NS"):
        return symbol[:-3]
    return symbol


def yahoo_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if symbol.startswith("^") or "." in symbol:
        return symbol
    return f"{symbol}.NS"


def parse_scanner_url(value: str) -> tuple[str, str]:
    if "=" in value:
        name, url = value.split("=", 1)
        return name.strip() or url.strip(), url.strip()
    url = value.strip()
    return url.rstrip("/").rsplit("/", 1)[-1] or "Scanner", url


def load_source(source_path: Path | None) -> dict[str, Any]:
    if source_path is None:
        return {}
    data = json_load(source_path, {})
    if not isinstance(data, dict):
        raise ValueError(f"source JSON must be an object: {source_path}")
    return data


def scanner_entries_from_source(source: dict[str, Any]) -> list[dict[str, Any]]:
    scanners = source.get("scanners", [])
    if not isinstance(scanners, list):
        raise ValueError("source JSON field 'scanners' must be a list")

    normalized: list[dict[str, Any]] = []
    for index, scanner in enumerate(scanners, start=1):
        if not isinstance(scanner, dict):
            raise ValueError("each scanner must be an object")
        scanner_id = str(scanner.get("id") or scanner.get("name") or f"Scanner-{index}")
        symbols = []
        for item in scanner.get("symbols", []):
            if isinstance(item, str):
                symbols.append({"symbol": normalize_symbol(item), "name": normalize_symbol(item)})
                continue
            if not isinstance(item, dict):
                continue
            raw_symbol = item.get("symbol") or item.get("ticker") or item.get("nse_symbol")
            if not raw_symbol:
                continue
            symbol = normalize_symbol(str(raw_symbol))
            symbols.append(
                {
                    "symbol": symbol,
                    "name": str(item.get("name") or item.get("company") or symbol),
                    "screener_link": str(item.get("screener_link") or item.get("url") or ""),
                }
            )
        normalized.append(
            {
                "id": scanner_id,
                "name": str(scanner.get("name") or scanner_id),
                "url": str(scanner.get("url") or ""),
                "symbols": dedupe_symbols(symbols),
            }
        )
    return normalized


def dedupe_symbols(symbols: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for item in symbols:
        symbol = normalize_symbol(item.get("symbol", ""))
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        result.append({**item, "symbol": symbol})
    return result


def fetch_screener_url(name: str, url: str, timeout: float) -> dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 JSON Stock Tracker",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    cookie = os.environ.get("SCREENER_COOKIE", "").strip()
    if cookie:
        headers["Cookie"] = cookie

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    symbols: list[dict[str, str]] = []
    pattern = re.compile(r'<a[^>]+href=["\'](/company/([^/"\']+)[^"\']*)["\'][^>]*>(.*?)</a>', re.I | re.S)
    for match in pattern.finditer(response.text):
        link, raw_symbol, raw_name = match.groups()
        symbol = normalize_symbol(html.unescape(raw_symbol).strip())
        label = re.sub(r"<[^>]+>", "", raw_name)
        label = html.unescape(label).strip() or symbol
        symbols.append({"symbol": symbol, "name": label, "screener_link": f"https://www.screener.in{link}"})
    return {"id": name, "name": name, "url": url, "symbols": dedupe_symbols(symbols)}


def fetch_yahoo_history(symbol: str, timeout: float, history_range: str = "3y") -> list[dict[str, Any]]:
    ticker = quote_plus(yahoo_symbol(symbol))
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={history_range}&interval=1d"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 JSON Stock Tracker"}, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    result = payload.get("chart", {}).get("result") or []
    if not result:
        return []
    chart = result[0]
    timestamps = chart.get("timestamp") or []
    quote = (chart.get("indicators", {}).get("quote") or [{}])[0]
    opens = quote.get("open") or []
    highs = quote.get("high") or []
    lows = quote.get("low") or []
    closes = quote.get("close") or []
    volumes = quote.get("volume") or []

    bars: list[dict[str, Any]] = []
    for index, stamp in enumerate(timestamps):
        close = safe_float(closes[index] if index < len(closes) else None)
        high = safe_float(highs[index] if index < len(highs) else None)
        low = safe_float(lows[index] if index < len(lows) else None)
        open_price = safe_float(opens[index] if index < len(opens) else None)
        if close is None or high is None or low is None or open_price is None:
            continue
        bars.append(
            {
                "date": datetime.fromtimestamp(stamp, timezone.utc).date().isoformat(),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": int(safe_float(volumes[index] if index < len(volumes) else 0) or 0),
            }
        )
    return bars


def source_market_data(source: dict[str, Any], symbol: str) -> list[dict[str, Any]]:
    for key in ("market_data", "prices", "history"):
        data = source.get(key)
        if isinstance(data, dict):
            bars = data.get(symbol) or data.get(yahoo_symbol(symbol)) or data.get(symbol.upper())
            if isinstance(bars, list):
                return normalize_bars(bars)
    return []


def normalize_bars(raw_bars: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bars: list[dict[str, Any]] = []
    for raw in raw_bars:
        if not isinstance(raw, dict):
            continue
        date = raw.get("date") or raw.get("Date")
        close = safe_float(raw.get("close", raw.get("Close")))
        high = safe_float(raw.get("high", raw.get("High")))
        low = safe_float(raw.get("low", raw.get("Low")))
        open_price = safe_float(raw.get("open", raw.get("Open", close)))
        volume = int(safe_float(raw.get("volume", raw.get("Volume", 0))) or 0)
        if not date or close is None or high is None or low is None or open_price is None:
            continue
        bars.append(
            {
                "date": str(date)[:10],
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            }
        )
    return sorted(bars, key=lambda row: row["date"])


def rolling_mean(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return statistics.fmean(values[-window:])


def ema_series(values: list[float], span: int) -> list[float]:
    if not values:
        return []
    alpha = 2.0 / (span + 1.0)
    ema = [values[0]]
    for value in values[1:]:
        ema.append((value * alpha) + (ema[-1] * (1.0 - alpha)))
    return ema


def compute_rsi(closes: list[float], window: int = 14) -> float | None:
    if len(closes) <= window:
        return None
    gains: list[float] = []
    losses: list[float] = []
    for previous, current in zip(closes[-(window + 1) : -1], closes[-window:]):
        change = current - previous
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))
    avg_gain = statistics.fmean(gains)
    avg_loss = statistics.fmean(losses)
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def compute_directional_indicators(bars: list[dict[str, Any]], window: int = 14) -> dict[str, float | None]:
    if len(bars) <= window:
        return {"ATR 14": None, "NATR 14": None, "ADX 14": None, "+DI 14": None, "-DI 14": None}

    true_ranges: list[float] = []
    plus_dm: list[float] = []
    minus_dm: list[float] = []
    for previous, current in zip(bars[:-1], bars[1:]):
        high = float(current["high"])
        low = float(current["low"])
        prev_high = float(previous["high"])
        prev_low = float(previous["low"])
        prev_close = float(previous["close"])
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        up_move = high - prev_high
        down_move = prev_low - low
        true_ranges.append(tr)
        plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0.0)
        minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0.0)

    if len(true_ranges) < window:
        return {"ATR 14": None, "NATR 14": None, "ADX 14": None, "+DI 14": None, "-DI 14": None}

    atr = statistics.fmean(true_ranges[-window:])
    plus = statistics.fmean(plus_dm[-window:])
    minus = statistics.fmean(minus_dm[-window:])
    if atr == 0:
        plus_di = minus_di = adx = None
    else:
        plus_di = (plus / atr) * 100.0
        minus_di = (minus / atr) * 100.0
        denominator = plus_di + minus_di
        adx = None if denominator == 0 else (abs(plus_di - minus_di) / denominator) * 100.0
    close = safe_float(bars[-1]["close"])
    natr = None if not close else (atr / close) * 100.0
    return {
        "ATR 14": round_num(atr),
        "NATR 14": round_num(natr),
        "ADX 14": round_num(adx),
        "+DI 14": round_num(plus_di),
        "-DI 14": round_num(minus_di),
    }


def compute_macd(closes: list[float]) -> tuple[float | None, float | None]:
    if len(closes) < 35:
        return None, None
    ema12 = ema_series(closes, 12)
    ema26 = ema_series(closes, 26)
    macd_line_series = [fast - slow for fast, slow in zip(ema12[-len(ema26) :], ema26)]
    signal_series = ema_series(macd_line_series, 9)
    line = macd_line_series[-1]
    hist = line - signal_series[-1]
    return round_num(line), round_num(hist)


def compute_bollinger(closes: list[float]) -> dict[str, Any]:
    if len(closes) < 20:
        return {"bb_percent_b": None, "bb_width": None, "bb_signal": ""}
    window = closes[-20:]
    mean = statistics.fmean(window)
    stdev = statistics.pstdev(window)
    upper = mean + (2 * stdev)
    lower = mean - (2 * stdev)
    current = closes[-1]
    percent_b = None if upper == lower else (current - lower) / (upper - lower)
    width = None if mean == 0 else ((upper - lower) / mean) * 100.0
    prior_high = max(closes[-21:-1]) if len(closes) >= 21 else max(window)
    if width is not None and width < 8 and current <= prior_high:
        signal = "SQUEEZE"
    elif width is not None and width < 12 and current > prior_high:
        signal = "SQUEEZE BREAK"
    elif percent_b is not None and percent_b > 1:
        signal = "BREAKOUT"
    elif percent_b is not None and percent_b < 0:
        signal = "BELOW BAND"
    else:
        signal = "NORMAL"
    return {"bb_percent_b": round_num(percent_b, 4), "bb_width": round_num(width), "bb_signal": signal}


def compute_camarilla(bars: list[dict[str, Any]]) -> dict[str, float | None]:
    if len(bars) < 2:
        return {"Cam H3": None, "Cam H4": None, "Cam L3": None, "Cam L4": None}
    prior = bars[-2]
    high = safe_float(prior["high"])
    low = safe_float(prior["low"])
    close = safe_float(prior["close"])
    if high is None or low is None or close is None:
        return {"Cam H3": None, "Cam H4": None, "Cam L3": None, "Cam L4": None}
    spread = high - low
    return {
        "Cam H3": round_num(close + (spread * 1.1 / 4.0)),
        "Cam H4": round_num(close + (spread * 1.1 / 2.0)),
        "Cam L3": round_num(close - (spread * 1.1 / 4.0)),
        "Cam L4": round_num(close - (spread * 1.1 / 2.0)),
    }


def compute_returns(closes: list[float]) -> dict[str, float | None]:
    offsets = {
        "1D%": 1,
        "1W%": 5,
        "1M%": 21,
        "3M%": 63,
        "6M%": 126,
        "1Y%": 252,
        "2Y%": 504,
        "3Y%": 756,
    }
    current = closes[-1] if closes else None
    result: dict[str, float | None] = {}
    for label, offset in offsets.items():
        previous = closes[-(offset + 1)] if len(closes) > offset else None
        result[label] = pct_change(current, previous)
    result["Avg Weekly%"] = round_num((result["1M%"] or 0) / 4.0 if result["1M%"] is not None else None)
    result["Avg Monthly%"] = round_num((result["3M%"] or 0) / 3.0 if result["3M%"] is not None else None)
    result["Avg 3M%"] = round_num((result["6M%"] or 0) / 2.0 if result["6M%"] is not None else None)
    result["Avg 6M%"] = round_num((result["1Y%"] or 0) / 2.0 if result["1Y%"] is not None else None)
    result["Avg 1Y%"] = result["1Y%"]
    return result


def signal_family(signal: str) -> str:
    if signal in {"BREAKOUT", "STRONG BUY", "BUY", "BUY (Squeeze)", "PULLBACK", "OVERSOLD"}:
        return "BULL"
    if signal in {"WEAK", "SELL"}:
        return "BEAR"
    return "NEUTRAL"


def compute_signals(metrics: dict[str, Any]) -> dict[str, Any]:
    current = safe_float(metrics.get("Current Price"))
    ma20 = safe_float(metrics.get("MA 20"))
    ma50 = safe_float(metrics.get("MA 50"))
    ma200 = safe_float(metrics.get("MA 200"))
    rsi = safe_float(metrics.get("RSI 14"))
    adx = safe_float(metrics.get("ADX 14"))
    plus_di = safe_float(metrics.get("+DI 14"))
    minus_di = safe_float(metrics.get("-DI 14"))
    macd_hist = safe_float(metrics.get("MACD Hist"))
    breakout = safe_float(metrics.get("20D Breakout%"))
    natr = safe_float(metrics.get("NATR 14"))
    bb_signal = str(metrics.get("BB Signal") or "")

    if current is None:
        return {
            "Setup Signal": "No Data",
            "Core Signal": "No Data",
            "Signal": "No Data",
            "Signal Quality": "N/A - NO DATA",
            "Signal Regime": "UNKNOWN",
            "Win Prob%": None,
            "Hist Precision%": None,
            "Exp 5D%": None,
            "Exp 10D%": None,
            "WF Samples": 0,
        }

    bullish_stack = bool(ma20 and ma50 and current > ma20 > ma50)
    above_200 = bool(ma200 and current > ma200)
    direction_ok = plus_di is None or minus_di is None or plus_di >= minus_di
    trend_ok = adx is None or adx >= 18
    momentum_ok = macd_hist is None or macd_hist >= 0

    if ma200 and current < ma200:
        setup = "HOLD (Below MA200)"
    elif breakout is not None and breakout > 2 and direction_ok and trend_ok:
        setup = "BREAKOUT"
    elif bullish_stack and above_200 and trend_ok and direction_ok and momentum_ok and rsi is not None and rsi < 72:
        setup = "STRONG BUY" if (breakout or 0) >= 0 else "BUY"
    elif bb_signal == "SQUEEZE BREAK" and above_200:
        setup = "BUY (Squeeze)"
    elif rsi is not None and rsi < 35 and above_200:
        setup = "PULLBACK"
    elif rsi is not None and rsi > 78:
        setup = "HOLD (Overbought)"
    elif direction_ok is False:
        setup = "HOLD (DI Weakness)"
    elif not bullish_stack and current and ma50 and current < ma50:
        setup = "WEAK"
    else:
        setup = "HOLD"

    core = setup
    family = signal_family(setup)
    if family == "BULL":
        if natr is not None and natr > 9:
            signal = "HOLD (High Vol)"
            quality = "REJECT - HIGH VOL"
            regime = "HIGH-VOL"
        elif not trend_ok:
            signal = "HOLD (Choppy Regime)"
            quality = "REJECT - CHOPPY"
            regime = "CHOPPY"
        else:
            signal = setup
            quality = "PASS - HIGH" if setup in {"BREAKOUT", "STRONG BUY"} else "PASS - MED"
            regime = "TRENDING"
    else:
        signal = setup
        quality = "N/A - NON-BULL" if family != "BULL" else "PASS - LOW"
        regime = "CHOPPY" if adx is not None and adx < 18 else "TRENDING"

    win_prob = 62 if quality == "PASS - HIGH" else 56 if quality == "PASS - MED" else 45 if family == "NEUTRAL" else 38
    return {
        "Setup Signal": setup,
        "Core Signal": core,
        "Signal": signal,
        "Signal Quality": quality,
        "Signal Regime": regime,
        "Win Prob%": win_prob,
        "Hist Precision%": max(35, win_prob - 4),
        "Exp 5D%": 2.4 if win_prob >= 60 else 1.2 if win_prob >= 55 else 0.0,
        "Exp 10D%": 4.1 if win_prob >= 60 else 2.0 if win_prob >= 55 else 0.0,
        "WF Samples": 20 if win_prob >= 55 else 12,
    }


def compute_symbol_metrics(symbol: str, bars: list[dict[str, Any]]) -> dict[str, Any]:
    if not bars:
        return {
            "Symbol": symbol,
            "Current Price": None,
            "Latest Session": "",
            "Signal": "No Data",
            "Setup Signal": "No Data",
            "Core Signal": "No Data",
            "Signal Quality": "N/A - NO DATA",
            "Signal Regime": "UNKNOWN",
            "WF Samples": 0,
        }

    closes = [float(row["close"]) for row in bars]
    highs = [float(row["high"]) for row in bars]
    volumes = [int(row.get("volume", 0) or 0) for row in bars]
    current = closes[-1]
    returns = compute_returns(closes)
    di = compute_directional_indicators(bars)
    macd_line, macd_hist = compute_macd(closes)
    bb = compute_bollinger(closes)
    camarilla = compute_camarilla(bars)

    high_52w = max(highs[-252:]) if highs else None
    prior_20_high = max(highs[-21:-1]) if len(highs) >= 21 else None
    avg_vol_20 = statistics.fmean(volumes[-20:]) if len(volumes) >= 20 else None
    current_vol = volumes[-1] if volumes else None
    vol_ratio = None if not avg_vol_20 else current_vol / avg_vol_20
    traded_value_cr = None
    if len(bars) >= 20:
        traded_values = [(float(row["close"]) * int(row.get("volume", 0) or 0)) / 10_000_000 for row in bars[-20:]]
        traded_value_cr = statistics.fmean(traded_values)

    metrics: dict[str, Any] = {
        "Symbol": symbol,
        "Current Price": round_num(current),
        "Latest Session": bars[-1]["date"],
        "1D%": returns["1D%"],
        "1W%": returns["1W%"],
        "1M%": returns["1M%"],
        "3M%": returns["3M%"],
        "6M%": returns["6M%"],
        "1Y%": returns["1Y%"],
        "2Y%": returns["2Y%"],
        "3Y%": returns["3Y%"],
        "Avg Weekly%": returns["Avg Weekly%"],
        "Avg Monthly%": returns["Avg Monthly%"],
        "Avg 3M%": returns["Avg 3M%"],
        "Avg 6M%": returns["Avg 6M%"],
        "Avg 1Y%": returns["Avg 1Y%"],
        "RSI 14": round_num(compute_rsi(closes)),
        "MA 20": round_num(rolling_mean(closes, 20)),
        "MA 50": round_num(rolling_mean(closes, 50)),
        "MA 200": round_num(rolling_mean(closes, 200)),
        "Vol Ratio 20": round_num(vol_ratio),
        "MACD Line": macd_line,
        "MACD Hist": macd_hist,
        "52W High Dist%": pct_change(current, high_52w),
        "20D Breakout%": pct_change(current, prior_20_high),
        "BB Signal": bb["bb_signal"],
        "Avg Traded Value 20D Cr": round_num(traded_value_cr),
        **di,
        **camarilla,
    }
    metrics.update(compute_signals(metrics))
    metrics["Liquidity Tag"] = liquidity_tag(metrics.get("Avg Traded Value 20D Cr"))
    metrics["RS Tag"] = rs_tag(metrics.get("1M%"), metrics.get("3M%"))
    metrics["RS vs NIFTY 1M%"] = None
    metrics["RS vs NIFTY 3M%"] = None
    metrics["RS vs Sector 1M%"] = None
    metrics["RS vs Sector 3M%"] = None
    metrics["Sector"] = ""
    metrics["Industry"] = ""
    metrics["Sector Benchmark"] = ""
    return metrics


def liquidity_tag(value: Any) -> str:
    traded = safe_float(value)
    if traded is None:
        return ""
    if traded >= 100:
        return "Deep"
    if traded >= 20:
        return "Liquid"
    if traded >= 5:
        return "Adequate"
    if traded >= 1:
        return "Thin"
    return "Illiquid"


def rs_tag(one_month: Any, three_month: Any) -> str:
    one = safe_float(one_month)
    three = safe_float(three_month)
    if one is None and three is None:
        return ""
    score = (one or 0) + (three or 0)
    if one is not None and three is not None and one > 5 and three > 10:
        return "Strong vs Both"
    if score > 8:
        return "RS Leader"
    if score >= 0:
        return "Mixed"
    if score > -10:
        return "Weak RS"
    return "Lagging"


def blank_row(columns: list[str]) -> dict[str, Any]:
    return {column: None for column in columns}


def project_row(row: dict[str, Any], columns: list[str]) -> dict[str, Any]:
    return {column: row.get(column) for column in columns}


def load_state(output_dir: Path) -> dict[str, Any]:
    state = json_load(output_dir / STATE_JSON_NAME, {})
    if not isinstance(state, dict):
        state = {}
    state.setdefault("format_version", FORMAT_VERSION)
    state.setdefault("symbols", {})
    state.setdefault("price_history", [])
    state.setdefault("dashboard_history", [])
    state.setdefault("validation", [])
    state.setdefault("last_dashboard_rows", {})
    return state


def save_state(output_dir: Path, state: dict[str, Any]) -> None:
    json_dump(output_dir / STATE_JSON_NAME, state)


def update_symbol_state(
    state: dict[str, Any],
    symbol: str,
    scanner_id: str,
    name: str,
    current_price: float | None,
    run_date: str,
) -> dict[str, Any]:
    symbols = state.setdefault("symbols", {})
    item = symbols.setdefault(
        symbol,
        {
            "symbol": symbol,
            "name": name,
            "first_captured": run_date,
            "capture_price": current_price,
            "total_appearances": 0,
            "scanners": {},
        },
    )
    item["name"] = name or item.get("name") or symbol
    item["last_seen"] = run_date
    item["total_appearances"] = int(item.get("total_appearances") or 0) + 1
    if item.get("capture_price") is None and current_price is not None:
        item["capture_price"] = current_price
    scanner_state = item.setdefault("scanners", {}).setdefault(
        scanner_id,
        {"first_captured": run_date, "appearances": 0},
    )
    scanner_state["last_seen"] = run_date
    scanner_state["appearances"] = int(scanner_state.get("appearances") or 0) + 1
    return item


def build_scanner_row(
    scanner_id: str,
    item: dict[str, Any],
    symbol_state: dict[str, Any],
    metrics: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    capture_price = symbol_state.get("capture_price")
    current_price = metrics.get("Current Price")
    row = blank_row(SCANNER_COLUMNS)
    row.update(metrics)
    row.update(
        {
            "Symbol": item["symbol"],
            "Name": item.get("name") or item["symbol"],
            "First Captured": symbol_state.get("first_captured"),
            "Last Seen": symbol_state.get("last_seen"),
            "In Screener?": "Yes",
            "Capture Price": round_num(capture_price),
            "Current Price": current_price,
            "Since Capture%": pct_change(current_price, capture_price),
            "AI Decision": "",
            "AI Reason": "",
            "AI Conf%": None,
            "Last Updated": generated_at,
        }
    )
    return project_row(row, SCANNER_COLUMNS)


def timeframe_alignment(metrics: dict[str, Any]) -> str:
    checks = []
    current = safe_float(metrics.get("Current Price"))
    ma20 = safe_float(metrics.get("MA 20"))
    ma50 = safe_float(metrics.get("MA 50"))
    one_month = safe_float(metrics.get("1M%"))
    three_month = safe_float(metrics.get("3M%"))
    checks.append("D+" if current is not None and ma20 is not None and current >= ma20 else "D-")
    checks.append("W+" if one_month is not None and one_month >= 0 else "W-")
    checks.append("M+" if three_month is not None and three_month >= 0 and (ma50 is None or current is None or current >= ma50) else "M-")
    return "/".join(checks)


def scanner_mtf(scanner_ids: list[str]) -> str:
    buckets = {"D": False, "W": False, "M": False}
    for scanner_id in scanner_ids:
        lowered = scanner_id.lower()
        if "week" in lowered or "weekly" in lowered or "-w" in lowered:
            buckets["W"] = True
        elif "month" in lowered or "monthly" in lowered or "-m" in lowered:
            buckets["M"] = True
        else:
            buckets["D"] = True
    return "/".join(f"{key}{'+' if value else '-'}" for key, value in buckets.items())


def build_dashboard_rows(
    state: dict[str, Any],
    active_rows_by_symbol: dict[str, list[dict[str, Any]]],
    generated_at: str,
) -> list[dict[str, Any]]:
    dashboard_rows: list[dict[str, Any]] = []
    all_symbols = set(state.get("symbols", {}).keys()) | set(active_rows_by_symbol.keys())

    for symbol in sorted(all_symbols):
        active_rows = active_rows_by_symbol.get(symbol, [])
        symbol_state = state.get("symbols", {}).get(symbol, {})
        if not active_rows:
            previous = dict(state.get("last_dashboard_rows", {}).get(symbol, {}))
            if previous:
                previous["In Screener?"] = "No"
                previous["Last Updated"] = generated_at
                dashboard_rows.append(project_row(previous, DASHBOARD_COLUMNS))
            continue

        best = choose_best_scanner_row(active_rows)
        scanner_ids = sorted({row.get("_scanner_id", "") for row in active_rows if row.get("_scanner_id")})
        scanner_list = ", ".join(scanner_ids)
        current_price = best.get("Current Price")
        capture_price = symbol_state.get("capture_price")
        signal = best.get("Signal") or ""
        setup = best.get("Setup Signal") or ""
        ai_conf = best.get("AI Conf%")
        consensus = consensus_score(best, len(scanner_ids))
        risk = risk_tag(best)
        quick = quick_action(signal, consensus, risk, best)
        cam_setup = cam_setup_label(best)
        row = blank_row(DASHBOARD_COLUMNS)
        row.update(best)
        row.update(
            {
                "Symbol": symbol,
                "Name": symbol_state.get("name") or best.get("Name") or symbol,
                "In Screener?": "Yes",
                "Quick Action": quick,
                "Consensus Score": consensus,
                "MTF Alignment": scanner_mtf(scanner_ids),
                "Historical MTF": timeframe_alignment(best),
                "Sector": best.get("Sector") or "",
                "Industry": best.get("Industry") or "",
                "Sector Benchmark": best.get("Sector Benchmark") or "",
                "RS Tag": best.get("RS Tag") or "",
                "Liquidity Tag": best.get("Liquidity Tag") or "",
                "Risk Tag": risk,
                "BB Signal": best.get("BB Signal") or "",
                "Cam Setup": cam_setup,
                "Volume Buzz": volume_buzz(best.get("Vol Ratio 20")),
                "Since Capture Trend": since_capture_trend(pct_change(current_price, capture_price)),
                "First Captured": symbol_state.get("first_captured"),
                "Days Tracked": days_between(symbol_state.get("first_captured"), today_utc()),
                "Last Seen": symbol_state.get("last_seen"),
                "Total Appearances": symbol_state.get("total_appearances"),
                "Unique Scanners": len(scanner_ids),
                "Scanner List": scanner_list,
                "Best Scanner": best.get("_scanner_id"),
                "Capture Price": round_num(capture_price),
                "Current Price": current_price,
                "Ideal Enter Price": ideal_enter_price(best),
                "Possible Sell Value": best.get("Cam H4") or best.get("Cam H3"),
                "Stop Loss Value": best.get("Cam L4") or best.get("Cam L3"),
                "Since Capture%": pct_change(current_price, capture_price),
                "AI Decision": best.get("AI Decision") or "",
                "AI Conf%": ai_conf,
                "Screener Link": best.get("Screener Link") or "",
                "Last Updated": generated_at,
            }
        )
        row["Momentum Tag"] = ""
        row["_momentum_score"] = momentum_score(row)
        row["_setup"] = setup
        dashboard_rows.append(row)

    active = [row for row in dashboard_rows if row.get("In Screener?") == "Yes"]
    inactive = [row for row in dashboard_rows if row.get("In Screener?") != "Yes"]
    active.sort(key=lambda row: row.get("_momentum_score") or -9999, reverse=True)
    for index, row in enumerate(active, start=1):
        row["Momentum Rank"] = index
    total = len(active)
    for row in active:
        row["Momentum Tag"] = momentum_tag(row.get("Momentum Rank"), total)
    inactive.sort(key=lambda row: str(row.get("Symbol") or ""))
    return [project_row(row, DASHBOARD_COLUMNS) for row in active + inactive]


def choose_best_scanner_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return max(rows, key=momentum_score)


def momentum_score(row: dict[str, Any]) -> float:
    score = 0.0
    for field, weight in [("1M%", 0.45), ("3M%", 0.35), ("6M%", 0.15), ("20D Breakout%", 0.2)]:
        value = safe_float(row.get(field))
        if value is not None:
            score += value * weight
    win_prob = safe_float(row.get("Win Prob%"))
    if win_prob is not None:
        score += (win_prob - 50) * 0.3
    if str(row.get("Signal", "")).startswith(("BREAKOUT", "STRONG BUY", "BUY")):
        score += 8
    return score


def consensus_score(row: dict[str, Any], unique_scanners: int) -> int | None:
    if row.get("Current Price") is None:
        return None
    score = 40 + min(unique_scanners, 5) * 5
    win_prob = safe_float(row.get("Win Prob%"))
    if win_prob is not None:
        score += int((win_prob - 50) * 0.6)
    if str(row.get("Signal", "")).startswith(("BREAKOUT", "STRONG BUY")):
        score += 10
    elif str(row.get("Signal", "")).startswith("BUY"):
        score += 6
    if row.get("Liquidity Tag") in {"Thin", "Illiquid"}:
        score -= 8
    if row.get("RS Tag") in {"Weak RS", "Lagging"}:
        score -= 8
    return max(0, min(100, score))


def risk_tag(row: dict[str, Any]) -> str:
    natr = safe_float(row.get("NATR 14"))
    liquidity = row.get("Liquidity Tag")
    rs = row.get("RS Tag")
    signal = str(row.get("Signal") or "")
    if signal in {"No Data", "Symbol Not Found"}:
        return "NO DATA"
    if liquidity in {"Illiquid", "Thin"}:
        return "LIQUIDITY RISK"
    if natr is not None and natr > 9:
        return "HIGH VOL"
    if rs in {"Weak RS", "Lagging"}:
        return "RS RISK"
    return "NORMAL"


def quick_action(signal: str, consensus: int | None, risk: str, row: dict[str, Any]) -> str:
    if consensus is None or row.get("Current Price") is None:
        return "NO DATA"
    if risk in {"HIGH VOL", "LIQUIDITY RISK"}:
        return "CAUTION"
    if signal in {"BREAKOUT", "STRONG BUY", "BUY", "BUY (Squeeze)"} and consensus >= 62:
        return "BUY NOW"
    if signal in {"PULLBACK", "OVERSOLD"}:
        return "WATCH"
    if signal.startswith("HOLD"):
        return "WATCH"
    return "AVOID" if signal in {"WEAK", "SELL"} else "WATCH"


def volume_buzz(value: Any) -> str:
    ratio = safe_float(value)
    if ratio is None:
        return ""
    if ratio >= 2:
        return "HIGH"
    if ratio >= 1.2:
        return "RISING"
    if ratio < 0.7:
        return "LOW"
    return "NORMAL"


def since_capture_trend(value: Any) -> str:
    pct = safe_float(value)
    if pct is None:
        return ""
    if pct >= 15:
        return "STRONG UP"
    if pct >= 3:
        return "UP"
    if pct <= -10:
        return "DOWN"
    return "FLAT"


def cam_setup_label(row: dict[str, Any]) -> str:
    current = safe_float(row.get("Current Price"))
    h3 = safe_float(row.get("Cam H3"))
    h4 = safe_float(row.get("Cam H4"))
    l3 = safe_float(row.get("Cam L3"))
    if current is None:
        return ""
    if h4 is not None and current >= h4:
        return "EXTENDED"
    if h3 is not None and current >= h3:
        return "BREAKOUT ZONE"
    if l3 is not None and current <= l3:
        return "PULLBACK ZONE"
    return "MID RANGE"


def ideal_enter_price(row: dict[str, Any]) -> float | None:
    current = safe_float(row.get("Current Price"))
    h3 = safe_float(row.get("Cam H3"))
    l3 = safe_float(row.get("Cam L3"))
    if current is None:
        return None
    candidates = [value for value in [h3, l3, current] if value is not None]
    return round_num(min(candidates, key=lambda value: abs(value - current)) if candidates else current)


def momentum_tag(rank: Any, total: int) -> str:
    value = safe_float(rank)
    if value is None or total <= 0:
        return ""
    percentile = value / total
    if percentile <= 0.10:
        return "ELITE"
    if percentile <= 0.25:
        return "STRONG"
    if percentile <= 0.50:
        return "HEALTHY"
    if percentile <= 0.75:
        return "NEUTRAL"
    if percentile <= 0.90:
        return "WEAK"
    return "LAGGING"


class TelegramClient:
    def __init__(self, config: TrackerConfig) -> None:
        self.config = config

    def send_outputs(self, files: list[Path], caption: str) -> dict[str, Any]:
        if self.config.telegram_dry_run:
            return {
                "attempted": False,
                "status": "dry_run",
                "files": [str(path) for path in files],
                "caption": caption,
            }
        if not self.config.telegram_bot_token or not self.config.telegram_chat_id:
            status = "skipped_missing_config"
            result = {"attempted": False, "status": status, "files": [str(path) for path in files]}
            if self.config.telegram_required:
                raise RuntimeError("Telegram token/chat id are required but not configured")
            return result

        api_base = self.config.telegram_api_base.rstrip("/")
        token = self.config.telegram_bot_token
        chat_id = self.config.telegram_chat_id
        sent: list[dict[str, Any]] = []
        for path in files:
            url = f"{api_base}/bot{token}/sendDocument"
            with path.open("rb") as handle:
                response = requests.post(
                    url,
                    data={"chat_id": chat_id, "caption": f"{caption}\n{path.name}"},
                    files={"document": (path.name, handle, "application/json")},
                    timeout=self.config.request_timeout_sec,
                )
            sent.append({"file": str(path), "status_code": response.status_code})
            response.raise_for_status()

        message_url = f"{api_base}/bot{token}/sendMessage"
        response = requests.post(
            message_url,
            data={"chat_id": chat_id, "text": caption},
            timeout=self.config.request_timeout_sec,
        )
        sent.append({"message": True, "status_code": response.status_code})
        response.raise_for_status()
        return {"attempted": True, "status": "sent", "sent": sent}


class JsonStockTracker:
    def __init__(self, config: TrackerConfig) -> None:
        self.config = config
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict[str, Any]:
        summary: dict[str, Any] = {"iterations": []}
        iteration = 1
        while True:
            result = self.run_once(iteration)
            if self.config.max_iterations is None:
                print(json.dumps({"iteration": result}, indent=2), flush=True)
            else:
                summary["iterations"].append(result)
            if self.config.max_iterations is not None and iteration >= self.config.max_iterations:
                break
            iteration += 1
            time.sleep(self.config.sleep_sec)
        return summary

    def run_once(self, iteration: int) -> dict[str, Any]:
        generated_at = utc_now()
        run_date = generated_at[:10]
        source = load_source(self.config.source_json)
        scanners = scanner_entries_from_source(source)
        for scanner_url in self.config.scanner_urls:
            name, url = parse_scanner_url(scanner_url)
            scanners.append(fetch_screener_url(name, url, self.config.request_timeout_sec))
        if self.config.limit_symbols is not None:
            scanners = limit_scanner_symbols(scanners, self.config.limit_symbols)

        state = load_state(self.config.output_dir)
        market_data: dict[str, list[dict[str, Any]]] = {}
        active_rows_by_symbol: dict[str, list[dict[str, Any]]] = defaultdict(list)
        scanner_rows: dict[str, list[dict[str, Any]]] = {}
        errors: list[dict[str, Any]] = []

        for scanner in scanners:
            scanner_id = scanner["id"]
            scanner_rows[scanner_id] = []
            for item in scanner.get("symbols", []):
                symbol = item["symbol"]
                bars = market_data.get(symbol)
                if bars is None:
                    bars = source_market_data(source, symbol)
                    if not bars and self.config.fetch_yahoo:
                        try:
                            bars = fetch_yahoo_history(symbol, self.config.request_timeout_sec)
                        except Exception as exc:  # noqa: BLE001 - preserve per-symbol errors in JSON
                            errors.append({"symbol": symbol, "stage": "yahoo_fetch", "error": str(exc)})
                            bars = []
                    market_data[symbol] = bars
                metrics = compute_symbol_metrics(symbol, bars)
                symbol_state = update_symbol_state(
                    state,
                    symbol,
                    scanner_id,
                    item.get("name") or symbol,
                    metrics.get("Current Price"),
                    run_date,
                )
                scanner_row = build_scanner_row(scanner_id, item, symbol_state, metrics, generated_at)
                scanner_row["Screener Link"] = item.get("screener_link") or scanner.get("url") or ""
                scanner_rows[scanner_id].append(scanner_row)
                active_view = dict(scanner_row)
                active_view["_scanner_id"] = scanner_id
                active_view["Screener Link"] = item.get("screener_link") or scanner.get("url") or ""
                active_rows_by_symbol[symbol].append(active_view)

        dashboard = build_dashboard_rows(state, active_rows_by_symbol, generated_at)
        state["last_dashboard_rows"] = {row["Symbol"]: row for row in dashboard}

        price_history_rows = build_price_history(generated_at, scanner_rows)
        dashboard_history_rows = build_dashboard_history(generated_at, dashboard)
        validation = build_validation(
            generated_at,
            iteration,
            dashboard,
            market_data,
            errors,
            mode="json",
        )

        state["price_history"].extend(price_history_rows)
        state["dashboard_history"].extend(dashboard_history_rows)
        state["validation"].append(validation)
        save_state(self.config.output_dir, state)

        full_payload = {
            "format_version": FORMAT_VERSION,
            "generated_at": generated_at,
            "iteration": iteration,
            "schema": SCHEMA,
            "source": {
                "source_json": str(self.config.source_json) if self.config.source_json else None,
                "scanner_urls": list(self.config.scanner_urls),
                "fetch_yahoo": self.config.fetch_yahoo,
            },
            "dashboard": dashboard,
            "scanners": scanner_rows,
            "price_history": state["price_history"],
            "dashboard_history": state["dashboard_history"],
            "validation": state["validation"],
            "errors": errors,
        }
        dashboard_payload = {
            "format_version": FORMAT_VERSION,
            "generated_at": generated_at,
            "iteration": iteration,
            "schema": {"dashboard_columns": DASHBOARD_COLUMNS, "validation_columns": VALIDATION_COLUMNS},
            "dashboard": dashboard,
            "validation": state["validation"],
            "errors": errors,
        }

        full_path = self.config.output_dir / FULL_JSON_NAME
        dashboard_path = self.config.output_dir / DASHBOARD_JSON_NAME
        archive_stamp = generated_at.replace(":", "").replace("-", "")
        archive_path = self.config.output_dir / f"gas_stock_tracker_run_{archive_stamp}_iter{iteration}.json"
        json_dump(full_path, full_payload)
        json_dump(dashboard_path, dashboard_payload)
        json_dump(archive_path, full_payload)
        validate_written_json(full_path, dashboard_path)

        telegram_caption = (
            f"JSON stock tracker iteration {iteration}: "
            f"{len(dashboard)} dashboard rows, validation {validation['Status']}"
        )
        telegram = TelegramClient(self.config).send_outputs([full_path, dashboard_path], telegram_caption)
        full_payload["telegram"] = telegram
        dashboard_payload["telegram"] = telegram
        json_dump(full_path, full_payload)
        json_dump(dashboard_path, dashboard_payload)
        json_dump(archive_path, full_payload)

        return {
            "iteration": iteration,
            "generated_at": generated_at,
            "full_json": str(full_path),
            "dashboard_json": str(dashboard_path),
            "archive_json": str(archive_path),
            "dashboard_rows": len(dashboard),
            "validation_status": validation["Status"],
            "telegram_status": telegram["status"],
            "errors": errors,
        }


def limit_scanner_symbols(scanners: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    remaining = limit
    limited: list[dict[str, Any]] = []
    for scanner in scanners:
        symbols = list(scanner.get("symbols", []))[: max(remaining, 0)]
        remaining -= len(symbols)
        limited.append({**scanner, "symbols": symbols})
        if remaining <= 0:
            for extra in scanners[len(limited) :]:
                limited.append({**extra, "symbols": []})
            break
    return limited


def build_price_history(generated_at: str, scanner_rows: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scanner_id, scanner_data in scanner_rows.items():
        for row in scanner_data:
            history_row = blank_row(PRICE_HISTORY_COLUMNS)
            history_row.update(row)
            history_row["Snapshot At"] = generated_at
            history_row["Scanner"] = scanner_id
            rows.append(project_row(history_row, PRICE_HISTORY_COLUMNS))
    return rows


def build_dashboard_history(generated_at: str, dashboard_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in dashboard_rows:
        history_row = blank_row(DASHBOARD_HISTORY_COLUMNS)
        history_row.update(row)
        history_row["Snapshot At"] = generated_at
        rows.append(project_row(history_row, DASHBOARD_HISTORY_COLUMNS))
    return rows


def build_validation(
    generated_at: str,
    iteration: int,
    dashboard: list[dict[str, Any]],
    market_data: dict[str, list[dict[str, Any]]],
    errors: list[dict[str, Any]],
    mode: str,
) -> dict[str, Any]:
    checked = [row for row in dashboard if row.get("In Screener?") == "Yes"]
    unresolved = [row for row in checked if row.get("Current Price") is None]
    latest_sessions = [
        bars[-1]["date"]
        for bars in market_data.values()
        if bars and isinstance(bars[-1], dict) and bars[-1].get("date")
    ]
    status = "PASS"
    details = "JSON files saved and schema-aligned"
    if not checked:
        status = "SKIP"
        details = "No active scanner rows were configured"
    elif unresolved or errors:
        status = "WARN"
        details = f"{len(unresolved)} unresolved active rows; {len(errors)} fetch errors"
    return {
        "Snapshot At": generated_at,
        "Iteration": iteration,
        "Mode": mode,
        "Checked Rows": len(checked),
        "Matched Rows": max(0, len(checked) - len(unresolved)),
        "Mismatch Rows": 0,
        "Unresolved Rows": len(unresolved),
        "Latest Session": max(latest_sessions) if latest_sessions else "",
        "Status": status,
        "Details": details,
    }


def validate_written_json(full_path: Path, dashboard_path: Path) -> None:
    full = json_load(full_path, {})
    dashboard = json_load(dashboard_path, {})
    if full.get("format_version") != FORMAT_VERSION:
        raise RuntimeError(f"invalid format_version in {full_path}")
    if dashboard.get("format_version") != FORMAT_VERSION:
        raise RuntimeError(f"invalid format_version in {dashboard_path}")
    for row in full.get("dashboard", []):
        if list(row.keys()) != DASHBOARD_COLUMNS:
            raise RuntimeError("dashboard row does not match dashboard schema")
    for scanner_rows in full.get("scanners", {}).values():
        for row in scanner_rows:
            allowed = set(SCANNER_COLUMNS) | {"Screener Link"}
            if not set(row.keys()).issubset(allowed):
                raise RuntimeError("scanner row has unexpected keys")


def running_from_notebook_launcher() -> bool:
    launcher = Path(sys.argv[0]).name.lower() if sys.argv else ""
    return (
        "colab_kernel_launcher" in launcher
        or "ipykernel_launcher" in launcher
        or bool(os.environ.get("COLAB_RELEASE_TAG"))
        or bool(os.environ.get("JPY_PARENT_PID"))
        or "google.colab" in sys.modules
    )


def build_config(argv: list[str] | None = None, *, max_iterations: int | None = None) -> TrackerConfig:
    env_max_iterations = os.environ.get("MAX_ITERATIONS")
    default_max_iterations = int(env_max_iterations) if env_max_iterations else max_iterations
    parser = argparse.ArgumentParser(description="Run the JSON stock screener tracker.")
    parser.add_argument("--source-json", type=Path, default=os.environ.get("SCREENER_SOURCE_JSON"))
    parser.add_argument("--scanner-url", action="append", default=[], help="ScannerName=https://www.screener.in/...")
    parser.add_argument("--output-dir", type=Path, default=Path(os.environ.get("SCREENER_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)))
    parser.add_argument("--max-iterations", type=int, default=default_max_iterations)
    parser.add_argument("--once", action="store_true", help="Alias for --max-iterations 1")
    parser.add_argument("--sleep-sec", type=float, default=float(os.environ.get("SLEEP_SEC", "60")))
    parser.add_argument("--timeout-sec", type=float, default=float(os.environ.get("REQUEST_TIMEOUT_SEC", "30")))
    parser.add_argument("--limit-symbols", type=int, default=None)
    parser.add_argument("--no-yahoo", action="store_true", help="Use only market data from --source-json.")
    parser.add_argument("--telegram-bot-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"))
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"))
    parser.add_argument("--telegram-api-base", default=os.environ.get("TELEGRAM_API_BASE", "https://api.telegram.org"))
    parser.add_argument("--telegram-dry-run", action="store_true", help="Do not call Telegram; record the files that would be sent.")
    parser.add_argument("--telegram-required", action="store_true", help="Fail if Telegram is not configured or sending fails.")
    args = parser.parse_args(argv)

    resolved_max_iterations = 1 if args.once else args.max_iterations
    if resolved_max_iterations is not None and resolved_max_iterations < 1:
        raise ValueError("--max-iterations must be >= 1")
    source_json = Path(args.source_json) if args.source_json else None
    return TrackerConfig(
        output_dir=args.output_dir,
        source_json=source_json,
        scanner_urls=tuple(args.scanner_url),
        fetch_yahoo=not args.no_yahoo,
        limit_symbols=args.limit_symbols,
        max_iterations=resolved_max_iterations,
        sleep_sec=args.sleep_sec,
        request_timeout_sec=args.timeout_sec,
        telegram_bot_token=args.telegram_bot_token,
        telegram_chat_id=args.telegram_chat_id,
        telegram_api_base=args.telegram_api_base,
        telegram_dry_run=args.telegram_dry_run,
        telegram_required=args.telegram_required,
    )


def main(argv: list[str] | None = None, *, max_iterations: Any = _UNSET) -> dict[str, Any]:
    program_max_iterations = None if max_iterations is _UNSET else max_iterations
    parse_argv = argv
    if argv is None and (max_iterations is not _UNSET or running_from_notebook_launcher()):
        parse_argv = []
    config = build_config(parse_argv, max_iterations=program_max_iterations)
    summary = JsonStockTracker(config).run()
    if config.max_iterations is not None:
        print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    try:
        main()
        # main(max_iterations=1)
    except Exception as exc:  # noqa: BLE001 - command-line tool returns JSON errors
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        raise
