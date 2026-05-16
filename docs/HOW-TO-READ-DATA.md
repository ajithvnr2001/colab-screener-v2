# How to Read the Screener Tracker Data

> GitHub reference for this file:
> `https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/HOW-TO-READ-DATA.md`
>
> Quick navigation:
> - [Docs README](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/README.md)
> - [Start Here Beginner Guide](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/START-HERE-BEGINNER-GUIDE.md)
> - [JSON Output Workflow](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/JSON-OUTPUT-WORKFLOW.md)
> - [Complete Column Glossary](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/COMPLETE-COLUMN-GLOSSARY.md)
> - [All Possible Scenarios](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/ALL-POSSIBLE-SCENARIOS.md)
> - [Practical Scenario Examples](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/PRACTICAL-SCENARIO-EXAMPLES.md)

Practical guide for reading the tracker output and using the Dashboard, scanner rows, and history sections correctly.

## Current JSON Format

The runnable tracker in this repository now writes JSON files instead of Excel files.

Primary files:

- `json_output/gas_stock_tracker_dashboard.json`
- `json_output/gas_stock_tracker.json`

Primary sections:

- `dashboard`: the main Dashboard rows
- `scanners`: scanner-specific rows grouped by scanner id
- `price_history`: append-only per-scanner snapshots
- `dashboard_history`: append-only Dashboard snapshots
- `validation`: run-level JSON validation rows
- `telegram`: Telegram send result for the run

Use `docs/JSON-OUTPUT-WORKFLOW.md` for exact run commands, Telegram configuration, and end-to-end test instructions.

For the exhaustive catalog of live-script labels and derived states, also read:

- `ALL-POSSIBLE-SCENARIOS.md`

For practical example combinations and what to do with them, also read:

- `PRACTICAL-SCENARIO-EXAMPLES.md`

For first-time onboarding, also read:

- `START-HERE-BEGINNER-GUIDE.md`

For the meaning of every workbook column, also read:

- `COMPLETE-COLUMN-GLOSSARY.md`

## AI Optimization Status

The current AI update did not add any new dependency.

- Python/package dependencies: unchanged
- AI providers: unchanged
- New pip installs required: none
- What changed: prompt instructions, BB/Camarilla-aware context, DI-gap context, AI cache key, JSON parsing fallback, and AI reason formatting

So the AI layer was optimized beyond the prompt, but the dependency stack did not increase.

## Dashboard Stability Fix (2026-04-11)

The dashboard update path now normalizes preserved Dashboard row values before they are reused.

- numeric Dashboard fields from older workbook rows are coerced back to numeric types
- inactive preserved rows no longer break ranking or sorting
- this fixes the dashboard rebuild error: `'<` not supported between instances of `str` and `int'`
- the fix changes stability only; it does not change the underlying signal math

## Iteration Flow Fix (2026-04-11)

The dashboard-only workbook export now copies only the real populated Dashboard range.

- `gas_stock_tracker_dashboard.xlsx` is generated from current Dashboard data only
- this reduces the chance of the loop stalling before Telegram/send/sleep
- intended live order is unchanged:
  - upload files
  - send Telegram status
  - sleep `60` seconds
  - start next iteration

## Enhanced Live Signal Upgrade (2026-04-17)

The raw live setup engine now defaults to the enhanced rule path.

- `SIGNAL_ENGINE = "enhanced"` is the active default
- `Setup Signal` now incorporates `+DI 14`, `-DI 14`, `NATR 14`, and Bollinger squeeze / stretch context
- the older stable rule path is still preserved as `Core Signal`
- off market, repeated runs still reuse `signal_snapshot_cache.json` for the completed session

Practical meaning:

- `Setup Signal` = the raw rule-engine label
- `Signal` = the final live label after predictive quality filtering
- `Core Signal` = the simpler trend-only reference

## Walk-Forward Predictive Signal Upgrade (2026-04-17)

The live tracker now adds a walk-forward evidence layer to reduce low-quality bullish setups.

New columns:

- `Signal Quality`
- `Signal Regime`
- `Win Prob%`
- `Hist Precision%`
- `Exp 5D%`
- `Exp 10D%`
- `WF Samples`

Method:

- replay recent historical bars using only information available at each bar
- use a trailing `320`-bar context window for each replay
- evaluate the most recent `180` eligible bars
- measure forward `5D` and `10D` returns after each historical setup
- prefer exact setup-label stats first
- fall back to signal-family stats when exact samples are too thin

Meaning:

- `Signal Regime = TRENDING` means current structure is healthy enough for normal trend-following confidence
- `Signal Regime = CHOPPY` means the current tape is mixed and needs more skepticism
- `Signal Regime = HIGH-VOL` means current normalized volatility is too hot for normal breakout confidence
- `Win Prob%` weights `5D` win rate at `40%` and `10D` win rate at `60%`
- `Hist Precision%` is the historical `10D` win rate of that exact/family setup bucket
- `Exp 5D%` and `Exp 10D%` are the average forward returns of those historical samples
- `WF Samples` is the number of usable walk-forward examples behind the row

Quality gate:

- bullish raw setups can be rejected even if `Setup Signal` says `BUY`, `STRONG BUY`, `BREAKOUT`, `PULLBACK`, or `OVERSOLD`
- rejected rows are converted into final `Signal` values such as `HOLD (High Vol)`, `HOLD (Choppy Regime)`, `HOLD (Thin History)`, or `HOLD (Low Quality)`
- `Signal Quality` reports whether the final live signal passed, failed, or could not be fully verified

## Relative Strength, Liquidity, And Validation Upgrade (2026-04-18)

The live workbook now adds benchmark-relative strength, liquidity screening, and automatic post-run self-validation.

New row-level columns:

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

How to read the new relative-strength fields:

- `Sector` and `Industry` come from Yahoo asset-profile metadata
- `Sector Benchmark` is the nearest NSE thematic benchmark the script could resolve for that normalized sector
- `RS vs NIFTY 1M%` / `3M%` show how much the stock outperformed or underperformed `^NSEI`
- `RS vs Sector 1M%` / `3M%` show how much the stock outperformed or underperformed its sector benchmark when one exists
- positive numbers are better
- negative numbers mean the stock is lagging that benchmark over that window
- `RS Tag` compresses the four comparisons into:
- `Strong vs Both`
- `RS Leader`
- `Mixed`
- `Weak RS`
- `Lagging`

How to read the new liquidity fields:

- `Avg Traded Value 20D Cr` is the stock's average recent daily traded value estimate in crores
- `Liquidity Tag` classifies that value:
- `Deep` for `>= 100 Cr`
- `Liquid` for `>= 20 Cr`
- `Adequate` for `>= 5 Cr`
- `Thin` for `>= 1 Cr`
- `Illiquid` for `< 1 Cr`

How these new fields affect interpretation:

- `Risk Tag` now penalizes weak relative strength and poor liquidity
- `Quick Action` is downgraded when liquidity is `Thin` / `Illiquid` or when `RS Tag` is `Weak RS` / `Lagging`
- `BUY NOW` now also expects non-negative `3M` relative strength vs NIFTY and sector when those comparisons exist

How to read the new `Validation` sheet:

- it exists only in the full workbook `gas_stock_tracker.xlsx`
- one row is appended after each successful Dashboard rebuild
- it is a run-freshness check, not a stock-selection table
- `Checked Rows` = sampled active rows compared against fresh recomputation
- `Matched Rows` = sampled rows with no differences
- `Mismatch Rows` = sampled rows where at least one checked field drifted
- `Unresolved Rows` = sampled rows where fresh Yahoo history could not be fetched
- `Latest Session` = latest completed market session date seen in the fresh histories
- `Status = PASS` means the sampled rows matched
- `Status = WARN` means at least one sampled row drifted
- `Status = SKIP` means validation was disabled or no eligible active rows existed
- `Details` summarizes which rows drifted or confirms that the sample matched

## Pre-Upgrade Active Dashboard Validation (2026-04-17)

The previous dashboard-only export was checked end-to-end against fresh Yahoo chart data before the predictive columns above were added.

- scope: `In Screener? = Yes` rows only
- `321` active rows were present in the validated export
- `318` active rows matched exactly on visible Dashboard metrics and on the then-live `Signal` plus `Core Signal`
- visible metrics checked:
- `Current Price`, `1D%`, `1W%`, `1M%`, `3M%`, `6M%`, `1Y%`
- `RSI 14`, `ADX 14`, `+DI 14`, `-DI 14`, `ATR 14`, `NATR 14`
- the remaining `3` active rows were already flagged correctly as unresolved-data states:
- `NDRINVIT` -> `No Data`
- `IWARE` -> `No Data`
- `PropsharePlatina` -> `Symbol Not Found`

Practical meaning:

- pre-upgrade active-row math was verified for that export
- this was the historical reference before the `2026-04-18` freshness fix and post-fix validation shown below

## Yahoo History Freshness Fix (2026-04-18)

The Yahoo history path was hardened after a real one-session-stale workbook was identified.

What happened in the stale workbook:

- `gas_stock_tracker_dashboard (12).xlsx` was structurally fine
- but many active rows were using `2026-04-16` closes while fresh Yahoo was already serving `2026-04-17` as the latest completed daily session
- that made prices, return columns, indicator columns, and live signals stale by one session

Concrete examples:

- `QPOWER`: workbook `1138.05` matched Yahoo `2026-04-16`; fresh Yahoo `2026-04-17` close was `1206.05`
- `GOODLUCK`: workbook `1187.00` matched Yahoo `2026-04-16`; fresh Yahoo `2026-04-17` close was `1229.05`
- `SCI`: workbook `288.93` matched Yahoo `2026-04-16`; fresh Yahoo `2026-04-17` close was `305.87`

Root cause:

- `fetch_history()` could accept `_yf_chart_history()` too early
- the code was not comparing that chart response against the `yfinance` fallback for freshness

Current fix:

- chart history and fallback history are both normalized into a common structure
- their last timestamps are compared
- the fresher dataset wins

Practical reading rule:

- if you are checking a fresh workbook after `2026-04-18`, active rows should now line up with the latest completed Yahoo daily session more reliably

## Post-Fix Active Dashboard Validation (2026-04-18)

The first post-fix dashboard-only workbook was then validated again end-to-end.

- validation target: `gas_stock_tracker_dashboard (13).xlsx`
- active rows in Dashboard: `372`
- exact full active-row matches: `370`
- active mismatch rows: `0`
- signal-layer mismatch rows: `0`
- expected active unresolved-data exceptions:
- `PropsharePlatina` -> `Symbol Not Found`
- `PARTH` -> `No Data`

What was checked:

- `Current Price`, `1D%`, `1W%`, `1M%`, `3M%`, `6M%`, `1Y%`
- `RSI 14`, `ADX 14`, `+DI 14`, `-DI 14`, `ATR 14`, `NATR 14`
- `Signal`, `Setup Signal`, `Core Signal`
- `Signal Quality`, `Signal Regime`
- `Win Prob%`, `Hist Precision%`, `Exp 5D%`, `Exp 10D%`, `WF Samples`

Practical meaning:

- `(12)` is the historical stale example
- `(13)` is the first clean post-fix reference export for active rows with resolved data

## Latest Workbook Verification Snapshot (2026-04-19)

The later workbook pair was also reviewed after the schema and AI-path expansion.

Dashboard-only export:

- target: `gas_stock_tracker_dashboard (15).xlsx`
- real Dashboard schema at that time: `66` columns
- total rows: `685`
- active rows: `359`
- inactive rows: `325`
- active rows with blank `Signal`: `0`
- active rows with blank `Setup Signal`: `0`
- active rows with blank `Core Signal`: `0`
- active rows with blank `AI Decision`: `2`
- those two active AI-blank rows were unresolved-data states already shown correctly:
- `PARTH` -> `No Data`
- one blank-symbol row -> `Symbol Not Found`

Full workbook:

- target: `gas_stock_tracker (4).xlsx`
- workbook sheet count: `257`
- latest visible `Validation` entries were both `PASS`
- stored workbook validation samples showed `2/2` and later `12/12` matched active rows
- the real populated `Dashboard` data matched the dashboard-only export on `66` headers and `685` rows

Low-severity note:

- the full-workbook `Dashboard` had a stale Excel used-range extending far to the right
- inspection showed those extra far-right cells were empty metadata artifacts, not shifted dashboard data
- the real `66` data columns remained aligned
- later code now adds one extra Dashboard readability column, `Momentum Tag`, so future exports will show `67` Dashboard columns

## Screener Pagination Fix (2026-04-11)

The live fetcher now reads all screener pages, not just page 1.

- if a screener has `page=2`, `page=3`, etc., those stocks are now included
- duplicates across pages are removed before processing

Practical meaning:

- `In Screener? = Yes` now reflects the full screen more accurately for multi-page screens

## Screener Startup Fetch Fix (2026-04-12)

The live startup fetch path was tightened for the current page-expanded screener list.

- explicit `page=1`, `page=2`, etc. URLs are now treated as single-page fetches
- auto-pagination only happens for non-paged screener URLs
- Phase 1 now shows progress while pages are being fetched

Practical meaning:

- the run should visibly progress during screener fetch instead of appearing stuck at startup

## Safe Phase 1 Speedup (2026-04-12)

The live tracker now speeds up screener fetch conservatively.

- screener fetch has its own worker limit
- Yahoo and AI worker counts are unchanged
- later pages in the same screen group are skipped after the first empty later page

Practical meaning:

- startup should finish faster without depending on aggressive request bursts

## Screener Auth Fail-Fast Fix (2026-04-12)

The live tracker now stops if Screener authentication fails.

- login/register pages are detected explicitly
- those pages are not counted as empty stock pages
- if Phase 1 has zero stocks because auth failed, the run aborts

Practical meaning:

- public screener URLs are fetched using their exact page query first
- the tracker no longer turns public fetch failures into a forced `[AUTH]` cookie message
- if Phase 1 gets zero stocks, the script stops instead of silently turning all fetches into zero-stock runs

## Where to Start

Open the `Dashboard` sheet first. It is the main decision view.

There are now two output workbooks:

- `gas_stock_tracker.xlsx`: full workbook
- `gas_stock_tracker_dashboard.xlsx`: Dashboard-only workbook

Both are regenerated on each successful iteration.

Use this trust order when reading any stock:

1. `In Screener?` must be `Yes` for active conviction.
2. `Signal` is the final technical decision layer.
3. `Setup Signal` shows the raw setup before predictive filtering.
4. `Core Signal` is the simpler base-rule cross-check.
5. `Signal Quality` and `Signal Regime` tell you whether the current setup passed the quality gate and what market regime it sits in.
6. `Win Prob%`, `Hist Precision%`, `Exp 5D%`, `Exp 10D%`, and `WF Samples` show the walk-forward evidence behind the setup.
7. `RS Tag`, `RS vs NIFTY 3M%`, `RS vs Sector 3M%`, `Avg Traded Value 20D Cr`, and `Liquidity Tag` tell you whether the stock is actually leading and tradeable.
8. `Risk Tag`, `BB Signal`, `Cam Setup`, and `Volume Buzz` refine entry quality.
9. `Momentum Rank` and `Momentum Tag` tell you how strong the row is versus the rest of the Dashboard right now.
10. `AI Decision` and `AI Conf%` are the second layer.
11. `Consensus Score` shows aggregated AI conviction.
12. `Quick Action` is the routing layer.
13. `Validation` sheet tells you whether the current run stayed aligned with fresh Yahoo data.

If a row is inactive, treat it as historical context, not a fresh setup.

Important live behavior:

- if `In Screener? = No`, the row is now frozen
- the script does not refresh AI or non-AI technical values for inactive scanner rows
- the Dashboard keeps the row, but marks it inactive
- Telegram now sends separate download links for the full workbook and the dashboard-only workbook

## AI Dependency Map

Runtime dependency reality:

- the AI layer currently uses `openai` plus `requests`
- Gemini also uses the native Google `generateContent` REST path for structured JSON output
- no new Python package was added by the recent AI improvements
- AI still needs internet access and valid provider credentials at runtime

Current AI controls in the script:

- `AI_ENABLED`
- `AI_PRIMARY`
- `AI_SECONDARY_ENABLED`
- `NVIDIA_NIM_API_KEYS`
- `NVIDIA_NIM_MODELS`
- `GEMINI_API_KEYS`
- `GEMINI_MODELS`
- `AI_TIMEOUT_SEC`
- `AI_MAX_RETRIES`
- `AI_DELAY_SEC`
- `AI_TEMPERATURE`
- `AI_TOP_P`
- `AI_MAX_TOKENS`

Current provider behavior:

- with `AI_SECONDARY_ENABLED = False`, the script stays inside the primary provider family only
- with `AI_SECONDARY_ENABLED = True`, the secondary provider family is tried only after the primary chain fails
- the current checked-in default is `AI_PRIMARY = "google"` with `AI_SECONDARY_ENABLED = False`
- multiple keys scale throughput inside the same provider without changing the decision logic
- Gemini uses native JSON-schema output with minimal thinking
- NVIDIA GLM-family routes are called with explicit thinking-disable hints
- if `AI_ENABLED = False`, the AI layer is skipped
- if `AI_ENABLED = True` but there is no valid provider, the technical layer still runs and AI outputs remain blank

These columns depend directly on AI:

- `AI Decision`
- `AI Reason`
- `AI Conf%`
- `Consensus Score`
- the AI-assisted part of `Quick Action`

Without AI:

- `Consensus Score` is blank.
- `Quick Action` usually falls back to `WATCH`, unless risk/quality logic forces a weaker warning state.
- Dashboard sorting by consensus becomes less useful.

These columns work without AI:

- `Symbol`, `Name`
- `MTF Alignment`
- `Historical MTF`
- `Sector`, `Industry`, `Sector Benchmark`
- `RS Tag`
- `RS vs NIFTY 1M%`, `RS vs NIFTY 3M%`
- `RS vs Sector 1M%`, `RS vs Sector 3M%`
- `Avg Traded Value 20D Cr`
- `Liquidity Tag`
- `Momentum Rank`
- `Momentum Tag`
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
- `Risk Tag`
- `BB Signal`
- `Cam Setup`
- `Volume Buzz`
- `Since Capture Trend`
- `First Captured`, `Last Seen`, `Days Tracked`
- `Total Appearances`, `Unique Scanners`, `Scanner List`, `Best Scanner`
- `Capture Price`, `Current Price`, `Since Capture%`
- `Cam H3`, `Cam H4`, `Cam L3`, `Cam L4`
- `Ideal Enter Price`, `Possible Sell Value`, `Stop Loss Value`
- `1D%`, `1W%`, `1M%`, `3M%`, `6M%`, `1Y%`
- `RSI 14`, `ADX 14`, `+DI 14`, `-DI 14`, `ATR 14`, `NATR 14`
- `Screener Link`, `Last Updated`

Important practical rule:

- blank AI fields do not mean the technical setup is wrong
- they only mean the optional second-opinion layer did not run or did not have a valid provider path

## AI Failure / Missing-AI Behavior

If AI is missing, disabled, or temporarily unavailable:

- `Signal`, `Setup Signal`, `Core Signal`, `Signal Quality`, `Signal Regime`, and the predictive stats still remain usable
- `AI Decision`, `AI Reason`, `AI Conf%`, and `Consensus Score` stay blank
- `Quick Action` usually falls back to `WATCH`
- stock-picking should then be based on the technical stack only

Do not do this:

- do not reject a good technical row only because AI fields are blank
- do not trust `WATCH` blindly in an AI-disabled workbook, because `WATCH` is often just the fallback label without consensus input

## Beginner Notes

If you are new to the workbook, do not start by scanning every number.

Start with:

1. `In Screener?`
2. final `Signal`
3. `Signal Quality`
4. `Signal Regime`
5. `Risk Tag`
6. `BB Signal`
7. `Cam Setup`
8. AI columns only after that

Important correction:

- `PASS - UNVERIFIED` is a `Signal Quality` value
- it is not part of `Signal Regime`

## How To Pick Stocks With AI Enabled

Use this order:

1. keep only `In Screener? = Yes`
2. skip `No Data`, `Symbol Not Found`, and `Error`
3. read `Signal` first, not `Setup Signal`
4. confirm that `Signal Quality` is not `REJECT - ...`
5. prefer `Signal Regime = TRENDING`
6. prefer `Win Prob% >= 55`, `Hist Precision% >= 55`, and positive `Exp 10D%`
7. prefer `WF Samples >= 5`
8. prefer `Risk Tag` not `HIGH`
9. prefer `RS Tag = Strong vs Both`, `RS Leader`, or at least not `Weak RS` / `Lagging`
10. prefer `Liquidity Tag = Deep`, `Liquid`, or at least `Adequate`
11. prefer `+DI 14 > -DI 14`
12. prefer `Volume Buzz` not `Low`
13. prefer supportive dashboard context:
- `BB Signal = SQUEEZE BREAK`, `SQUEEZE`, `BUY ZONE`, or a non-stretched constructive state
- `Cam Setup = SQUEEZE + H4 BREAK`, `WATCH H4 BREAK`, `SQUEEZE NEAR H4`, `OVERSOLD AT L3`, or `WATCH L3 SUPPORT`
14. then check AI alignment:
- `AI Decision` should be `BUY`, `STRONG BUY`, or `ACCUMULATE`
- `AI Conf% >= 65` is a good practical floor
- `Consensus Score >= 6` is stronger than mixed AI
15. then check `Quick Action`:
- `BUY NOW` is strongest
- `ACCUMULATE` is good
- `WATCH` means keep monitoring

Best AI-enabled rows usually look like this:

- `Signal = BREAKOUT`, `STRONG BUY`, or a strong `BUY`
- `Signal Quality = PASS - HIGH` or `PASS - MED`
- `Signal Regime = TRENDING`
- `RS Tag` not weak and liquidity not thin
- low or medium `Risk Tag`
- constructive `BB Signal` and `Cam Setup`
- bullish `AI Decision`
- `Consensus Score >= 6`

## How To Pick Stocks Without AI

If AI is off, simplify the process:

1. keep only `In Screener? = Yes`
2. ignore `AI Decision`, `AI Reason`, `AI Conf%`, and `Consensus Score`
3. treat `Quick Action` as a weak helper only
4. use the technical trust order:
- `Signal`
- `Setup Signal`
- `Core Signal`
- `Signal Quality`
- `Signal Regime`
- `Win Prob%`, `Hist Precision%`, `Exp 10D%`, `WF Samples`
- `RS Tag`, `RS vs NIFTY 3M%`, `RS vs Sector 3M%`
- `Avg Traded Value 20D Cr`, `Liquidity Tag`
- `Risk Tag`
- `BB Signal`
- `Cam Setup`
- `Volume Buzz`
- `MTF Alignment`
- `Historical MTF`
5. prefer rows where final `Signal` is bullish, the quality gate passed, the regime is not `HIGH-VOL`, and the predictive stats are not weak
6. prefer agreement between live scanner breadth (`MTF Alignment`) and price-based higher-timeframe structure (`Historical MTF`)

Best non-AI rows usually look like this:

- `Signal = BREAKOUT`, `STRONG BUY`, or `BUY`
- `Signal Quality = PASS - HIGH` or `PASS - MED`
- `Signal Regime = TRENDING`
- positive or at least non-weak relative strength
- usable liquidity
- `Risk Tag = LOW` or controlled `MED`
- `+DI 14 > -DI 14`
- constructive BB/Camarilla context
- acceptable walk-forward evidence

## Quick Action

`Quick Action` is the fastest summary of what to do now.

| Value | Meaning | Practical use |
|---|---|---|
| `BUY NOW` | Strong agreement across consensus, momentum, and risk | Candidate for immediate entry checklist |
| `ACCUMULATE` | Bullish, but not perfect | Build in stages or buy on dips |
| `WATCH` | Some promise, not enough confirmation | Keep on watchlist |
| `CAUTION` | Weak or conflicting setup | Avoid new entry or reduce size |
| `AVOID` | Bearish and/or high-risk setup | Stay away |

Treat `Quick Action` as a routing layer, not as an automatic trade instruction.

Current quality-aware behavior:

- if `Signal Quality` is a `REJECT - ...` state, `Quick Action` is forced down into `WATCH`, `CAUTION`, or `AVOID`
- `BUY NOW` now requires both strong consensus and a strong final technical signal
- `BUY NOW` is also blocked when `RS Tag` is weak/lagging or liquidity is thin/illiquid
- `ACCUMULATE` is downgraded when relative strength or liquidity is poor
- `HIGH-VOL` regime blocks normal `ACCUMULATE` behavior even if the raw setup looked bullish

## Consensus Score

`Consensus Score` runs from `1.0` to `10.0`.

| Range | Interpretation |
|---|---|
| `8.0-10.0` | Very strong bullish consensus |
| `6.0-7.9` | Bullish |
| `4.0-5.9` | Mixed / neutral |
| `1.0-3.9` | Bearish |

Use it with `Risk Tag`, `MTF Alignment`, and `Historical MTF`, not by itself.

## MTF Columns

`MTF Alignment` shows whether a stock is present across active `In Screener? = Yes` Daily, Weekly, and Monthly buckets inferred from scanner IDs.

Examples:

- `D✅ W✅ M✅`: highest conviction
- `D✅ W✅ M❌`: strong, but not full alignment
- `D✅ W❌ M❌`: short-term only
- `D❌ W✅ M✅`: better for swing or position views

Important current-config nuance:

- the checked-in `Variant-*` scanner IDs do not carry weekly or monthly tags, so they classify into the default `D` bucket
- because of that, `MTF Alignment` can legitimately remain `D`-heavy unless you add or rename scanners so the code can classify some as `W` or `M`
- do not read missing `W` / `M` scanner breadth as automatically bearish when your scanner naming/configuration itself does not provide those buckets

More aligned timeframes generally mean better persistence and fewer false positives.

`Historical MTF` uses the same `D/W/M` tick format, but it is now price-based instead of scanner-history-based.

Current meaning:

- `MTF Alignment` = live active scanner breadth across D / W / M buckets inferred from scanner IDs
- `Historical MTF` = actual Yahoo price history resampled into Daily / Weekly / Monthly bars and checked for constructive D / W / M structure

These two columns can diverge legitimately:

- stronger `MTF Alignment` with weaker `Historical MTF` means scanner breadth is live, but higher-timeframe price structure is weaker
- stronger `Historical MTF` with weaker `MTF Alignment` means price structure still looks healthier across D / W / M even though current scanner breadth is lighter

If `Historical MTF` is blank, treat that as missing or insufficient usable Yahoo history for the price-based D / W / M calculation.

## Risk Tag

`Risk Tag` compresses several warning signs into one label:

- `LOW`
- `MED`
- `HIGH`

Risk flags can include:

- `RSI > 78`
- `RSI < 30`
- `ADX < 16`
- `NATR` is hot
- `-DI > +DI` while ADX is already meaningful
- very near 52-week high
- very far below 52-week high

Use `HIGH` risk rows carefully, even when the setup still looks bullish.

## Volume Buzz

`Volume Buzz` is derived from `Vol Ratio 20`.

| Value | Approx meaning |
|---|---|
| `High` | Unusually strong participation |
| `Above Avg` | Confirming interest |
| `Normal` | Ordinary volume |
| `Low` | Weak participation |

Breakouts with poor volume are less reliable.

## Signal

`Signal` is the final rule-based technical output. It is not AI-generated.

Current live engine:

- `Signal` = final quality-gated live signal
- `Setup Signal` = enhanced raw setup engine
- `Core Signal` = older stable base-rule engine

Current default signal profile in `screener-colab-appsheet-parallel.py`:

- `balanced`

Also available:

- `precision` (experimental)
- `conservative`
- `aggressive`

Important note:

- `precision` is not the live default.
- It is kept only as an optional test profile because wider holdout backtests did not show strong enough generalization.
- For profile testing and report interpretation, use `backtest/HOW-TO-USE-BACKTEST.md`.

Raw setup family:

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

Additional final live labels from the quality gate:

- `HOLD (High Vol)`
- `HOLD (Choppy Regime)`
- `HOLD (Thin History)`
- `HOLD (Low Quality)`

How to interpret the three signal columns:

- `Signal` tells you what the tracker is willing to treat as the final live action label now.
- `Setup Signal` tells you what the raw engine wanted before the walk-forward gate.
- `Core Signal` tells you what the older baseline engine would have said without DI / NATR / Bollinger refinement.

How to interpret key final outcomes:

- `BREAKOUT`: strongest final continuation path. It already passed both the raw setup engine and the predictive gate.
- `STRONG BUY`: strong bullish structure that still passed the gate.
- `BUY`: constructive bullish structure with enough confirmation and acceptable predictive quality.
- `BUY (Squeeze)`: constructive bullish structure plus squeeze-to-expansion context.
- `HOLD (DI Weakness)`: price structure is still decent, but directional internals have weakened.
- `HOLD (High Vol)`: raw bullish setup exists, but current volatility regime is too hot.
- `HOLD (Choppy Regime)`: raw bullish setup exists, but current market structure is too mixed.
- `HOLD (Thin History)`: the setup did not have enough walk-forward evidence outside a clearly trending regime.
- `HOLD (Low Quality)`: the setup failed the probability / precision / expected-return gate.
- `SELL`: breakdown state.

Rule of thumb:

- Best long entries happen when final `Signal` and `AI Decision` both point bullish.
- Confidence is strongest when `Signal`, `Setup Signal`, and `Core Signal` also agree.
- If `Setup Signal` is bullish but final `Signal` is one of the quality-gated hold labels, respect the rejection.

## Signal Quality

`Signal Quality` explains whether the raw setup survived the predictive filter.

Exact families:

- `PASS - HIGH`
- `PASS - MED`
- `PASS - LOW`
- `PASS - UNVERIFIED`
- `N/A - NON-BULL`
- `REJECT - HIGH-VOL`
- `REJECT - CHOPPY`
- `REJECT - THIN HISTORY`
- `REJECT - LOW EDGE`

How to use it:

- `PASS - HIGH` is the cleanest live quality state.
- `PASS - MED` and `PASS - LOW` still passed, but with weaker evidence.
- `PASS - UNVERIFIED` means there was not enough usable walk-forward evidence to score the setup properly, so treat it more cautiously.
- `N/A - NON-BULL` means the row was not a bullish setup to begin with, so the bullish quality gate did not apply.
- any `REJECT - ...` state means the final `Signal` has already been downgraded and should be read as a blocked setup, not as a missed bullish signal.

## Signal Regime

`Signal Regime` classifies the current market texture of the row:

- `TRENDING`
- `CHOPPY`
- `HIGH-VOL`

How to use it:

- `TRENDING` is the cleanest regime for continuation and breakout setups.
- `CHOPPY` means even a raw `BUY` should be treated carefully.
- `HIGH-VOL` means the row is hot and more likely to whipsaw, so the quality gate becomes stricter.

## Predictive Columns

These columns come from the walk-forward replay layer:

- `Win Prob%`
- `Hist Precision%`
- `Exp 5D%`
- `Exp 10D%`
- `WF Samples`

Practical interpretation:

- higher `Win Prob%` is better
- higher `Hist Precision%` means the setup historically held up better over `10D`
- positive `Exp 5D%` and `Exp 10D%` are healthier than negative averages
- very low `WF Samples` means the row has thin evidence and should be trusted less

## BB Signal

`BB Signal` is the Dashboard Bollinger interpretation layer.

It uses:

- Bollinger `%B`
- Bollinger width
- width percentile over recent history
- squeeze state
- RSI context

Current values:

| Value | Meaning |
|---|---|
| `SELL ZONE` | Price is above the upper band and overbought |
| `SQUEEZE BREAK` | Compression is starting to expand upward |
| `STRETCHED` | Above the upper band, but not yet in the strongest sell zone |
| `NEAR HIGH` | Close to upper-band extension |
| `BUY ZONE` | Below the lower band with strong oversold context |
| `OVERSOLD` | Below the lower band, but not full reversal-quality |
| `SQUEEZE` | Volatility compression is present |
| `NORMAL` | No Bollinger extreme |

How to use it:

- `SQUEEZE` is a setup state.
- `SQUEEZE BREAK` is more actionable than plain `SQUEEZE`.
- `SELL ZONE` on a bullish row usually means "do not chase."

## Cam Setup

`Cam Setup` combines the Dashboard Bollinger state with daily Camarilla levels derived from the previous completed bar.

Common values:

- `SQUEEZE + H4 BREAK`
- `WATCH H4 BREAK`
- `SQUEEZE NEAR H4`
- `OVERSOLD AT L3`
- `OVERSOLD BELOW L4`
- `WATCH L3 SUPPORT`
- `UPPER BAND UNDER H4`
- `AT/ABOVE H4 RESISTANCE`
- neutral location states such as `INSIDE L3-H3`

How to use it:

- `SQUEEZE + H4 BREAK` is the cleanest Camarilla-confirmed breakout state.
- `WATCH H4 BREAK` means BB is constructive, but price still has not cleared the static breakout line.
- `OVERSOLD AT L3` is a cleaner dip-buy location than lower-band oversold by itself.
- `UPPER BAND UNDER H4` means the upper-band move is still below the static breakout ceiling.

## Camarilla Price Columns

The Dashboard also includes:

- `Cam H3`
- `Cam H4`
- `Cam L3`
- `Cam L4`
- `Ideal Enter Price`
- `Possible Sell Value`
- `Stop Loss Value`

How to read them:

- `Cam H4` is the main breakout trigger reference.
- `Cam H3` is the nearer upper resistance / pullback-fail line.
- `Cam L3` is the main dip-buy support reference.
- `Cam L4` is the breakdown / stop reference.
- `Possible Sell Value` is a derived target for this system, not a textbook `H5`.

## Momentum Rank

`Momentum Rank` is a relative ranking across the Dashboard.

It is based on weighted recent returns:

`1D x 3 + 1W x 2 + 1M x 1`

Lower rank number is better.

- Rank `1` is strongest momentum
- Top 10 to 20 percent is usually where leaders sit

Use it as a filter, not as a standalone buy signal.

## Momentum Tag

`Momentum Tag` is the quick-reading version of `Momentum Rank`.

It does not use a separate formula.

It is derived directly from the Dashboard rank percentile:

- `ELITE` = top `10%`
- `STRONG` = next `10%`
- `HEALTHY` = next `20%`
- `NEUTRAL` = middle `20%`
- `WEAK` = next `20%`
- `LAGGING` = bottom `20%`

How to use it:

- use `Momentum Rank` when you want exact ordering
- use `Momentum Tag` when you want a fast visual quality bucket
- do not treat `Momentum Tag` as a signal by itself
- `Momentum Tag` is appended at the end of the Dashboard schema so old workbook columns stay aligned on the first upgraded run
- the best long candidates usually combine:
- constructive final `Signal`
- non-rejected `Signal Quality`
- acceptable `Risk Tag`
- and `Momentum Tag = ELITE`, `STRONG`, or at least `HEALTHY`

## Scanner Sheets

Each scanner sheet now has `59` columns.

Main groups:

- Identity: `Symbol`, `Name`, `First Captured`, `Last Seen`, `In Screener?`
- Pricing: `Capture Price`, `Current Price`, `Since Capture%`
- Returns: `1D%`, `1W%`, `1M%`, `3M%`, `6M%`, `1Y%`, `2Y%`, `3Y%`
- Averages: `Avg Weekly%`, `Avg Monthly%`, `Avg 3M%`, `Avg 6M%`, `Avg 1Y%`
- Trend and momentum: `RSI 14`, `MA 20`, `MA 50`, `MA 200`
- Signal: `Signal`, `Setup Signal`, `Core Signal`
- Predictive: `Signal Quality`, `Signal Regime`, `Win Prob%`, `Hist Precision%`, `Exp 5D%`, `Exp 10D%`, `WF Samples`
- AI: `AI Decision`, `AI Reason`, `AI Conf%`
- Advanced: `ADX 14`, `+DI 14`, `-DI 14`, `ATR 14`, `NATR 14`, `Vol Ratio 20`, `MACD Line`, `MACD Hist`, `52W High Dist%`, `20D Breakout%`
- Meta: `Last Updated`

How to read the advanced indicators:

| Column | Meaning | Quick interpretation |
|---|---|---|
| `ADX 14` | Trend strength | Higher = stronger trend, not direction |
| `+DI 14 / -DI 14` | Directional control | `+DI > -DI` = bulls in control |
| `ATR 14 / NATR 14` | Volatility | Hot NATR = noisy setup |
| `Vol Ratio 20` | Relative volume | Higher = stronger participation |
| `MACD Line` | Trend direction | Positive is bullish bias |
| `MACD Hist` | Momentum acceleration | Positive and rising is strongest |
| `52W High Dist%` | Distance from 52-week high | Lower means closer to breakout territory |
| `20D Breakout%` | Distance above prior 20-day high | Positive means breakout is active |

If you want the exhaustive meaning of all scanner, Dashboard, `Price History`, and `Dashboard History` columns, use:

- `COMPLETE-COLUMN-GLOSSARY.md`

## Price History and Dashboard History

`Price History` is append-only and now has `51` columns. It stores per-scanner snapshots, including the raw Camarilla reference levels, relative-strength/liquidity fields, and the predictive signal-quality fields.

`Dashboard History` is append-only and now has `55` columns. It stores full Dashboard snapshots over time, including the final `Signal`, raw `Setup Signal`, `Core Signal`, relative-strength/liquidity columns, and the walk-forward evidence fields.

Use them to:

- track when a stock moved from `WATCH` to `BUY NOW`
- track consensus changes
- track risk changes
- inspect how `Cam H3/H4/L3/L4` moved relative to the chosen entry/target/stop
- study persistence across time

## Reading After the Signal Hardening Updates

The current build improved both indicator accuracy and signal quality.

What changed in practical terms:

| Area | Current behavior |
|---|---|
| OHLCV parsing | Row-aligned before indicator calculation |
| MA validity | Full lookback required |
| RSI edge cases | Flat series handled correctly |
| ADX usage | Trend strength only, with DI added for direction |
| Volatility filter | `NATR` now helps reject overly noisy setups |
| Squeeze logic | Uses rolling width percentile, not a fixed width threshold |
| Predictive gate | Walk-forward evidence can block raw bullish setups |
| Camarilla layer | Dashboard now maps BB states against `H3/H4/L3/L4` from the previous completed bar |
| No Data rows | Technical and AI fields are cleared |
| AI consensus | Active rows only |

## Minimal Entry Checklist (AI Enabled)

For a cleaner long entry, prefer all of the following:

1. `In Screener? = Yes`
2. `Signal` is `BUY` or better
3. `Signal Quality` is not a `REJECT - ...` state
4. `Signal Regime` is preferably `TRENDING` and not `HIGH-VOL`
5. `Win Prob%` and `Hist Precision%` are comfortably above mid-50s
6. `Exp 10D%` is positive
7. `AI Decision` is bullish
8. `AI Conf% >= 65`
9. `Consensus Score >= 6`
10. `Risk Tag` is not `HIGH`
11. `Volume Buzz` is not `Low`
12. `+DI > -DI`
13. `NATR` is not excessively hot

If several of these fail, keep the stock in watch mode.

## Minimal Entry Checklist (AI Disabled)

For a cleaner long entry without AI, prefer:

1. `In Screener? = Yes`
2. `Signal` is `BUY` or better
3. `Signal Quality` is not a `REJECT - ...` state
4. `Signal Regime` is preferably `TRENDING` and not `HIGH-VOL`
5. `Win Prob%` and `Hist Precision%` are comfortably above mid-50s
6. `Exp 10D%` is positive
7. `WF Samples` is not thin
8. `Risk Tag` is not `HIGH`
9. `Volume Buzz` is not `Low`
10. `+DI > -DI`
11. `NATR` is not excessively hot
12. `BB Signal` and `Cam Setup` are constructive, not stretched/failing
13. `MTF Alignment` and `Historical MTF` are not contradicting the long case

If several of these fail, keep the row as a watchlist candidate only.

## False-Signal Reduction Rules

When market conditions are choppy:

- respect final `Signal` over raw `Setup Signal`
- reject any row where `Signal Quality` already says `REJECT - ...`
- filter out `Risk Tag = HIGH`
- prefer `Consensus Score >= 6`
- prefer at least 2 timeframe confirmations
- avoid overextended `BB Signal` states unless you are trading mean reversion

When market conditions are trending:

- prefer `Signal Quality = PASS - HIGH` or `PASS - MED`
- keep ADX and DI confirmation as baseline
- prefer `SQUEEZE BREAK` over plain `SQUEEZE`
- give more weight to repeated active appearances across scanners

Profile reminder:

- start from `balanced`
- use `conservative` if you want fewer signals
- use `aggressive` only for earlier exploratory entries
- use `precision` only as an experiment, not as the baseline default

## What Not to Assume

This system can reduce false positives from data or logic issues, but it cannot eliminate market risk.

It does not protect against:

- gap risk
- earnings or event shocks
- index-wide risk-off moves
- low-liquidity traps
- regime shifts

Use the Dashboard as a decision aid, not as a substitute for risk management.

## April 21, 2026 Reading Update

Two newer things are now confirmed.

### 1. `Momentum Tag` is verified in a generated workbook

Verified file:

- `gas_stock_tracker_dashboard (16).xlsx`

Verified facts:

- Dashboard columns = `67`
- active rows = `313`
- active blank `Momentum Tag` rows = `0`
- active blank `Signal` / `Setup Signal` / `Core Signal` rows = `0`

Observed active `Momentum Tag` counts:

- `ELITE = 31`
- `STRONG = 31`
- `HEALTHY = 63`
- `NEUTRAL = 62`
- `WEAK = 63`
- `LAGGING = 63`

So `Momentum Tag` is no longer a code-only feature. It is verified in live workbook output.

### 2. `Validation = WARN` can be normal during market hours

Verified file:

- `gas_stock_tracker (5).xlsx`

Latest visible `Validation` row:

- `Checked Rows = 12`
- `Matched Rows = 0`
- `Mismatch Rows = 12`
- `Unresolved Rows = 0`
- `Status = WARN`

Why that happened:

- the run was checked during market hours
- fresh validation compares live-sensitive fields
- sampled rows drifted on:
- `Current Price`
- `1D%`
- `1W%`
- `RSI 14`
- benchmark-relative strength fields

How to read that correctly:

- this does **not** automatically mean the workbook is broken
- this does **not** mean the `Momentum Tag` addition caused a failure
- it means sampled rows moved while the validator was refetching fresh Yahoo data

Best practice:

- use market-hours `WARN` as a freshness caution
- use off-market `PASS` as the strict confirmation standard
