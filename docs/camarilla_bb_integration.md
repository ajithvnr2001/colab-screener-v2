# Camarilla + Bollinger Integration Plan

This is the corrected implementation plan for integrating Camarilla Pivot Points with the existing Bollinger-based dashboard logic in `D:\screener-colab-appsheet\screener-colab-appsheet-parallel.py`.

## AI Optimization Status

The later AI optimization pass did not change Camarilla math and did not add new dependencies.

- Dependencies: unchanged
- Providers: unchanged
- Camarilla impact: only richer AI interpretation context
- Additional AI optimization: prompt structure, cache key, JSON repair, and explanation preservation

## Dashboard Stability Fix (2026-04-11)

The Dashboard reuse path now normalizes preserved Dashboard values before ranking and sorting.

- old numeric Dashboard cells are coerced back to numeric types
- inactive preserved rows no longer trigger mixed-type dashboard failures
- this fixes the runtime error: `'<` not supported between instances of `str` and `int'`
- Camarilla math itself is unchanged by this fix

## Iteration Loop Behavior (2026-04-11)

The live tracker loop that contains the Camarilla + Bollinger Dashboard layer now completes each successful cycle in this order:

- upload `gas_stock_tracker.xlsx`
- build and upload `gas_stock_tracker_dashboard.xlsx`
- send Telegram status with both download links
- sleep `60` seconds
- start the next iteration

The dashboard-only workbook is now built from the real populated `Dashboard` range only, which reduces the chance of the run stalling before Telegram/send/sleep.

## Predictive Signal Quality Upgrade (2026-04-17)

The later predictive upgrade does not change Camarilla math.

What it does change:

- the Dashboard now also carries `Signal`, `Setup Signal`, and `Core Signal` as separate concepts
- the Dashboard now shows `Signal Quality`, `Signal Regime`, `Win Prob%`, `Hist Precision%`, `Exp 5D%`, `Exp 10D%`, and `WF Samples`
- `Quick Action` can now be downgraded even when BB + Camarilla context is constructive, if the predictive gate rejects the raw bullish setup

Practical implication:

- `Cam Setup` still tells you where price sits relative to the BB + Camarilla execution map
- final `Signal` still has priority over `Cam Setup` when the predictive gate has already blocked the trade

## Yahoo History Freshness Fix (2026-04-18)

The later Yahoo freshness fix does not change Camarilla math, but it does matter for how the Dashboard reads BB + Camarilla context.

What changed:

- the script now compares chart vs fallback Yahoo history and keeps the fresher dataset
- this fixes the one-session-stale case seen in `gas_stock_tracker_dashboard (12).xlsx`

Practical Camarilla implication:

- `Cam H3/H4/L3/L4` are still derived from the previous completed daily bar
- but the current comparison price used by the Dashboard now comes from the fresher latest completed Yahoo session more reliably
- that means `Cam Setup`, `BB Signal`, and the live price-vs-level interpretation are less likely to lag by one session

## Latest Workbook Verification Context (2026-04-19)

The later verified workbook pair also confirmed that the Camarilla + BB layer remained structurally aligned after the larger schema changes.

- `gas_stock_tracker_dashboard (15).xlsx` kept the real `66`-column Dashboard layout intact
- `gas_stock_tracker (4).xlsx` kept the same real Dashboard content, and its latest visible `Validation` rows both showed `PASS`
- the full workbook had a bloated Excel used-range on the Dashboard sheet, but the actual populated Camarilla / BB columns were still aligned correctly

The previous draft was not 100% accurate. These were the main issues:

- It called `H - L` "true range". That is incorrect here. This implementation uses the previous bar's plain range, not ATR-style true range.
- It described a helper using the latest bar's `H/L/C` while also saying "previous closed day". For a live/current bar comparison, that is inconsistent.
- It presented `H5/L5` as if they were standard textbook Camarilla levels. They are not consistent across references, so they should not be treated as canonical in this project.
- It implied the feature could be added without schema work. In this codebase, Dashboard integration requires explicit header updates.

## Correct mathematical basis

For a daily dashboard using the latest available close as the comparison price:

- Use the previous completed daily bar as the Camarilla reference bar.
- Use the latest close as the current comparison price.

Definitions:

- `H_prev` = previous completed bar high
- `L_prev` = previous completed bar low
- `C_prev` = previous completed bar close
- `R` = `H_prev - L_prev`

Canonical levels:

- `H3 = C_prev + (R * 1.1) / 4`
- `H4 = C_prev + (R * 1.1) / 2`
- `L3 = C_prev - (R * 1.1) / 4`
- `L4 = C_prev - (R * 1.1) / 2`

Notes:

- Only `H3`, `H4`, `L3`, and `L4` are treated as canonical here.
- Any upside projection beyond `H4` is labeled as a derived target, not as textbook `H5`.

## Implemented architecture

The feature is implemented in the main script as a Dashboard-layer strategy overlay:

1. `calc_camarilla(...)`
- Added beside the other indicator helpers.
- Uses `highs[-2]`, `lows[-2]`, and `closes[-2]` as the reference bar.
- Returns `Cam H3`, `Cam H4`, `Cam L3`, `Cam L4`.

2. Phase 3 cache
- Added `_cam_data` alongside `_bb_data`.
- Camarilla levels are computed during the Yahoo history pass and cached by symbol.

3. Dashboard schema
- Added Dashboard columns:
  - `Cam Setup`
  - `Cam H3`
  - `Cam H4`
  - `Cam L3`
  - `Cam L4`
  - `Ideal Enter Price`
  - `Possible Sell Value`
  - `Stop Loss Value`

4. Dashboard history
- Added `Cam Setup`, `Ideal Enter Price`, `Possible Sell Value`, and `Stop Loss Value` to Dashboard History.

Current live schema after the predictive upgrade:

- scanner sheets: `59` columns
- `Price History`: `51` columns
- `Dashboard`: `67` columns
- `Dashboard History`: `55` columns

Later readability addition:

- `Momentum Tag` was added to the Dashboard only
- it is appended at the end of the Dashboard schema so legacy Dashboard columns remain aligned
- it does not change any Camarilla or Bollinger calculation
- it only makes the momentum layer easier to read beside `Cam Setup`

## Implemented BB + Camarilla logic

The integration is deterministic and limited to Dashboard interpretation. It does not rewrite the core scanner-sheet schema.

### Breakout path

When Bollinger indicates squeeze expansion:

- `BB Signal = SQUEEZE BREAK`
- If price is above `H4`: `Cam Setup = SQUEEZE + H4 BREAK`
- Otherwise: `Cam Setup = WATCH H4 BREAK`

Execution values:

- `Ideal Enter Price = H4`
- `Possible Sell Value = H4 + (H4 - H3)` as a derived extension target
- `Stop Loss Value = H3 - 0.2% buffer`

### Dip-buy path

When Bollinger indicates lower-band exhaustion:

- `BB Signal = BUY ZONE` or `OVERSOLD`
- If price is at or below `L3`: `Cam Setup = OVERSOLD AT L3`
- If price is below `L4`: `Cam Setup = OVERSOLD BELOW L4`
- Otherwise: `Cam Setup = WATCH L3 SUPPORT`

Execution values:

- `Ideal Enter Price = L3`
- `Possible Sell Value = H3`
- `Stop Loss Value = L4 - 0.2% buffer`

### Resistance / fake-out path

When Bollinger is stretched near the upper band:

- If price is between `H3` and `H4`: `Cam Setup = UPPER BAND UNDER H4`
- If price is at or above `H4`: `Cam Setup = AT/ABOVE H4 RESISTANCE`

This is an interpretation layer only. It does not auto-generate a new short-side execution model.

### Neutral path

If there is no BB extreme, the dashboard still shows Camarilla location:

- `ABOVE H4`
- `BETWEEN H3-H4`
- `INSIDE L3-H3`
- `BETWEEN L4-L3`
- `BELOW L4`

## Why this version is correct for this repo

- It matches the existing architecture, where Bollinger is already a Dashboard-only context layer via `_bb_data`.
- It avoids inventing unsupported textbook claims.
- It keeps scanner sheets stable while still surfacing execution-grade Camarilla information in the Dashboard.
- It makes the derived target explicit instead of incorrectly naming it `H5`.

## Current status

- This integration remains part of the current main script.
- The main script default signal profile is `balanced`.
- The optional `precision` signal profile does not change the Camarilla math itself; it only changes how selective the underlying rule-based signal becomes.
- The later predictive quality gate also does not change Camarilla math itself; it only changes whether a raw bullish setup is allowed to stay bullish as the final live `Signal`.
- `Historical MTF` is now a separate price-based Daily / Weekly / Monthly field from resampled Yahoo history; this does not change the Camarilla math or the BB + Camarilla execution layer.
- For profile comparison and holdout testing, use `backtest/HOW-TO-USE-BACKTEST.md`.
- The Dashboard now also has an `In Screener?` column, and inactive rows are kept as frozen context instead of being re-evaluated.
- Each successful iteration now also produces a dashboard-only workbook:
  - `gas_stock_tracker_dashboard.xlsx`
- The full workbook remains:
  - `gas_stock_tracker.xlsx`

## Using BB + Camarilla With And Without AI

With AI enabled:

- use `Signal` first, then `Signal Quality`, then `Signal Regime`
- use `BB Signal` and `Cam Setup` to refine timing
- then use `AI Decision`, `AI Conf%`, and `Consensus Score` as the second-opinion layer
- best aligned breakout state:
  - `Signal = BREAKOUT`
  - `BB Signal = SQUEEZE BREAK`
  - `Cam Setup = SQUEEZE + H4 BREAK`
  - bullish AI alignment

With AI disabled:

- use the same BB + Camarilla context, but ignore AI fields
- `Quick Action` becomes much less informative because consensus is blank
- treat `Cam Setup` as an execution/timing layer, not as a replacement for the final `Signal`

## Validation status

After implementation, validate with:

1. `python -m py_compile D:\screener-colab-appsheet\screener-colab-appsheet-parallel.py`
2. Open a regenerated workbook and confirm the new Dashboard columns appear.
3. Confirm BB + Camarilla rows still make sense when predictive rejection happens:
   - example: `Setup Signal = BREAKOUT` but final `Signal = HOLD (High Vol)` should still keep a constructive `Cam Setup`, but must not be treated as a clean live breakout
4. Spot-check a few symbols:
   - `SQUEEZE BREAK` names should show `WATCH H4 BREAK` or `SQUEEZE + H4 BREAK`
   - lower-band oversold names should show `WATCH L3 SUPPORT`, `OVERSOLD AT L3`, or `OVERSOLD BELOW L4`
   - stretched upper-band names below `H4` should show `UPPER BAND UNDER H4`
5. Freshness check after `2026-04-18`:
   - active workbook rows should line up with the latest completed Yahoo daily session
   - the verified clean post-fix reference export is `gas_stock_tracker_dashboard (13).xlsx`

## April 21, 2026 note

Two later observations are relevant to BB/Camarilla reading but do not change the logic itself.

### `Momentum Tag` output is verified

The newer Dashboard export `gas_stock_tracker_dashboard (16).xlsx` confirmed:

- `Momentum Tag` is present
- active blank `Momentum Tag` rows = `0`

This does not change BB/Camarilla interpretation. It only makes Dashboard scanning easier.

### Intraday `Validation = WARN` is not a BB/Camarilla bug by itself

The corresponding full workbook `gas_stock_tracker (5).xlsx` later showed:

- `Checked Rows = 12`
- `Matched Rows = 0`
- `Mismatch Rows = 12`
- `Unresolved Rows = 0`
- `Status = WARN`

The mismatch details were concentrated in live-moving fields like price, short returns, `RSI 14`, and benchmark-relative strength.

So:

- do not blame BB/Camarilla logic just because a market-hours validation row says `WARN`
- read that warning first as an intraday drift signal unless the mismatch set points somewhere else
