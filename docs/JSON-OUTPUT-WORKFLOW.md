# JSON Output Workflow

> GitHub reference for this file:
> `https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/JSON-OUTPUT-WORKFLOW.md`

This repo now includes a full JSON-only clone of the Colab tracker:

- source Excel script: `docs/screener-colab-appsheet-parallel.py`
- JSON script: `screener-colab-appsheet-json.py`
- compatibility launcher: `main scanner/screener-colab-appsheet-json-full.py`

The JSON script keeps the same runtime shape and feature switches as the Excel script. The difference is the deliverable: it persists JSON, uploads JSON, and sends JSON documents to Telegram.

## Source And Config

The source comes from the same places as the Excel script.

- `SCANNERS`: Screener.in scanner definitions.
- `SCREENER_COOKIE`: Screener session cookie.
- `PROXY_URL`: optional Screener proxy.
- `YF_SUFFIX`: Yahoo suffix, currently `.NS`.
- `AI_ENABLED`: turns AI decisions on or off.
- `AI_PRIMARY`: chooses `google` or `nvidia`.
- `AI_SECONDARY_ENABLED`: enables fallback to the other AI provider.
- `NVIDIA_NIM_API_KEYS`, `NVIDIA_NIM_MODELS`: NVIDIA AI config.
- `GEMINI_API_KEYS`, `GEMINI_MODELS`: Gemini AI config.
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`: Telegram config.
- `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_REGION`: S3-compatible storage config.

There is no separate `source.json` input in the full clone. Edit the same top config block you already edit in the Excel script.

## Run

Continuous run:

```bash
python screener-colab-appsheet-json.py
```

Compatibility launcher:

```bash
python "main scanner/screener-colab-appsheet-json-full.py"
```

Colab copy-paste footer:

```python
if __name__ == "__main__":
    main()
    # main(max_iterations=1)
```

For a one-iteration test, comment `main()` and uncomment `main(max_iterations=1)`.

## JSON Output

Local files are saved beside the script:

- `gas_stock_tracker.json`
- `gas_stock_tracker_dashboard.json`
- `dashboard_snapshots.json` when `DASHBOARD_DB_ENABLED = True`

S3 keys are configured at the top:

- `S3_JSON_KEY = "reports/gas_stock_tracker.json"`
- `S3_DASHBOARD_JSON_KEY = "reports/gas_stock_tracker_dashboard.json"`
- `S3_DASHBOARD_DB_KEY = "reports/dashboard_snapshots.json"`

The full JSON file stores the workbook-equivalent sections as JSON sheets:

- `Dashboard`
- all scanner sheets
- `Price History`
- `Dashboard History`
- `Validation`

The dashboard JSON file stores only the `Dashboard` sheet.

The dashboard snapshots JSON file stores the same historical dashboard rows that the Excel script's SQLite snapshot feature stored, but as JSON records with row metadata and the full dashboard payload.

## Telegram

Each successful iteration sends:

- a Telegram status message
- `gas_stock_tracker.json` as a Telegram document
- `gas_stock_tracker_dashboard.json` as a Telegram document
- the best-picks text summary when available

New-stock alerts still use the same alert logic from the Excel script.

## What Changed From Excel

Kept:

- scanner fetching
- symbol resolution
- Yahoo history fetching
- technical indicators
- AI decisions
- fundamental layer
- dashboard update
- validation
- Telegram alerts
- loop behavior
- Colab restart behavior
- S3 persistence
- dashboard snapshot history

Changed:

- no `.xlsx` files are written
- S3 report keys now use `.json`
- local report files now use `.json`
- dashboard-only export is JSON
- Telegram sends JSON documents instead of Excel workbook files
- dashboard snapshot history is written to `dashboard_snapshots.json`, not SQLite

## Validation

Recommended checks after changes:

```bash
python -m py_compile screener-colab-appsheet-json.py "main scanner/screener-colab-appsheet-json-full.py"
```

The full runtime needs the same packages as the Excel script because it keeps the same feature set and in-memory calculation model. No extra package is added for JSON output.
