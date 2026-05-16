# Screener.in Multi-MTF Stock Tracker - Parallel Edition

> GitHub reference for this file:
> `https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/README.md`
>
> Main script reference:
> [main scanner/screener-colab-appsheet-parallel.py](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/main%20scanner/screener-colab-appsheet-parallel.py)
>
> JSON script reference:
> [screener-colab-appsheet-json.py](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/screener-colab-appsheet-json.py)
>
> Docs index:
> - [Start Here Beginner Guide](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/START-HERE-BEGINNER-GUIDE.md)
> - [JSON Output Workflow](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/JSON-OUTPUT-WORKFLOW.md)
> - [How to Read Data](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/HOW-TO-READ-DATA.md)
> - [Complete Column Glossary](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/COMPLETE-COLUMN-GLOSSARY.md)
> - [All Possible Scenarios](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/ALL-POSSIBLE-SCENARIOS.md)
> - [Practical Scenario Examples](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/PRACTICAL-SCENARIO-EXAMPLES.md)
> - [Bugfix Analysis](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/bugfixana.md)
> - [Camarilla + Bollinger Integration](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/camarilla_bb_integration.md)
> - [Dashboard Heavy Analysis For Colab](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/DASHBOARD-HEAVY-ANALYSIS-COLAB.md)
> - [Gemini 3 Flash Lite Batch Reference](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/gemini%203-flash-lite-batch.md)

## GitHub Docs Folder Note

These files are prepared for upload inside the repository `docs/` folder.

That means the GitHub path pattern is:

- `https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/<filename>.md`

Use that path format whenever you want to replace a filename placeholder with the real GitHub URL.

Automated stock screener tracker for the currently configured Screener.in scanners.

## JSON Output Implementation

This repository now includes a runnable JSON-first tracker:

- main script: `screener-colab-appsheet-json.py`
- compatibility entrypoint: `main scanner/screener-colab-appsheet-json-full.py`
- full JSON output: `./gas_stock_tracker.json`
- dashboard-only JSON output: `./gas_stock_tracker_dashboard.json`
- dashboard snapshot history JSON: `./dashboard_snapshots.json`

The full JSON tracker uses the same top-of-file config block as the Excel Colab script. Scanner source comes from `SCANNERS`, AI is controlled by `AI_ENABLED` / `AI_PRIMARY` / `AI_SECONDARY_ENABLED`, and Telegram is controlled by `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`.

The JSON tracker saves files on the system where it is running, uploads JSON to the configured S3 JSON keys, and sends the full/dashboard JSON outputs to Telegram every iteration when Telegram credentials are configured.

Continuous run:

```bash
python screener-colab-appsheet-json.py
```

The script footer also supports the Excel-style in-file switch:

```python
if __name__ == "__main__":
    main()
    # main(max_iterations=1)
```

For a one-iteration test, comment `main()` and uncomment `main(max_iterations=1)`, exactly like the Excel script.

End-to-end validation:

```bash
python -m unittest discover -s tests -v
```

For the full JSON usage, schema, Telegram, and validation details, read:

- `docs/JSON-OUTPUT-WORKFLOW.md`

The older Excel workbook documentation below is kept as historical context for the same Dashboard/scanner/history concepts, but the full JSON clone writes JSON deliverables instead of `.xlsx`.

Important current-state note:

- the checked-in `SCANNERS` list currently contains `3` variant screens
- the workbook creates one scanner sheet per configured scanner
- older workbooks can still contain more historical scanner sheets from previous configurations

The script:

- fetches screener membership
- resolves symbols
- pulls Yahoo Finance OHLCV history
- computes technical indicators
- generates a rule-based signal
- optionally requests AI decisions
- writes everything into `gas_stock_tracker.json`
- writes a separate Dashboard-only `gas_stock_tracker_dashboard.json`
- maintains Dashboard, Dashboard History, Price History, and Validation history

Start here if you are new:

- `START-HERE-BEGINNER-GUIDE.md`
- `COMPLETE-COLUMN-GLOSSARY.md`

## AI Optimization Status

The latest AI-layer update did not increase dependencies.

- Python/package dependencies: unchanged
- AI providers: unchanged
- New pip installs required: none
- What changed: prompt rules, richer AI input context, metric-based AI cache key, safer JSON repair, and better reason preservation

So this was not only a prompt rewrite. The AI runtime logic was optimized, but the dependency footprint stayed the same.

## Dashboard Stability Fix (2026-04-11)

The live dashboard rebuild path now normalizes preserved Dashboard row values before ranking, sorting, coloring, and history writes.

- Existing Dashboard rows are read back with numeric fields coerced to numeric types.
- Inactive preserved rows no longer carry text values into momentum ranking or consensus sorting.
- This fixes the runtime failure: `'<` not supported between instances of `str` and `int'`.
- Output behavior is otherwise unchanged: the fix is for dashboard stability, not signal logic.

## Iteration Flow Fix (2026-04-11)

The end-of-iteration flow now keeps the dashboard-only export bounded to the real populated Dashboard range.

- `gas_stock_tracker_dashboard.xlsx` is now built from the current Dashboard data range only.
- The dashboard-only export no longer deep-copies the entire worksheet footprint.
- This reduces the chance of the loop stalling before Telegram/send/sleep on large or previously bloated Dashboard sheets.
- Intended order remains:
  - finish uploads
  - send Telegram status with both links
  - sleep `60` seconds
  - start next iteration

## Enhanced Live Signal Upgrade (2026-04-17)

The raw live setup engine now defaults to the enhanced rule path.

- `SIGNAL_ENGINE = "enhanced"` is the current default
- the enhanced setup engine consumes `+DI 14`, `-DI 14`, `NATR 14`, and Bollinger squeeze / stretch context
- the older stable rule path is still preserved as `Core Signal`

Practical meaning:

- `Setup Signal` = the raw rule-engine output before any walk-forward quality rejection
- `Signal` = the final live label after the predictive quality gate
- `Core Signal` = the simpler MA/RSI/ADX/MACD/volume/breakout baseline

## Walk-Forward Predictive Signal Upgrade (2026-04-17)

The live signal stack now adds a predictive validation layer on top of the rule engine.

New live columns:

- `Setup Signal`
- `Signal Quality`
- `Signal Regime`
- `Win Prob%`
- `Hist Precision%`
- `Exp 5D%`
- `Exp 10D%`
- `WF Samples`

Current method:

- a trailing `320`-bar lookback is used so the historical replays have enough context for `MA 200`, Bollinger width percentile, and the rest of the live indicator stack
- the most recent `180` eligible bars are evaluated in walk-forward mode
- each historical sample computes the signal using only the data that would have existed at that bar
- forward `5D` and `10D` returns are then measured from that historical signal point
- exact-label statistics are preferred first
- if the exact label has fewer than `5` samples, the script falls back to the broader signal family when that gives better coverage

Meaning of the predictive fields:

- `Signal Regime = TRENDING` means the current structure is directionally healthy and volatility is not abnormally hot
- `Signal Regime = CHOPPY` means trend quality is mixed even if the setup looks bullish on raw rules
- `Signal Regime = HIGH-VOL` means current normalized volatility is too hot for normal breakout confidence
- `Win Prob%` = `40%` weight on `5D` win rate plus `60%` weight on `10D` win rate
- `Hist Precision%` = historical `10D` win rate for the selected exact/family setup bucket
- `Exp 5D%` / `Exp 10D%` = average forward returns from those walk-forward samples
- `WF Samples` = number of usable historical examples backing the current row's setup statistics

Quality-gate behavior:

- bullish raw setups can be downgraded even when `Setup Signal` says `BUY`, `STRONG BUY`, `BREAKOUT`, `PULLBACK`, or `OVERSOLD`
- the final `Signal` becomes `HOLD (High Vol)`, `HOLD (Choppy Regime)`, `HOLD (Thin History)`, or `HOLD (Low Quality)` when the predictive gate rejects the raw setup
- `Signal Quality` now reports `PASS - HIGH`, `PASS - MED`, `PASS - LOW`, `PASS - UNVERIFIED`, `N/A - NON-BULL`, or `REJECT - ...`
- non-bullish setups are not re-labeled by the quality gate; they keep their raw `Setup Signal`

This upgrade does not claim perfect prediction. It is a stricter live filter designed to reduce low-quality longs, not to eliminate trading losses.

## Relative Strength, Liquidity, And Self-Validation Upgrade (2026-04-18)

The tracker now adds three more live quality layers on top of the predictive signal stack:

- benchmark-aware relative strength
- liquidity quality classification
- automatic post-run workbook self-validation

New live columns:

- `Sector`
- `Industry`
- `Sector Benchmark`
- `RS Tag`
- `RS vs NIFTY 1M%`
- `RS vs NIFTY 3M%`
- `RS vs Sector 1M%`
- `RS vs Sector 3M%`
- `Avg Traded Value 20D Cr`
- `Liquidity Tag`

New workbook sheet:

- `Validation`

How the relative-strength layer works:

- the script asks Yahoo for each stock's asset profile
- sector / industry labels are normalized into a smaller live set such as `Financial Services`, `Technology`, `Healthcare`, `Energy`, `Industrials`, and so on
- each normalized sector is mapped to the closest available NSE thematic benchmark when possible
- the stock's `1M` and `3M` returns are compared against both:
- `^NSEI` as the broad-market benchmark
- the resolved sector benchmark when one is available
- the `RS Tag` then compresses the four comparisons into a readable label:
- `Strong vs Both`
- `RS Leader`
- `Mixed`
- `Weak RS`
- `Lagging`

How the liquidity layer works:

- `Avg Traded Value 20D Cr` is the average recent daily traded-value estimate from Yahoo close x volume, converted into crores
- `Liquidity Tag` is then assigned with practical thresholds:
- `Deep` for `>= 100 Cr`
- `Liquid` for `>= 20 Cr`
- `Adequate` for `>= 5 Cr`
- `Thin` for `>= 1 Cr`
- `Illiquid` for `< 1 Cr`

How these new layers affect the Dashboard:

- `Momentum Rank` now includes medium-term relative-strength contribution, not only raw stock returns
- `Risk Tag` now becomes harsher when liquidity is thin or when the stock is materially lagging benchmarks
- `Quick Action` is downgraded when liquidity is `Thin` / `Illiquid` or when `RS Tag` is `Weak RS` / `Lagging`
- `BUY NOW` now also expects non-negative `3M` relative strength vs both NIFTY and the sector benchmark when those values exist

How the self-validation layer works:

- after each successful Dashboard rebuild, the full workbook appends one row to the `Validation` sheet
- the validator only checks active `Dashboard` rows with `In Screener? = Yes`
- unresolved rows such as `No Data`, `Symbol Not Found`, and `Error` are excluded from comparison and counted separately when fresh history is unavailable
- by default the validator checks a spaced sample of `12` rows across the eligible Dashboard, not only the top rows
- for each sampled row the script:
- refetches fresh Yahoo stock history
- refetches fresh benchmark history for relative-strength recomputation
- recomputes the live technical row using the current code
- compares prices, returns, indicators, signal-layer fields, relative-strength fields, and liquidity fields
- `Validation` sheet result states:
- `PASS` = no sampled mismatches
- `WARN` = at least one sampled mismatch
- `SKIP` = validation disabled or no eligible rows

Important workbook behavior:

- the `Validation` sheet exists only in the full workbook `gas_stock_tracker.xlsx`
- the Dashboard-only export stays dashboard-only
- the validation sheet is a run log for workbook freshness, not a per-stock watchlist

## Pre-Upgrade Active Dashboard Validation (2026-04-17)

The last exported dashboard-only workbook was validated against fresh Yahoo chart data before the predictive columns above were added.

- validation target: `gas_stock_tracker_dashboard (11).xlsx`
- scope: `In Screener? = Yes` rows only
- `321` active rows found in the export
- `318` active rows matched exactly on visible Dashboard metrics:
- `Current Price`, `1D%`, `1W%`, `1M%`, `3M%`, `6M%`, `1Y%`
- `RSI 14`, `ADX 14`, `+DI 14`, `-DI 14`, `ATR 14`, `NATR 14`
- the then-live `Signal` and `Core Signal` also matched exactly on those `318` rows
- the remaining `3` active rows were unresolved-data cases already represented correctly in the workbook:
- `NDRINVIT` -> `No Data`
- `IWARE` -> `No Data`
- `PropsharePlatina` -> `Symbol Not Found` with a blank resolved symbol

Practical meaning:

- the pre-upgrade active-row indicator math was verified for that export
- this was the historical reference before the `2026-04-18` freshness fix and post-fix validation shown below

## Yahoo History Freshness Fix (2026-04-18)

The Yahoo history path now defends against one-session-stale chart data.

What was wrong before:

- `fetch_history()` could accept `_yf_chart_history()` immediately when Yahoo chart/CDN returned a usable but stale daily series.
- the code did not compare chart recency against the `yfinance` fallback before accepting the primary response
- that could leave the workbook one completed session behind even in an off-market run

Observed stale examples from `gas_stock_tracker_dashboard (12).xlsx`:

- `QPOWER`: workbook `Current Price = 1138.05`, which matched Yahoo `2026-04-16`; fresh Yahoo `2026-04-17` close was `1206.05`
- `GOODLUCK`: workbook `1187.00`, which matched Yahoo `2026-04-16`; fresh Yahoo `2026-04-17` close was `1229.05`
- `SCI`: workbook `288.93`, which matched Yahoo `2026-04-16`; fresh Yahoo `2026-04-17` close was `305.87`

Current fix:

- `_hist_from_df(...)` converts fallback DataFrames into the same history shape as chart responses
- `_hist_last_ts(...)` extracts the last available session timestamp from either history source
- `_pick_fresher_history(...)` compares chart vs fallback and keeps the fresher dataset
- `fetch_history()` now always prefers the fresher history basis instead of blindly trusting the first chart payload

Practical meaning:

- off-market runs now use the latest completed Yahoo daily session more reliably
- `Current Price`, return columns, indicator columns, `Signal`, `Setup Signal`, `Core Signal`, and the walk-forward evidence fields are much less likely to be one session stale

## Post-Fix Active Dashboard Validation (2026-04-18)

The first dashboard-only workbook generated after the freshness fix was validated end-to-end against fresh Yahoo history.

- validation target: `gas_stock_tracker_dashboard (13).xlsx`
- scope: every `Dashboard` row with `In Screener? = Yes`
- `372` active rows were present in the export
- `370` active rows matched exactly on visible Dashboard metrics, signal-layer fields, and predictive fields
- `0` active mismatch rows were found
- `0` signal-layer mismatch rows were found
- the only expected active unresolved-data cases were:
- `PropsharePlatina` -> `Symbol Not Found`
- `PARTH` -> `No Data`

Fields verified on matched rows:

- `Current Price`, `1D%`, `1W%`, `1M%`, `3M%`, `6M%`, `1Y%`
- `RSI 14`, `ADX 14`, `+DI 14`, `-DI 14`, `ATR 14`, `NATR 14`
- `Signal`, `Setup Signal`, `Core Signal`
- `Signal Quality`, `Signal Regime`
- `Win Prob%`, `Hist Precision%`, `Exp 5D%`, `Exp 10D%`, `WF Samples`
- `RS Tag`, `RS vs NIFTY 1M%`, `RS vs NIFTY 3M%`, `RS vs Sector 1M%`, `RS vs Sector 3M%`
- `Avg Traded Value 20D Cr`, `Liquidity Tag`

Practical meaning:

- `gas_stock_tracker_dashboard (12).xlsx` is a stale historical reference only
- `gas_stock_tracker_dashboard (13).xlsx` is the first clean post-fix active-row reference export for resolved Yahoo history
- later workbook pair `(15)` / full workbook `(4)` are the latest structurally verified artifacts; see the `2026-04-19` note below

## Historical MTF Reliability Fix (2026-04-14)

`Historical MTF` is now a real price-based multi-timeframe field.

- `MTF Alignment` still means live active scanner breadth across Daily / Weekly / Monthly buckets inferred from scanner IDs.
- `Historical MTF` now uses Yahoo price history resampled into Daily / Weekly / Monthly bars.
- Each timeframe is evaluated from actual price structure rather than retained scanner-name history.
- The workbook column name stays `Historical MTF` for compatibility, but the meaning is now price-based D/W/M structure.
- If usable Yahoo history is missing, `Historical MTF` is left blank.

Current configuration nuance:

- the checked-in `Variant-*` scanner IDs do not expose weekly / monthly tags, so they classify into the default `D` bucket
- because of that, `MTF Alignment` can legitimately stay `D`-heavy unless you add or rename scanners so the script can classify some scanners as `W` or `M`
- do not confuse missing `W` / `M` scanner breadth with bearish price structure; that is what `Historical MTF` is for

This is more reliable than the previous version because the earlier implementation could show broad "historical" alignment from retained scanner rows or even current scanner presence on a new stock, without proving that the price structure itself was aligned across D / W / M.

## Latest Workbook Verification Snapshot (2026-04-19)

The later workbook pair was also checked after the schema, AI-runtime, and validation-sheet upgrades.

Dashboard-only export:

- target: `gas_stock_tracker_dashboard (15).xlsx`
- real Dashboard schema at that time: `66` columns
- total Dashboard rows: `685`
- active rows: `359`
- inactive rows: `325`
- active rows with blank `Signal`: `0`
- active rows with blank `Setup Signal`: `0`
- active rows with blank `Core Signal`: `0`
- active rows with blank `AI Decision`: `2`
- those two AI-blank active rows were unresolved-data rows already represented correctly:
- `PARTH` -> `No Data`
- one blank-symbol row -> `Symbol Not Found`

Full workbook:

- target: `gas_stock_tracker (4).xlsx`
- workbook sheet count: `257`
- latest visible `Validation` rows both returned `PASS`
- sampled validation results stored in the workbook were:
- `2/2` matched active rows on `2026-04-18 19:00:44`
- `12/12` matched active rows on `2026-04-19 22:40:39`
- the full-workbook `Dashboard` matched the dashboard-only export on the real `66` populated headers and `685` rows

Low-severity workbook artifact:

- the full-workbook `Dashboard` carried a bloated Excel used-range (`A1:ZXC685`)
- inspection showed those far-right cells were stale empty cells / used-range metadata, not shifted dashboard data
- the meaningful Dashboard data remained aligned on the real `66` populated columns

Practical meaning:

- `(13)` remains the first post-fix full active-row recompute reference
- `(15)` and full workbook `(4)` are the latest structurally verified workbook artifacts
- no active-row structural corruption was found in that later pair
- later code now adds one extra Dashboard readability column, `Momentum Tag`, so future exports will show `67` Dashboard columns

## Screener Pagination Fix (2026-04-11)

The screener fetch path now paginates across all pages for a screen instead of silently stopping at page 1.

- the script now reads `limit` and walks `page=1,2,3...`
- stocks are deduplicated across pages
- fetch stops when a page comes back empty or shorter than the requested page size

This fixes screens like `long-term` where page 2 contains additional stocks that were previously missed.

## Screener Startup Fetch Fix (2026-04-12)

The live fetcher now handles the current page-expanded `SCANNERS` list more efficiently.

- if a scanner URL already contains an explicit `page=` value, the fetcher now fetches only that page
- automatic multi-page walking is used only when the URL does not specify a page
- Phase 1 now prints progress during screener fetch
- screener fetch now tries direct requests first and uses shorter timeouts before proxy fallback

This prevents the startup phase from exploding into repeated nested pagination work.

## Safe Phase 1 Speedup (2026-04-12)

Phase 1 is now faster without blindly raising overall worker pressure.

- screener fetch uses its own worker count: `SCREENER_FETCH_WORKERS = 4`
- YF and AI still keep the lower `PARALLEL_WORKERS = 2`
- explicit paged screen URLs are grouped by base screen
- within each group, fetch stops after the first empty later page

This speeds up startup mainly by reducing wasted screener requests, not by hammering the site.

## Screener Auth Fail-Fast Fix (2026-04-12)

The public screener fetch path was simplified back toward the older working implementation.

- exact screener page URLs are fetched directly first
- page query parameters such as `?page=2` are preserved instead of being over-rewritten
- old-style JSON and HTML parsing is retained
- the false `[AUTH]` classification path was removed for public scanner fetches
- if Phase 1 still ends with zero stocks, the run aborts generically instead of blaming cookies

If this still fails on a public screen, the issue is now the actual fetch response for that runtime, not the tracker forcing an auth error path.

## Colab Runtime Log Noise Fix (2026-04-18)

The Colab/Jupyter runtime path now suppresses warning spam and reduces progress noise.

- notebook `jupyter_client.session` `DeprecationWarning` spam is filtered at startup
- the notebook helper is patched to use timezone-aware `datetime.now(timezone.utc)` when possible
- compact runtime logging is now the default in Colab-like environments
- per-screen, per-stock, and per-sheet progress spam is reduced in compact mode

Practical meaning:

- `log.txt` is less likely to be dominated by notebook warning noise
- real scanner errors are easier to spot in Colab output

## Main Features

- 5-phase pipeline with deduplicated Yahoo and AI work
- parallel fetch model with conservative concurrency
- persistent workbook workflow with S3 upload
- Dashboard aggregation across all scanners
- inactive scanner rows are frozen instead of being re-evaluated
- append-only history sheets
- Telegram alerts for new captures
- Telegram status now includes separate full-workbook and dashboard-only download links
- AI round-robin across multiple keys within the active provider family, with optional secondary-provider fallback

## 5-Phase Pipeline

1. Fetch screener pages
2. Update scanner sheets and resolve symbols
3. Fetch Yahoo Finance data for unique symbols
4. Generate AI decisions for valid symbols
5. Write results back to workbook and history sheets

## Technical Indicators

The current build computes:

- `RSI 14`
- `MA 20`
- `MA 50`
- `MA 200`
- `ADX 14`
- `+DI 14`
- `-DI 14`
- `ATR 14`
- `NATR 14`
- `Vol Ratio 20`
- `MACD Line`
- `MACD Hist`
- `52W High Dist%`
- `20D Breakout%`
- Bollinger context:
  - `BB %B`
  - `BB Width`
  - `BB Width Pctl`
  - `BB Squeeze`
- Camarilla context:
  - `Cam H3`
  - `Cam H4`
  - `Cam L3`
  - `Cam L4`

Return metrics:

- `1D%`
- `1W%`
- `1M%`
- `3M%`
- `6M%`
- `1Y%`
- `2Y%`
- `3Y%`
- `Avg Weekly%`
- `Avg Monthly%`
- `Avg 3M%`
- `Avg 6M%`
- `Avg 1Y%`

## Signal Engine

The live system now has three technical signal layers:

- `Setup Signal`: raw rule-engine output from the active engine
- `Signal`: final quality-gated live label
- `Core Signal`: older stable base-rule reference

`Setup Signal` uses:

- MA structure
- RSI state
- ADX strength
- MACD direction and histogram
- relative volume
- 52-week positioning
- 20-day breakout state
- DI confirmation
- normalized volatility via `NATR`
- Bollinger squeeze / expansion context

`Core Signal` is the older stable rule path that uses the base MA/RSI/ADX/MACD/volume/breakout logic without the DI / NATR / Bollinger refinement layer.

Raw setup family includes:

- `BREAKOUT`
- `STRONG BUY`
- `STRONG BUY (Oversold)`
- `BUY`
- `BUY (Squeeze)`
- `HOLD (Overbought)`
- `HOLD (DI Weakness)`
- `HOLD`
- `HOLD (Below MA200)`
- `PULLBACK`
- `OVERSOLD`
- `OVERSOLD (Watch)`
- `WEAK`
- `SELL`
- `No Data`
- `Symbol Not Found`

Additional final live labels introduced by the predictive gate:

- `HOLD (High Vol)`
- `HOLD (Choppy Regime)`
- `HOLD (Thin History)`
- `HOLD (Low Quality)`

## Workbook Structure

The workbook contains:

- `Dashboard`
- `Dashboard History`
- `Price History`
- one sheet per configured scanner
- with the current checked-in config, that means `3` scanner sheets
- older carried-forward workbooks may contain more historical scanner or backup sheets from previous runs

Per iteration, the script now also writes a second workbook:

- `gas_stock_tracker_dashboard.xlsx`

Current live-file behavior:

- `gas_stock_tracker.xlsx` is updated each successful iteration
- `gas_stock_tracker_dashboard.xlsx` is also regenerated each successful iteration
- the dashboard-only workbook contains only the `Dashboard` sheet

Current schema sizes:

- scanner sheets: `59` columns
- `Price History`: `51` columns
- `Dashboard`: `67` columns
- `Dashboard History`: `55` columns
- `Validation`: `10` columns

## Dashboard Columns

Main Dashboard decision columns:

- `In Screener?`
- `Signal`
- `Setup Signal`
- `Core Signal`
- `Signal Quality`
- `Signal Regime`
- `Win Prob%`
- `Hist Precision%`
- `Exp 5D%`
- `Exp 10D%`
- `WF Samples`
- `Quick Action`
- `Consensus Score`
- `MTF Alignment`
- `Historical MTF`
- `Momentum Rank`
- `Momentum Tag`
- `Risk Tag`
- `BB Signal`
- `Cam Setup`
- `Volume Buzz`
- `Since Capture Trend`

Tracking columns:

- `Symbol`
- `Name`
- `First Captured`
- `Days Tracked`
- `Last Seen`
- `Total Appearances`
- `Unique Scanners`
- `Scanner List`
- `Best Scanner`

Scanner meaning:

- `Scanner List` = all scanner sheets where the stock still exists in tracker history
- `Best Scanner` = the scanner that has produced the most live `In Screener? = Yes` hits for that stock

Momentum readability:

- `Momentum Rank` is still the true relative rank
- `Momentum Tag` is a simpler bucket derived from that rank:
- `ELITE`
- `STRONG`
- `HEALTHY`
- `NEUTRAL`
- `WEAK`
- `LAGGING`
- this addition does not change momentum math; it only makes Dashboard reading faster
- `Momentum Tag` is appended at the end of the Dashboard so older workbook columns do not shift during the first upgraded run

MTF notes:

- `MTF Alignment` = active-now Daily / Weekly / Monthly presence from rows where `In Screener? = Yes`
- `Historical MTF` = price-based Daily / Weekly / Monthly structure from Yahoo history resampled into D / W / M bars

Performance columns:

- `Capture Price`
- `Current Price`
- `Cam H3`
- `Cam H4`
- `Cam L3`
- `Cam L4`
- `Ideal Enter Price`
- `Possible Sell Value`
- `Stop Loss Value`
- `Since Capture%`
- `1D%`
- `1W%`
- `1M%`
- `3M%`
- `6M%`
- `1Y%`
- `RSI 14`
- `ADX 14`
- `+DI 14`
- `-DI 14`
- `ATR 14`
- `NATR 14`

Signal and AI columns:

- `Signal`
- `Setup Signal`
- `Core Signal`
- `Signal Quality`
- `Signal Regime`
- `Win Prob%`
- `Hist Precision%`
- `Exp 5D%`
- `Exp 10D%`
- `WF Samples`
- `AI Decision`
- `AI Conf%`

Reference columns:

- `Screener Link`
- `Last Updated`

Generated workbook files:

- `gas_stock_tracker.xlsx`
- `gas_stock_tracker_dashboard.xlsx`

Telegram download behavior:

- one link for `gas_stock_tracker.xlsx`
- one link for `gas_stock_tracker_dashboard.xlsx`

## AI Dependency

The AI layer is optional. The technical layer is not.

Runtime dependency reality:

- the AI layer currently uses `openai` plus `requests`
- NVIDIA NIM is called through an OpenAI-compatible chat path
- Gemini is called through Google's native `generateContent` REST path with JSON schema enforcement
- no extra AI-specific package was added in the recent AI upgrade
- AI calls still need live internet access at runtime, even if the rest of the workbook structure already exists

Current AI controls in the script:

- `AI_ENABLED = True` turns the AI layer on or off
- `AI_PRIMARY = "nvidia"` or `"google"` decides which provider family is primary
- `AI_SECONDARY_ENABLED = False` means use only the primary provider; `True` allows the other provider family only after the primary chain is exhausted
- `NVIDIA_NIM_API_KEYS` holds the NVIDIA NIM API keys
- `NVIDIA_NIM_MODELS` holds the allowed NIM model list
- `GEMINI_API_KEYS` holds the Google API keys
- `GEMINI_MODELS` holds the allowed Gemini model list
- `AI_TIMEOUT_SEC`, `AI_MAX_RETRIES`, and `AI_DELAY_SEC` control call behavior
- `AI_TEMPERATURE = 0.0`, `AI_TOP_P = 1.0`, and fixed per-provider model lists are used to reduce variance

Current checked-in defaults:

- `AI_PRIMARY = "google"`
- `AI_SECONDARY_ENABLED = False`
- primary Gemini model list currently contains `gemini-3-flash-preview`
- NVIDIA remains available through `NVIDIA_NIM_MODELS`, currently `z-ai/glm-5.1`

Current provider behavior:

- if `AI_SECONDARY_ENABLED = False`, the script rotates only within the primary provider family
- if `AI_SECONDARY_ENABLED = True`, the other provider family is tried only after the full primary chain fails
- keys rotate within the active provider; the scanner does not mix providers on the same row unless secondary fallback is explicitly enabled
- Gemini requests use native structured JSON output with minimal thinking
- NVIDIA GLM-family requests send explicit thinking-disable hints for consistency
- if `AI_ENABLED = False`, the AI layer is skipped entirely
- if `AI_ENABLED = True` but no valid provider is actually available, the technical layer still runs and AI fields remain blank

Works without AI:

- all technical indicators
- rule-based `Signal`
- `Setup Signal`
- `Core Signal`
- `Signal Quality`
- `Signal Regime`
- `Win Prob%`
- `Hist Precision%`
- `Exp 5D%`
- `Exp 10D%`
- `WF Samples`
- `Risk Tag`
- `BB Signal`
- `Cam Setup`
- `Volume Buzz`
- `MTF Alignment`
- `Historical MTF`
- scanner aggregation fields

Depends directly on AI:

- `AI Decision`
- `AI Reason`
- `AI Conf%`
- `Consensus Score`
- AI-assisted ranking pressure in `Quick Action`

Important nuance:

- `Quick Action` still exists without AI, but it becomes a far weaker routing field because `Consensus Score` is blank
- without AI, `Quick Action` mostly falls back to `WATCH`
- do not use missing AI as evidence that the technical setup is bad; it only means the optional second-opinion layer is absent

Dashboard History now also captures the raw Camarilla levels used by the Dashboard decision layer.

Inactive-row behavior:

- if a scanner row has `In Screener? = No`, the script no longer refreshes Yahoo-derived or AI-derived values on that row
- Dashboard keeps the stock visible, but marks it inactive through the Dashboard `In Screener?` column
- inactive Dashboard rows preserve their last live values instead of being re-evaluated from stale sheet state

## How To Pick Stocks

Start from the Dashboard only. Ignore inactive rows first.

Absolute first filter:

1. keep only `In Screener? = Yes`
2. skip `Signal = No Data`, `Symbol Not Found`, or `Error`
3. skip rows where the final `Signal` is already non-bullish unless you are explicitly looking for watchlist or reversal cases

How to pick with AI enabled:

1. require `Signal` to be `BUY`, `BUY (Squeeze)`, `STRONG BUY`, `STRONG BUY (Oversold)`, `BREAKOUT`, `PULLBACK`, or a controlled `OVERSOLD`
2. prefer `Setup Signal` and `Core Signal` to agree or at least not strongly contradict the final `Signal`
3. reject rows where `Signal Quality` already says `REJECT - ...`
4. prefer `Signal Regime = TRENDING`
5. prefer `Win Prob% >= 55`, `Hist Precision% >= 55`, and positive `Exp 10D%`
6. prefer `WF Samples >= 5`; treat `PASS - UNVERIFIED` as weaker than `PASS - HIGH` or `PASS - MED`
7. prefer `Risk Tag` not `HIGH`
8. prefer `Volume Buzz` not `Low`
9. prefer `+DI 14 > -DI 14`
10. prefer constructive `BB Signal` and `Cam Setup`:
- `SQUEEZE BREAK`
- `SQUEEZE`
- `BUY ZONE`
- `SQUEEZE + H4 BREAK`
- `WATCH H4 BREAK`
- `OVERSOLD AT L3`
11. then check AI:
- `AI Decision` should be bullish
- `AI Conf% >= 65` is a good practical threshold
- `Consensus Score >= 6` is stronger than raw technicals alone
12. then read `Quick Action`:
- `BUY NOW` is the strongest fully aligned state
- `ACCUMULATE` is good but not perfect
- `WATCH` means keep monitoring, not immediate action

How to pick with AI disabled:

1. ignore `AI Decision`, `AI Reason`, `AI Conf%`, and `Consensus Score`
2. treat `Quick Action` as a weak helper only, because it usually falls back to `WATCH`
3. rely mainly on:
- `Signal`
- `Setup Signal`
- `Core Signal`
- `Signal Quality`
- `Signal Regime`
- `Win Prob%`, `Hist Precision%`, `Exp 10D%`, `WF Samples`
- `Risk Tag`
- `BB Signal`
- `Cam Setup`
- `Volume Buzz`
- `MTF Alignment`
- `Historical MTF`
4. prioritize rows where the final `Signal` is bullish, the quality gate passed, the regime is not `HIGH-VOL`, and the predictive stats are not weak
5. use `MTF Alignment` for live scanner breadth and `Historical MTF` for price-based D/W/M structure; the best rows usually have support from both

Fast shortlist logic:

- best continuation candidates: `BREAKOUT` or `STRONG BUY` plus `PASS - HIGH` or `PASS - MED`, `TRENDING`, low/medium risk, good DI direction, and constructive BB/Camarilla context
- best early watch candidates: `BUY (Squeeze)` or `BUY` plus non-reject quality and tightening/squeeze context
- best dip-buy candidates: `STRONG BUY (Oversold)` or controlled `OVERSOLD` plus `BUY ZONE` or `OVERSOLD AT L3`, without `HIGH` risk
- rows to avoid for fresh longs: `HOLD (High Vol)`, `HOLD (Choppy Regime)`, `HOLD (Low Quality)`, `HOLD (Below MA200)`, `WEAK`, `SELL`, and any unresolved-data row

## Signal Integrity and Accuracy Updates

The current version includes the following hardening and correction work:

- row-aligned Yahoo OHLCV parsing
- stricter moving-average validity
- corrected RSI flat-series behavior
- DMI/ADX enrichment with `+DI` and `-DI`
- volatility enrichment with `ATR` and `NATR`
- percentile-based Bollinger squeeze detection
- walk-forward signal statistics with exact-label and family fallback buckets
- predictive quality gating for bullish setups
- Dashboard-level Camarilla integration using the previous completed bar
- active-row-only AI consensus
- transient field cleanup on `No Data`
- safer aggregation keying through `_stock_key(...)`

Practical impact:

- fewer low-quality buys in sideways markets
- stronger rejection of hot or statistically weak bullish setups
- cleaner directional confirmation
- less chasing of overly hot breakouts
- more meaningful squeeze labels across different stocks
- Dashboard and Price History now carry the raw Camarilla reference levels used by the execution layer
- inactive names no longer pollute live Dashboard metrics with fresh AI/non-AI refreshes
- users now get a smaller dashboard-only workbook each cycle for faster sharing/review

Default signal profile:

- `balanced`

Available profiles:

- `precision` (experimental)
- `conservative`
- `balanced`
- `aggressive`

The `precision` profile remains available for testing, but it is not the default because wider holdout testing on April 11, 2026 did not show robust generalization.

Backtest usage guide:

- `backtest/HOW-TO-USE-BACKTEST.md`

Colab notebook:

- `output/jupyter-notebook/colab-parallel-and-backtest-runner.ipynb`

Detailed live scenario guide:

- `ALL-POSSIBLE-SCENARIOS.md`

Practical live examples guide:

- `PRACTICAL-SCENARIO-EXAMPLES.md`

Beginner onboarding guide:

- `START-HERE-BEGINNER-GUIDE.md`

Complete column-by-column glossary:

- `COMPLETE-COLUMN-GLOSSARY.md`

The notebook and Colab helper flow now cover these Python programs:

- `screener-colab-appsheet-parallel.py`
- `download_dashboard_only_files.py`
- `dashboard_heavy_analysis_colab.py`
- `backtest/backtest_parallel_core_report.py`

Dashboard-only analyzer guide:

- `DASHBOARD-HEAVY-ANALYSIS-COLAB.md`

Current analyzer status:

- `dashboard_heavy_analysis_colab.py` reads the dashboard-only workbook and the core markdown docs.
- `best_stock` is now gated more strictly toward actionable `BUY NOW` / `ACCUMULATE` rows with stronger live confirmation.
- NVIDIA NIM refinement can now run in parallel across keys from `screener-colab-appsheet-parallel.py`.
- repeated same-input reruns can reuse a persistent NVIDIA cache file for better speed and more stable output.

## Scanner Sheet Schema

Scanner sheet groups:

- Identity:
  - `Symbol`, `Name`, `First Captured`, `Last Seen`, `In Screener?`
- Pricing:
  - `Capture Price`, `Current Price`, `Since Capture%`
- Returns:
  - `1D%`, `1W%`, `1M%`, `3M%`, `6M%`, `1Y%`, `2Y%`, `3Y%`
- Averages:
  - `Avg Weekly%`, `Avg Monthly%`, `Avg 3M%`, `Avg 6M%`, `Avg 1Y%`
- Trend:
  - `RSI 14`, `MA 20`, `MA 50`, `MA 200`
- Signal:
  - `Signal`
- AI:
  - `AI Decision`, `AI Reason`, `AI Conf%`
- Advanced:
  - `ADX 14`, `+DI 14`, `-DI 14`, `ATR 14`, `NATR 14`, `Vol Ratio 20`, `MACD Line`, `MACD Hist`, `52W High Dist%`, `20D Breakout%`
- Meta:
  - `Last Updated`

## Dashboard Interpretation Notes

- `Quick Action` is a routing layer, not an execution command.
- `Signal` is the first technical layer.
- `AI Decision` is a second opinion layer.
- `Risk Tag`, `BB Signal`, and `Cam Setup` help prevent chasing poor-quality setups.
- `SQUEEZE` is a setup state.
- `SQUEEZE BREAK` is more actionable than plain `SQUEEZE`.
- `PASS - UNVERIFIED` belongs to `Signal Quality`, not `Signal Regime`.

## Configuration

Main settings near the top of the script include:

- Telegram config
- screener cookie
- Wasabi S3 config
- AI provider keys
- AI model list
- signal profile
- parallel worker count

## Basic Usage

JSON tracker continuous usage:

```bash
python screener-colab-appsheet-json.py
```

One-iteration test:

Edit the footer to call `main(max_iterations=1)`.

## Recommended Validation After Changes

When changing signal logic, check:

1. signal distribution before and after
2. `No Data` rows are neutralized
3. inactive rows do not affect consensus
4. OHLCV alignment looks sane on sample symbols
5. breakout candidates have sensible `+DI/-DI`, `NATR`, `BB Signal`, and `Cam Setup`
6. active JSON rows match the latest completed Yahoo daily session, not the prior session
7. AI-disabled runs still produce sensible technical rows even when `Consensus Score` is blank

## Files

- `screener-colab-appsheet-json.py` - JSON-first main script
- `main scanner/screener-colab-appsheet-json-full.py` - compatibility entrypoint for the JSON tracker
- `tests/test_json_tracker_e2e.py` - end-to-end JSON and Telegram validation
- `JSON-OUTPUT-WORKFLOW.md` - JSON output, Telegram, and validation guide
- `screener-colab-appsheet-parallel.py` - main script
- `download_dashboard_only_files.py` - Colab-friendly dashboard-only downloader
- `dashboard_heavy_analysis_colab.py` - heavy dashboard analyzer for the dashboard-only workbook
- `DASHBOARD-HEAVY-ANALYSIS-COLAB.md` - Colab usage guide for the dashboard analyzer
- `HOW-TO-READ-DATA.md` - user-facing interpretation guide
- `START-HERE-BEGINNER-GUIDE.md` - beginner-oriented workbook onboarding guide
- `COMPLETE-COLUMN-GLOSSARY.md` - exhaustive meaning of workbook columns
- `bugfixana.md` - applied fixes and reassessment notes

## Current Status

Core indicator math is in good shape.

Latest verification status:

- stale-Yahoo daily history drift seen in `gas_stock_tracker_dashboard (12).xlsx` was fixed on `2026-04-18`
- `gas_stock_tracker_dashboard (13).xlsx` is verified clean for active rows with resolved data
- remaining uncertainty is normal market risk and unresolved symbol/data cases, not a known active-row calculation bug in the current verified export

## April 21, 2026 Update

### Verified `Momentum Tag` output

The first generated workbook checked after the `Momentum Tag` addition was:

- `gas_stock_tracker_dashboard (16).xlsx`

Verified facts from that file:

- Dashboard rows: `728`
- Dashboard columns: `67`
- active rows: `313`
- inactive rows: `415`
- active blank `Signal`: `0`
- active blank `Setup Signal`: `0`
- active blank `Core Signal`: `0`
- active blank `Momentum Tag`: `0`

Observed active `Momentum Tag` distribution:

- `ELITE = 31`
- `STRONG = 31`
- `HEALTHY = 63`
- `NEUTRAL = 62`
- `WEAK = 63`
- `LAGGING = 63`

That confirms:

- `Momentum Tag` is now a verified live Dashboard output
- `Momentum Rank` remains the exact ordering field
- `Momentum Tag` is only a human-readable bucket built from that same rank

### Intraday `Validation = WARN` interpretation

The matching full workbook was:

- `gas_stock_tracker (5).xlsx`

Its latest visible `Validation` row showed:

- `Snapshot At = 2026-04-21 11:04:13`
- `Mode = fresh-sample-12`
- `Checked Rows = 12`
- `Matched Rows = 0`
- `Mismatch Rows = 12`
- `Unresolved Rows = 0`
- `Latest Session = 2026-04-21`
- `Status = WARN`

The recorded mismatch details were:

- `PRIVISCL`: `Current Price`, `RSI 14`, `RS vs NIFTY 1M%`, `RS vs NIFTY 3M%`
- `GRAPHITE`: `Current Price`, `1D%`, `1W%`, `RSI 14`
- `NATCOPHARM`: `Current Price`, `1D%`, `1W%`, `RSI 14`
- `UNIPARTS`: `Current Price`, `1D%`, `1W%`, `RSI 14`
- `RPTECH`: `Current Price`, `1D%`, `1W%`, `RSI 14`

This pattern is important:

- it is a live-drift pattern, not a schema-break pattern
- during market hours, `Current Price`, `1D%`, `1W%`, `RSI 14`, and benchmark-relative strength can move before the validator finishes its fresh recomputation
- because of that, a market-hours `WARN` can happen even when the workbook logic is correct

Practical reading rule:

- off-market `PASS` is still the strongest freshness confirmation
- market-hours `WARN` should be interpreted through the `Details` column before assuming the workbook is wrong
- this `WARN` does **not** mean `Momentum Tag` broke validation
