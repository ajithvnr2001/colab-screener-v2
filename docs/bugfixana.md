# Bugfix Analysis and Step-by-Step Fix Plan

## Applied Indicator Accuracy Fixes (2026-04-10)

- Implemented in `D:\screener-colab-appsheet\screener-colab-appsheet-parallel.py`.
- Scope of this pass was indicator correctness plus safe schema additions for scanner/history/dashboard outputs.

## AI Optimization Status (2026-04-11)

- AI layer optimized without adding new dependencies.
- Scope of AI change: prompt rules, richer runtime context, safer cache key, better JSON recovery, and explanation preservation.
- AI providers and Python dependency footprint remain unchanged.

## Applied AI Provider Hardening (2026-04-19)

- Current checked-in default: `AI_PRIMARY = "google"`
- Current checked-in default: `AI_SECONDARY_ENABLED = False`
- Gemini now uses a native `generateContent` JSON-schema path with minimal thinking
- NVIDIA remains available when selected as primary or when secondary fallback is enabled
- NVIDIA GLM-family requests send explicit thinking-disable hints
- deterministic settings are now fixed around:
  - `AI_TEMPERATURE = 0.0`
  - `AI_TOP_P = 1.0`
  - fixed per-provider model lists

Expected effect:

- lower provider-to-provider variance
- less free-text / reasoning leakage into supposed JSON outputs
- clearer separation between primary-provider-only mode and true secondary fallback mode

## Applied Dashboard Stability Fix (2026-04-11)

- Dashboard rebuild now normalizes preserved Dashboard row values before reuse.
- Numeric columns from existing Dashboard rows are coerced back to numeric types.
- Inactive preserved rows no longer feed string values into momentum ranking, consensus sorting, color formatting, or history writes.
- This fixes the runtime failure seen in `log.txt`:
  - `Dashboard update failed: '<' not supported between instances of 'str' and 'int'`
- Scope of this fix is dashboard stability only. It does not change indicator math or the live signal engine.

## Applied Iteration Flow Fix (2026-04-11)

- The dashboard-only workbook export now copies only the real populated Dashboard range.
- It no longer deep-copies the full worksheet footprint.
- This reduces the chance of the run stalling after the final full-workbook upload and before Telegram/send/sleep.
- Intended runtime order:
  - upload full workbook
  - upload dashboard-only workbook
  - send Telegram status with both links

## Applied Live Signal Promotion (2026-04-17)

- The live `Signal` field now defaults to the enhanced rule path via `SIGNAL_ENGINE = "enhanced"`.
- The enhanced engine now directly drives the workbook `Signal`, AI context, and Telegram signal label.
- The older stable path is still preserved as `Core Signal` for comparison and debugging.
- Added off-market completed-session metric reuse through `signal_snapshot_cache.json`.

Expected effect:

- repeated off-market runs should keep the same indicator values and the same live `Signal`
- the main live signal is now stricter because it consumes `+DI 14`, `-DI 14`, `NATR 14`, and Bollinger squeeze / stretch context
- `Core Signal` remains available when you want the simpler base-trend read

## Applied Walk-Forward Predictive Signal Upgrade (2026-04-17)

- Added a predictive validation layer on top of the raw rule engine.
- New signal stack:
  - `Setup Signal` = raw enhanced-engine output
  - `Signal` = final quality-gated live label
  - `Core Signal` = older stable base-rule baseline
- Added live columns:
  - `Signal Quality`
  - `Signal Regime`
  - `Win Prob%`
  - `Hist Precision%`
  - `Exp 5D%`
  - `Exp 10D%`
  - `WF Samples`

Current walk-forward method:

- keep a trailing `320`-bar context window for replayed historical setups
- evaluate the most recent `180` eligible bars
- compute each historical setup using only the data available up to that bar
- measure forward `5D` and `10D` returns from that point
- prefer exact-label statistics first
- if exact samples are below `5`, fall back to the broader signal family when it provides better coverage

Current thresholds:

- `WALKFORWARD_MIN_SAMPLES = 5`
- `QUALITY_GATE_MIN_WIN_PROB = 55.0`
- `QUALITY_GATE_MIN_HIST_PRECISION = 55.0`
- `QUALITY_GATE_MIN_EXP_10D = 1.0`
- `QUALITY_GATE_MIN_SCORE = 55.0`

Current regime family:

- `TRENDING`
- `CHOPPY`
- `HIGH-VOL`

Current quality outputs:

- `PASS - HIGH`
- `PASS - MED`
- `PASS - LOW`
- `PASS - UNVERIFIED`
- `N/A - NON-BULL`
- `REJECT - HIGH-VOL`
- `REJECT - CHOPPY`
- `REJECT - THIN HISTORY`
- `REJECT - LOW EDGE`

Current reject downgrades:

- `HOLD (High Vol)`
- `HOLD (Choppy Regime)`
- `HOLD (Thin History)`
- `HOLD (Low Quality)`

Schema impact:

- scanner sheets: `59` columns
- `Price History`: `51` columns
- `Dashboard`: `67` columns
- `Dashboard History`: `55` columns

Other integration points:

- AI context now includes `Setup Signal`, `Signal Quality`, `Signal Regime`, and the walk-forward evidence fields
- Telegram alert summaries now show the raw setup plus predictive quality context
- Dashboard `Quick Action` now degrades rejected rows to `WATCH`, `CAUTION`, or `AVOID`
- walk-forward stats are cached in `signal_walkforward_cache.json`

Expected effect:

- fewer low-quality bullish signals getting through in choppy or overheated conditions
- clearer separation between raw setup quality and final live actionability
- better workbook transparency about why a row passed or failed

## Applied Pre-Upgrade Full Active Dashboard Validation (2026-04-17)

- Validation target: `D:\screener-colab-appsheet\main scanner\gas_stock_tracker_dashboard (11).xlsx`
- Validation scope: every `Dashboard` row with `In Screener? = Yes`
- Method:
- parse the Dashboard workbook directly from XLSX XML
- refetch `3y` Yahoo chart history for each active symbol
- recompute the visible Dashboard fields and both signal engines using the same balanced-profile formulas as the live script

Result:

- `321` active rows in the export
- `318` active rows validated exactly on visible Dashboard metrics plus both `Signal` and `Core Signal`
- `0` signal mismatches on validated rows
- `0` visible-metric mismatches on validated rows
- the remaining `3` active rows were unresolved-data cases already reflected correctly by the workbook:
- `NDRINVIT` -> `No Data`
- `IWARE` -> `No Data`
- `PropsharePlatina` -> `Symbol Not Found`

Expected effect:

- the pre-upgrade dashboard export is verified end-to-end for active rows with usable Yahoo history
- remaining exceptions are symbol-resolution / Yahoo-availability issues, not indicator-math defects
- a fresh post-upgrade run is still required to validate the new predictive columns and current final `Signal`

## Applied Yahoo History Freshness Fix (2026-04-18)

- Root issue:
  - `fetch_history()` could accept `_yf_chart_history()` immediately if the chart payload looked usable.
  - It did not compare that chart payload against the `yfinance` fallback for freshness.
  - In an off-market run, Yahoo chart/CDN could therefore leave the workbook one completed session behind.

- Real stale-export evidence from `D:\screener-colab-appsheet\main scanner\gas_stock_tracker_dashboard (12).xlsx`:
  - `QPOWER`: workbook `1138.05` matched Yahoo `2026-04-16`, while fresh Yahoo `2026-04-17` close was `1206.05`
  - `GOODLUCK`: workbook `1187.00` matched Yahoo `2026-04-16`, while fresh Yahoo `2026-04-17` close was `1229.05`
  - `SCI`: workbook `288.93` matched Yahoo `2026-04-16`, while fresh Yahoo `2026-04-17` close was `305.87`

- Current code change:
  - added `_hist_from_df(...)`
  - added `_hist_last_ts(...)`
  - added `_pick_fresher_history(...)`
  - updated `fetch_history()` so chart and fallback are both checked and the fresher history wins

- Expected effect:
  - active workbook rows should now use the latest completed Yahoo daily session more reliably
  - prices, return columns, indicators, `Signal`, and predictive fields should no longer lag by one completed session in the same way

## Applied Post-Fix Full Active Dashboard Validation (2026-04-18)

- Validation target: `D:\screener-colab-appsheet\main scanner\gas_stock_tracker_dashboard (13).xlsx`
- Validation scope: every `Dashboard` row with `In Screener? = Yes`
- Method:
  - parse the Dashboard workbook directly
  - refetch fresh Yahoo history for each active symbol through the current patched history path
  - recompute the visible Dashboard metrics, signal fields, and predictive fields using the current live formulas

Result:

- `372` active rows in the export
- `370` active rows validated exactly on:
  - `Current Price`, `1D%`, `1W%`, `1M%`, `3M%`, `6M%`, `1Y%`
  - `RSI 14`, `ADX 14`, `+DI 14`, `-DI 14`, `ATR 14`, `NATR 14`
  - `Signal`, `Setup Signal`, `Core Signal`
  - `Signal Quality`, `Signal Regime`
  - `Win Prob%`, `Hist Precision%`, `Exp 5D%`, `Exp 10D%`, `WF Samples`
- `0` active mismatch rows
- `0` signal-layer mismatch rows
- expected active unresolved-data rows:
  - `PropsharePlatina` -> `Symbol Not Found`
  - `PARTH` -> `No Data`

Expected effect:

- the current post-fix dashboard export is verified for active rows with resolved Yahoo data
- remaining uncertainty is normal market risk or unresolved symbol/data states, not a known live active-row math mismatch in the verified export

## Applied Later Workbook Pair Verification (2026-04-19)

- Dashboard-only target: `D:\screener-colab-appsheet\main scanner\gas_stock_tracker_dashboard (15).xlsx`
- Full-workbook target: `D:\screener-colab-appsheet\main scanner\gas_stock_tracker (4).xlsx`

Result:

- dashboard-only file was structurally clean
- real Dashboard schema remained `66` columns
- active rows with blank `Signal`: `0`
- active rows with blank `Setup Signal`: `0`
- active rows with blank `Core Signal`: `0`
- active rows with blank `AI Decision`: `2`, both unresolved-data cases already represented correctly
- full workbook carried `257` sheets
- latest visible `Validation` rows inside the full workbook both returned `PASS`
- the full-workbook Dashboard matched the dashboard-only export on the real populated columns and row count

Low-severity note:

- the full-workbook Dashboard had a stale far-right used-range footprint
- inspection showed this was empty-cell / Excel metadata inflation, not shifted live Dashboard data

## Applied Colab Runtime Log Noise Fix (2026-04-18)

- Root issue:
  - Colab/Jupyter could flood `log.txt` and notebook output with `jupyter_client.session` `DeprecationWarning` lines.
  - Heavy progress printing made the warning flood harder to read around real scanner logs.

- Current code change:
  - added notebook-specific warning filters at startup
  - patched notebook `utcnow()` usage to `datetime.now(timezone.utc)` when possible
  - enabled compact runtime logging by default in Colab-like environments
  - reduced per-screen, per-new-stock, and per-sheet progress spam in compact mode

- Expected effect:
  - cleaner `log.txt`
  - real scanner/runtime issues are easier to identify in Colab output

## Applied Screener Pagination Fix (2026-04-11)

- Root issue: `fetch_screener(...)` rebuilt the screen URL without the original query string, so `page=2+` was ignored and only page 1 was fetched.
- Current behavior:
  - the fetcher parses `limit` from the screener URL
  - fetches `page=1,2,3...`
  - deduplicates stocks across pages
  - stops when a page is empty or shorter than the page size

Expected effect:

- multi-page screens such as `long-term` now contribute all stocks, not just the first page

## Applied Screener Startup Fetch Fix (2026-04-12)

- Root issue: the current `SCANNERS` list is already page-expanded to many explicit `page=1..5` URLs, while the newer fetcher was also auto-paginating internally.
- That created nested pagination work and made Phase 1 look stalled.
- Current behavior:
  - explicit `page=` URLs fetch only that page
  - non-paged URLs still auto-walk across pages
  - direct requests are attempted first
  - fetch timeouts are shorter
  - Phase 1 progress is printed every 10 completed screener fetches

Expected effect:

- startup should move again instead of hanging for a long time before the first fetch output

## Applied Public Screener No-Cookie-First Fix (2026-04-12)

- Root issue: the newer fetcher had drifted too far from the older working behavior.
- Current behavior:
  - exact public screener page URLs are fetched directly first
  - page query parameters are preserved
  - old-style JSON and HTML parsing is retained
  - the false public-screen `[AUTH]` classification path was removed

Expected effect:

- public scanners should follow the older working fetch path again instead of being blocked by the newer auth/error logic

## Applied Safe Phase 1 Speedup (2026-04-12)

- Added a separate conservative screener-fetch worker count instead of raising all parallelism.
- Grouped explicit paged screen URLs by base screen.
- Within each group, later pages stop after the first empty later page.
- Yahoo and AI worker counts remain lower and unchanged.

Expected effect:

- faster Phase 1 with lower wasted request volume
- better speed without relying on obviously aggressive fetch patterns

## Applied Public Screener Fetch Simplification (2026-04-12)

- Root issue: the screener fetch logic had drifted away from the older working implementation and was over-classifying public fetch failures as auth problems.
- Current behavior:
  - exact public screener page URLs are fetched directly
  - page query parameters are preserved
  - old-style JSON and HTML parsing is retained
  - zero-stock runs still abort safely, but without forcing a fake auth diagnosis

Expected effect:

- public scanners follow the older fetch behavior again
- failures are treated as actual fetch/parse problems instead of cookie-only issues

### Fixed

- `calc_ma`
  - Now requires the full lookback window.
  - `MA 20`, `MA 50`, and `MA 200` no longer emit partial-window values mislabeled as full moving averages.

- `calc_rsi`
  - Flat series now returns `50.0` instead of `100.0`.
  - Minimum history check corrected to `period + 1`.

- `calc_dmi_metrics` added
  - Reworked DMI/ADX path to compute:
    - `ADX 14`
    - `+DI 14`
    - `-DI 14`
    - `ATR 14`
    - `NATR 14`
  - ADX smoothing now starts from valid DX values instead of implicitly blending early invalid slots as zeros.

- `calc_vol_ratio`
  - Uses actual recent sessions and keeps zero-volume bars instead of dropping them.
  - This makes RVOL less misleading for illiquid names.

- `calc_dist_52w`
  - Now returns a value only when a true 252-session window exists.
  - Prevents shorter-history stocks from being mislabeled as using a real 52-week reference.

- `calc_breakout_20d`
  - Minimum lookback corrected to allow a valid prior 20-session high comparison without the extra unnecessary bar.

- `calc_bollinger`
  - Minimum history check corrected from `period + 1` to `period`.

- Yahoo history normalization
  - `_yf_chart_history` now uses `adjclose` when available and applies the adjustment ratio to high/low as well.
  - `_yf_fetch_fallback` now enforces valid `Close/High/Low` rows and fills missing volume with `0.0`.
  - Result: history basis is more consistent across primary/fallback paths.

### Added

- New indicators added to metrics and workbook outputs:
  - `ATR 14`
  - `NATR 14`
  - `+DI 14`
  - `-DI 14`

- These are now wired into:
  - Scanner sheets
  - `Price History`
  - `Dashboard`
  - `Dashboard History`
  - AI prompt context
  - Telegram alert summary

### Compatibility

- Existing scanner sheets and `Price History` now refresh header rows, so newly added columns are labeled in already-existing workbooks instead of appearing as unlabeled trailing cells.
- Current schema sizes after the predictive upgrade:
  - scanner sheets: `59`
  - `Price History`: `51`
  - `Dashboard`: `67`
  - `Dashboard History`: `55`

### Momentum readability add-on

- Added `Momentum Tag` to the live `Dashboard` only.
- It is derived from the existing `Momentum Rank` percentile.
- It does not change momentum scoring, signal math, or ranking behavior.
- It is appended at the end of the Dashboard schema so older workbook columns do not shift during the first upgraded run.
- Reason for this add-on:
  - `Momentum Rank` is exact but less readable at a glance.
  - `Momentum Tag` makes the dashboard easier to scan without changing core logic.

### Verification

- Syntax check passed:
  - `uv run python -m py_compile "D:\screener-colab-appsheet\screener-colab-appsheet-parallel.py"`

## Applied Signal-Layer Upgrade (2026-04-10, second pass)

### What changed

- Added a new enhanced signal engine that actually consumes the newly added indicators:
  - `+DI 14`
  - `-DI 14`
  - `NATR 14`
  - Bollinger squeeze context

- The enhanced signal logic now:
  - requires directional confirmation for stronger long signals using `+DI > -DI`
  - requires a meaningful DI spread for the highest-quality breakout path
  - blocks or softens long signals when `NATR` is excessively hot
  - upgrades `BUY` into `BUY (Squeeze)` when a valid squeeze-to-breakout context is present
  - adds `HOLD (DI Weakness)` when price structure is okay but directional internals are weakening

- Bollinger context improved:
  - `calc_bollinger` now returns:
    - `BB %B`
    - `BB Width`
    - `BB Width Pctl`
    - `BB Squeeze`
  - Squeeze detection now uses rolling width percentile instead of a fixed universal width threshold.

- Dashboard interpretation improved:
  - `BB Signal` now recognizes `SQUEEZE BREAK` and percentile-based squeeze states.
  - `Risk Tag` now also considers:
    - high `NATR`
    - bearish `-DI > +DI` when ADX is already strong

- Aggregation keying improvement:
  - dashboard aggregation now uses `_stock_key(...)` instead of raw `sym else name`, reducing duplicate/merge risk for unresolved symbols.

### Verification

- Syntax check passed after the signal-layer upgrade:
  - `uv run python -m py_compile "D:\screener-colab-appsheet\screener-colab-appsheet-parallel.py"`

## Final Reassessment Status

### Current verdict

- Core indicator math is now in good shape.
- I do not see any obvious remaining correctness bug in the implemented indicators that would justify calling the current version "wrong".
- Remaining work is mainly model improvement or strategy tuning, not bug fixing.
- After the `2026-04-18` freshness fix, the active-row dashboard export `gas_stock_tracker_dashboard (13).xlsx` is also verified clean for resolved-data active rows.

### Indicators that are now acceptable

- `MA 20`, `MA 50`, `MA 200`
- `RSI 14`
- `ADX 14`
- `+DI 14`
- `-DI 14`
- `ATR 14`
- `NATR 14`
- `MACD Line`
- `MACD Hist`
- `Vol Ratio 20`
- `52W High Dist%`
- `20D Breakout%`
- `BB %B`
- `BB Width`
- `BB Width Pctl`
- `BB Squeeze`

### Important note

- `BB Signal`, `Risk Tag`, `Quick Action`, and the rule-based `Signal` are still heuristic decision layers.
- That is expected. They are not pure textbook indicators; they are interpretation logic built on top of the indicators.
- At this point they are reasonable and internally more consistent than before.

### Profile status update (2026-04-11)

- `balanced` remains the default signal profile in `D:\screener-colab-appsheet\screener-colab-appsheet-parallel.py`.
- `precision` exists as an optional experimental profile only.
- Reason: small-sample tests looked better, but a wider 20-stock holdout backtest did not generalize well enough to justify changing the live default.
- Operational recommendation:
  - use `balanced` for normal live runs
  - use the backtest folder to compare profiles before changing defaults
  - do not treat tiny-sample high accuracy as proof of robustness

### Optional future upgrades

- Add relative strength versus `NIFTY 50` and ideally sector benchmark.
- Add one volume-flow indicator such as `OBV`, `CMF`, or `MFI`.
- Add trend slope metrics such as `MA 50 slope` and `MA 200 slope`.
- Add ATR-based stop/risk bands for position management.
- Add regime-aware squeeze logic or TTM Squeeze if you want a more specialized breakout model.

## Applied Dashboard Strategy Add-on (2026-04-10, Camarilla + BB)

### What changed

- Added daily Camarilla `H3/H4/L3/L4` using the previous completed bar.
- Added a Dashboard-only `Cam Setup` layer that combines Bollinger state with Camarilla location.
- Added Dashboard execution columns:
  - `Ideal Enter Price`
  - `Possible Sell Value`
  - `Stop Loss Value`

### Important accuracy note

- This implementation uses the previous bar's plain range `H - L`.
- It does not use ATR-style true range.
- Any upside target beyond `H4` is treated as a derived target, not a canonical `H5`.

### Current deployment note

- The Camarilla + BB overlay remains part of the current live implementation.
- The main script default signal profile is `balanced`.
- This Camarilla overlay is still valid under any signal profile because it is a Dashboard interpretation/execution layer, not a replacement for the underlying indicator math.

## Scope
- Target file only: `D:\screener-colab-appsheet\screener-colab-appsheet-parallel.py`
- Focus only on fixes that materially change the generated signal list (`Signal`, Dashboard actions, ranking/consensus inputs).
- No infra/UI-only items included.

## Current Status (Already Correct)
- ADX gating for normal `BUY` is implemented.
  - `tm = adx is not None and adx >= cfg["ADX_WEAK"]` at around line `1795`.
  - `BUY` uses `... and tm` at around line `1804`.

---

## Priority Overview

1. **P0**: OHLCV row misalignment in Yahoo chart parser can produce wrong indicators and wrong `Signal`.
2. **P0**: Sentinel collision (`~NOFOUND`) can merge multiple unresolved stocks into one logical key.
3. **P1**: `No Data` path only writes `Signal`, leaves stale RSI/ADX/MACD/AI on row.
4. **P1**: Dashboard consensus ingests AI decisions from inactive rows (`In Screener? = No`).
5. **P2**: MA validity threshold (80% period) can create premature MA200 and alter trend classification.

---

## Fix 1 (P0): OHLCV Alignment Bug in `_yf_chart_history`

### Why this is major
- Current parser removes NaNs only from `close`, then truncates other arrays by length.
- This can decouple `close[i]` from `high[i]/low[i]/volume[i]`.
- ADX, MACD context, breakout, vol-ratio can be calculated from mismatched bars.
- Direct impact: wrong `BUY/HOLD/SELL` labels.

### Code anchors
- Function: `_yf_chart_history`
- Region: lines around `1570` to `1580`.
- Current risky behavior:
  - `closes = [x for x in closes if not math.isnan(x)]`
  - then slicing all arrays to `n = len(closes)`.

### Inch-by-inch implementation steps
1. In `_yf_chart_history`, stop filtering only `closes`.
2. Build all 4 arrays first (`close/high/low/volume`) from raw quote payload.
3. Compute common length `n_raw = min(len(closes), len(highs), len(lows), len(volumes))`.
4. Iterate `i in range(n_raw)` and build aligned rows.
5. Keep row only when at least `close`, `high`, `low` are finite numbers.
6. For `volume`, coerce missing to `0.0` (or drop row; choose one policy and keep it consistent).
7. Append accepted values into new arrays: `cl_aligned`, `hi_aligned`, `lo_aligned`, `vo_aligned`.
8. Enforce minimum accepted rows (`>= 5`) before return.
9. Return dict built from aligned arrays only.
10. Add one defensive check: all returned arrays must have equal length.

### Acceptance criteria
- `len(closes) == len(highs) == len(lows) == len(volumes)` for every returned history.
- Indicator functions never receive misaligned series.
- For the same symbol/date range, computed ADX and breakout are stable across runs.

### Validation checklist
- Pick 10 symbols with known sparse history and run one iteration.
- Confirm no exceptions in `calc_adx` from shape mismatch.
- Compare before/after signal counts for drift; inspect changed symbols manually.

---

## Fix 2 (P0): Sentinel (`~NOFOUND`) Key Collision in Sheet Identity

### Why this is major
- New unresolved symbols are inserted as `Symbol = "~NOFOUND"`.
- `load_sheet_stocks` uses `key = sym if sym else name`.
- Multiple unresolved rows collapse to the same key (`~NOFOUND`) and overwrite each other in memory.
- Direct impact: dropped symbols, wrong row updates, incomplete signal list.

### Code anchors
- Sentinel constant around line `226`.
- Loader key logic around line `1412`.
- Insert path sets sentinel around line `1956`.

### Inch-by-inch implementation steps
1. Introduce a helper function for stable row keying, e.g. `_stock_key(sym, name)`.
2. Keying rule:
   - If `sym` exists and not sentinel -> key by symbol.
   - If `sym` is sentinel or empty and `name` exists -> key by normalized name.
   - If both missing -> skip row.
3. Update `load_sheet_stocks` to use `_stock_key`.
4. Update Phase-2 ingestion (`key = sym if sym else name`) to use `_stock_key`.
5. Keep writing sentinel in sheet for visibility, but never use sentinel as primary identity key.
6. Add normalization for name keys (`strip`, collapse spaces, uppercase) to avoid duplicates by case/spacing.
7. Add duplicate detection log if same computed key appears twice in one sheet.

### Acceptance criteria
- Two unresolved names in same scanner remain as two independent rows.
- Re-run does not merge or overwrite unrelated unresolved entries.
- Number of rows with unresolved symbols matches number of unresolved names found.

### Validation checklist
- Force at least 3 unresolved symbols in a test scanner.
- Ensure all 3 persist with distinct rows after two iterations.
- Verify none are replaced by latest unresolved stock.

---

## Fix 3 (P1): `No Data` Path Leaves Stale Metrics on Scanner Rows

### Why this is major
- On fetch miss, code only writes `Signal = "No Data"` and continues.
- Previous RSI/ADX/MACD/AI fields remain from earlier cycles.
- Dashboard aggregation can read stale technical context and stale AI.
- Direct impact: signal list appears current but carries old indicator evidence.

### Code anchors
- Phase-5 write loop around lines `2075` to `2078`.

### Inch-by-inch implementation steps
1. Define a list of transient metric columns:
   - `Current Price`, returns (`1D%...3Y%`, averages), `RSI 14`, `MA 20/50/200`,
   - `ADX 14`, `Vol Ratio 20`, `MACD Line`, `MACD Hist`,
   - `52W High Dist%`, `20D Breakout%`, `AI Decision`, `AI Reason`, `AI Conf%`, `Last Updated`.
2. In `if not m:` branch, set `Signal = "No Data"` as today.
3. Clear all transient columns explicitly (`None`) for that row.
4. Keep identity/history columns intact:
   - `Symbol`, `Name`, `First Captured`, `Last Seen`, `In Screener?`, `Capture Price`.
5. Optionally stamp `Last Updated` with run timestamp + `No Data` note policy (choose one and keep consistent).

### Acceptance criteria
- Any `No Data` row has no stale indicator/AI values.
- Dashboard no longer inherits old AI decision when symbol has no latest data.

### Validation checklist
- Simulate one symbol transitioning from valid data to `No Data`.
- Verify RSI/ADX/MACD/AI become blank in scanner sheet.
- Confirm Dashboard reflects neutral/unknown state, not old bullish/bearish state.

---

## Fix 4 (P1): Dashboard Consensus Uses Inactive Rows

### Why this is major
- In `update_dashboard`, AI scores are appended whenever `ai_dec` is present.
- This happens regardless of `In Screener?` status.
- Inactive rows (`No`) can still bias consensus and quick action.
- Direct impact: action list can overstate conviction for stocks no longer active.

### Code anchors
- Aggregation loop around lines `938` to `1001`.
- `appearances` already gated by `if in_screener == "Yes"` at lines `996` to `998`.
- AI score append currently not gated at line `999`.

### Inch-by-inch implementation steps
1. Define active-row condition once:
   - `is_active = (in_screener == "Yes")`.
2. Keep scanners/timeframe metadata behavior as-is (or decide strict-active only; document choice).
3. Gate AI consensus append with `is_active`.
4. Gate AI confidence append with `is_active`.
5. (Recommended) For per-stock latest fields (`Signal`, `RSI`, `ADX`, etc.), prefer active row values over inactive values when both exist.
6. Add a tiny counter for skipped inactive AI values for audit logs.

### Acceptance criteria
- `Consensus Score` uses active scanner presence only.
- Removing a stock from all scanners eventually removes bullish/bearish AI carryover in Dashboard.

### Validation checklist
- Pick a symbol with historical AI `BUY`, then remove it from screener.
- Next run: ensure its consensus does not still use old AI scores.
- Verify action category changes accordingly.

---

## Fix 5 (P2): MA Validity Threshold Too Permissive for Long MA

### Why this is major
- `calc_ma` returns MA when `len(v) >= ceil(period * 0.8)`.
- For MA200, this can accept around 160 points and still emit MA200.
- Trend logic (`hm2`, `a200`, `pb`) can fire earlier than intended.
- Direct impact: early `BUY/HOLD` state transitions.

### Code anchors
- `calc_ma` around lines `1687` to `1690`.

### Inch-by-inch implementation steps
1. Add strictness by period tier:
   - For `period < 100`: keep flexible threshold (optional).
   - For `period >= 100` (especially 200): require full period length.
2. Keep output format unchanged (rounded float).
3. Document threshold policy near `SIGNAL_PROFILES` or near `calc_ma`.
4. Re-run on older listed stocks and newly listed stocks to confirm expected behavior.

### Acceptance criteria
- MA200 is absent (`None`) when insufficient long history.
- `hm2` path is only active with true long-term data support.

### Validation checklist
- For a stock with ~170 trading days, MA200 should be `None`.
- Ensure signal uses fallback logic (`not hm2`) as designed.

---

## Recommended Execution Order

1. Fix 1 (OHLCV alignment)  
2. Fix 2 (sentinel key collision)  
3. Fix 3 (`No Data` stale metrics clear)  
4. Fix 4 (inactive-row AI gating)  
5. Fix 5 (MA strictness policy)

Reason: first stabilize data correctness and row identity, then clean stale-state propagation, then tune MA strictness.

---

## Regression Test Matrix (Signal-Only)

Run after each fix and once at end:

1. **Data integrity**
- Number of symbols with valid metrics.
- Number of `No Data` rows.
- No indicator exceptions.

2. **Signal distribution**
- Count by `Signal` class: `BREAKOUT`, `STRONG BUY`, `BUY`, `HOLD`, `SELL`, etc.
- Diff vs prior run; inspect large deltas.

3. **Stale-state checks**
- For forced `No Data` symbols, all transient fields blank.
- Dashboard consensus changes when symbol becomes inactive.

4. **Identity checks**
- Multiple unresolved symbols remain distinct.
- No unintended row overwrite across iterations.

5. **Action coherence**
- Quick Action aligns with current active consensus.
- No symbols promoted by inactive stale AI.

---

## Done Definition

This bugfix batch is complete when:
- Signals are computed from aligned OHLCV rows only.
- Unresolved symbols no longer collide/overwrite.
- `No Data` does not carry stale technical/AI state.
- Dashboard consensus ignores inactive scanner rows.
- MA200 requires sufficient history and no premature long-trend interpretation.

---

## Applied Dashboard Activity Freeze + Separate Dashboard Workbook (2026-04-11)

### What changed

- Added Dashboard `In Screener?` so the Dashboard explicitly shows whether a stock is active in the current run.
- Scanner-sheet rows with `In Screener? = No` are now frozen:
  - no Yahoo metric refresh
  - no AI refresh
  - no Phase 5 overwrite
- Dashboard aggregation now uses active rows for live values and keeps inactive rows only as historical context.
- Added a second workbook artifact generated on each successful iteration:
  - `gas_stock_tracker.xlsx`
  - `gas_stock_tracker_dashboard.xlsx`
- Telegram now sends separate download links for:
  - full workbook
  - dashboard-only workbook

## Applied Historical MTF Reliability Fix (2026-04-14)

- `MTF Alignment` remains the live active-only Daily / Weekly / Monthly scanner-breadth view.
- `Historical MTF` no longer uses retained scanner history.
- `Historical MTF` now uses actual Yahoo price history resampled into Daily / Weekly / Monthly bars.
- Each timeframe is checked from real price structure instead of scanner-name presence.
- Dashboard, Dashboard History, and Dashboard DB payloads still carry `Historical MTF`, but the column meaning is now price-based D / W / M structure.
- If usable Yahoo history is missing, `Historical MTF` is left blank.

Why this is more reliable than the previous version:

- the older implementation could show broad "historical" alignment from retained scanner rows
- a brand-new stock could inherit a strong-looking `Historical MTF` simply from current scanner presence
- the new implementation answers the actual timeframe question: is the stock's price structure constructive on D / W / M?
- MTF output format remains tick-based, for example `D✅ W✅ M❌`.

## Applied Dashboard Heavy Analysis Recommendation Fix (2026-04-14)

- Scope of this pass was `dashboard_heavy_analysis_colab.py`, not the main tracker loop.
- Root issue from runtime review:
  - `WATCH` rows could still become `BEST STOCK`
  - too many rows could saturate at `100`
  - persistence-style rows could attach generic breakout docs too easily
- Current behavior:
  - `WATCH` is penalized instead of rewarded in the core score
  - `best_stock` now prefers active, non-excluded `BUY NOW` or `ACCUMULATE` rows with at least `2` live MTF confirmations
  - score inflation was reduced so ranking separates strong names more cleanly
  - ranking now prefers actionability and live confirmation ahead of weak persistence
  - markdown retrieval now penalizes generic breakout headings for persistence / weakening scenarios
  - analyzer wording now treats `Historical MTF` as price-based higher-timeframe structure, not retained scanner history

Expected effect:

- fewer watchlist-grade names surfacing as the top upside candidate
- more defensible separation between live actionable names and context-only names
- less misleading documentation context on non-breakout scenarios

## Applied Dashboard Heavy Analysis Speed And Stability Fix (2026-04-14)

- Scope of this pass was also `dashboard_heavy_analysis_colab.py`.
- Root issue:
  - `--ai-mode all` was calling NVIDIA NIM sequentially, which made all-stock analysis very slow
  - repeated reruns on the same input could drift because every run re-asked the model
- Current behavior:
  - NVIDIA NIM requests now run in parallel with a thread pool
  - worker count can auto-scale from the NVIDIA keys parsed from `screener-colab-appsheet-parallel.py`
  - AI prompt payload was trimmed to reduce latency
  - per-request token budget and timeout are configurable from CLI
  - AI temperature was reduced to `0.0`
  - repeated reruns can reuse `dashboard_ai_nvidia_cache.json`
  - ranking tie-break now includes stable symbol/name fallbacks

Expected effect:

- materially faster all-stock AI analysis in Colab
- more stable repeated outputs when the workbook and docs are unchanged
- lower unnecessary NVIDIA usage on same-input reruns

## Applied Phase 5 Write-Path Optimization (2026-04-13)

- Periodic S3 checkpoints now skip local artifact save by default.
- Periodic S3 checkpoints now skip backup-copy creation by default.
- Final end-of-iteration saves still keep the normal upload path.
- Phase 5 row rewrites now reuse static style objects instead of rebuilding them on every existing-row update.

### Why this matters

- Prevents inactive names from receiving fresh technical or AI values they did not earn in the current run.
- Prevents inactive scanner rows from contaminating Dashboard interpretation.
- Makes sharing the Dashboard faster because the dashboard-only workbook is smaller than the full tracker.

### Current expected behavior

- `In Screener? = Yes`
  - row is live
  - metrics and AI can update
- `In Screener? = No`
  - row is retained
  - row is not recalculated
  - Dashboard shows it as inactive context, not fresh conviction

---

## Notes
- This document intentionally does not include implementation code.
- It is an execution-grade checklist for controlled patching in `screener-colab-appsheet-parallel.py`.

## Applied Verification Update (2026-04-21)

### `Momentum Tag` output verification

Verified target:

- `D:\screener-colab-appsheet\main scanner\gas_stock_tracker_dashboard (16).xlsx`

Verified facts:

- Dashboard columns = `67`
- active rows = `313`
- active blank `Signal` rows = `0`
- active blank `Setup Signal` rows = `0`
- active blank `Core Signal` rows = `0`
- active blank `Momentum Tag` rows = `0`

Observed active `Momentum Tag` distribution:

- `ELITE = 31`
- `STRONG = 31`
- `HEALTHY = 63`
- `NEUTRAL = 62`
- `WEAK = 63`
- `LAGGING = 63`

Conclusion:

- `Momentum Tag` is verified in a generated workbook

### Intraday validation warning interpretation

Verified target:

- `D:\screener-colab-appsheet\main scanner\gas_stock_tracker (5).xlsx`

Latest visible `Validation` row:

- `Snapshot At = 2026-04-21 11:04:13`
- `Mode = fresh-sample-12`
- `Checked Rows = 12`
- `Matched Rows = 0`
- `Mismatch Rows = 12`
- `Unresolved Rows = 0`
- `Status = WARN`

Recorded mismatch examples:

- `PRIVISCL`: `Current Price`, `RSI 14`, `RS vs NIFTY 1M%`, `RS vs NIFTY 3M%`
- `GRAPHITE`: `Current Price`, `1D%`, `1W%`, `RSI 14`
- `NATCOPHARM`: `Current Price`, `1D%`, `1W%`, `RSI 14`
- `UNIPARTS`: `Current Price`, `1D%`, `1W%`, `RSI 14`
- `RPTECH`: `Current Price`, `1D%`, `1W%`, `RSI 14`

Conclusion:

- this warning pattern is consistent with live intraday drift
- it is not evidence of a `Momentum Tag` bug
- it is not evidence of Dashboard schema shift
