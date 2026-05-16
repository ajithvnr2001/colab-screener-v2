# Practical Scenario Examples

This is the companion to:

- `ALL-POSSIBLE-SCENARIOS.md`
- `HOW-TO-READ-DATA.md`

This file is intentionally practical. It shows the most important live workbook combinations and how to read them fast.

## AI Optimization Status

The latest AI work was an optimization pass, not a dependency expansion.

- Dependencies: unchanged
- Providers: unchanged
- New installs: none
- Improved areas: prompt structure, BB/Camarilla context, DI-gap context, cache-key safety, response parsing, and reason text retention

## Dashboard Stability Fix (2026-04-11)

The live dashboard path now normalizes preserved Dashboard row values before reusing them.

- numeric fields from older workbook rows are coerced back to numeric types
- inactive preserved rows no longer crash momentum ranking or consensus sorting
- this fixes the runtime error: `'<` not supported between instances of `str` and `int'`

## Iteration Loop Behavior (2026-04-11)

Each successful live run now ends in this order:

- upload `gas_stock_tracker.xlsx`
- build and upload `gas_stock_tracker_dashboard.xlsx`
- send Telegram status with both links
- sleep `60` seconds
- start the next iteration

So if the loop is healthy, you should keep receiving the Telegram status and both files every cycle.

Output files for each successful iteration:

- `gas_stock_tracker.xlsx`
- `gas_stock_tracker_dashboard.xlsx`

## Walk-Forward Predictive Signal Upgrade (2026-04-17)

The live technical stack now has three signal layers:

- `Signal` = final live label after predictive filtering
- `Setup Signal` = raw enhanced-engine setup label
- `Core Signal` = older stable baseline

New fields you will now see on strong rows:

- `Signal Quality`
- `Signal Regime`
- `Win Prob%`
- `Hist Precision%`
- `Exp 5D%`
- `Exp 10D%`
- `WF Samples`

Practical rule:

- if `Setup Signal` is bullish but final `Signal` has been downgraded to `HOLD (High Vol)`, `HOLD (Choppy Regime)`, `HOLD (Thin History)`, or `HOLD (Low Quality)`, respect the downgrade
- the raw setup is then only a watch candidate, not a clean live long

## Relative Strength, Liquidity, And Validation Upgrade (2026-04-18)

The practical row-reading flow now also includes:

- `RS Tag`
- `RS vs NIFTY 3M%`
- `RS vs Sector 3M%`
- `Avg Traded Value 20D Cr`
- `Liquidity Tag`
- the full-workbook `Validation` sheet

Practical rule:

- if two rows both look technically bullish, prefer the one with stronger relative strength and better liquidity
- if the `Validation` sheet is showing `WARN` on the latest run, be more careful about treating that workbook as fully fresh

## Yahoo History Freshness Fix (2026-04-18)

One historical workbook showed why freshness matters.

- `gas_stock_tracker_dashboard (12).xlsx` was not structurally broken
- but many active rows matched Yahoo `2026-04-16` while fresh Yahoo had already moved to `2026-04-17`
- that made prices, returns, indicators, and live signals stale by one completed session

Examples:

- `QPOWER`: workbook `1138.05` matched `2026-04-16`; fresh Yahoo `2026-04-17` close was `1206.05`
- `GOODLUCK`: workbook `1187.00` matched `2026-04-16`; fresh Yahoo `2026-04-17` close was `1229.05`
- `SCI`: workbook `288.93` matched `2026-04-16`; fresh Yahoo `2026-04-17` close was `305.87`

Current behavior:

- the script now compares chart vs fallback history and keeps the fresher dataset

## Post-Fix Dashboard Validation (2026-04-18)

The next dashboard-only export after the freshness fix was verified clean for active rows with resolved data.

- validation target: `gas_stock_tracker_dashboard (13).xlsx`
- `372` active rows
- `370` exact active matches
- `0` active mismatch rows
- expected unresolved-data active rows:
- `PropsharePlatina` -> `Symbol Not Found`
- `PARTH` -> `No Data`

## Latest Workbook Pair Verification (2026-04-19)

The later workbook pair was also checked after the schema and AI-provider changes.

Dashboard-only file:

- target: `gas_stock_tracker_dashboard (15).xlsx`
- real Dashboard schema at that time: `66` columns
- `359` active rows
- `0` active blank `Signal`
- `0` active blank `Setup Signal`
- `0` active blank `Core Signal`
- only `2` active rows had blank AI, and those were already unresolved-data rows:
- `PARTH`
- one blank-symbol `Symbol Not Found` row

Full workbook:

- target: `gas_stock_tracker (4).xlsx`
- `257` sheets
- latest visible `Validation` rows were both `PASS`
- the real populated `Dashboard` matched the dashboard-only export on the `66` meaningful columns
- later code now adds one extra Dashboard readability column, `Momentum Tag`, so future exports will show `67` Dashboard columns

Low-severity note:

- the full-workbook `Dashboard` carried a stale Excel used-range far to the right
- inspection showed that was empty-cell metadata, not shifted Dashboard data

## How To Use This File

Read a row in this order:

1. `In Screener?`
2. `Signal`
3. `Setup Signal`
4. `Core Signal`
5. `Signal Quality`
6. `Signal Regime`
7. `Win Prob%`, `Hist Precision%`, `Exp 10D%`, `WF Samples`
8. `RS Tag`, `RS vs NIFTY 3M%`, `RS vs Sector 3M%`
9. `Avg Traded Value 20D Cr`, `Liquidity Tag`
10. `Momentum Rank`, `Momentum Tag`
11. `Risk Tag`
12. `BB Signal`
13. `Cam Setup`
14. `Volume Buzz`
15. `MTF Alignment`
16. `Historical MTF`
17. `Quick Action`

If AI is disabled, ignore:

- `AI Decision`
- `AI Conf%`
- `Consensus Score`

and treat `Quick Action` mostly as a fallback watchlist label.

If `In Screener? = No`, stop there first. That row is no longer being actively refreshed.

Use `MTF Alignment` for live active-now scanner conviction and `Historical MTF` for price-based D / W / M trend context.

If final `Signal` is weaker than `Setup Signal`, the predictive gate is intentionally rejecting the raw setup.

## 1. Best Breakout Continuation

Typical row:

- `Signal = BREAKOUT`
- `Setup Signal = BREAKOUT`
- `Signal Quality = PASS - HIGH` or `PASS - MED`
- `Signal Regime = TRENDING`
- `RS Tag = Strong vs Both` or `RS Leader`
- `Liquidity Tag` not thin
- `Risk Tag = LOW`
- `BB Signal = SQUEEZE BREAK`
- `Cam Setup = SQUEEZE + H4 BREAK`
- `Volume Buzz = High` or `Above Avg`
- `MTF Alignment = D✅ W✅ M✅` or at least `D✅ W✅ M❌`
- `Historical MTF` should ideally also look constructive, but it can diverge legitimately from `MTF Alignment`
- `Quick Action = BUY NOW` or `ACCUMULATE`

Meaning:

- This is the cleanest momentum continuation case in the live script.
- Price structure, breakout context, volume, and dashboard interpretation all agree.
- Best case is when both live scanner breadth and price-based D / W / M structure confirm each other.

Practical read:

- strongest long candidate
- better than a plain `BUY`
- better than a stretched overbought move without squeeze confirmation

## 2. Early Breakout Watch

Typical row:

- `Signal = BUY (Squeeze)` or `BUY`
- `Signal Quality` not `REJECT - ...`
- `RS Tag` at least not weak
- `Liquidity Tag` at least `Adequate`
- `BB Signal = SQUEEZE`
- `Cam Setup = WATCH H4 BREAK` or `SQUEEZE NEAR H4`
- `Risk Tag = LOW` or `MED`
- `Volume Buzz = Normal` or better

Meaning:

- Setup is constructive, but the breakout is not fully confirmed yet.
- This is earlier than `BREAKOUT`.

Practical read:

- keep on watchlist
- useful when you want early entries, but conviction is lower than a full breakout

## 3. High-Quality Dip Buy

Typical row:

- `Signal = STRONG BUY (Oversold)`
- `Signal Quality` not `REJECT - ...`
- `RS Tag` not weak
- `Liquidity Tag` not thin
- `BB Signal = BUY ZONE`
- `Cam Setup = OVERSOLD AT L3`
- `Risk Tag = LOW` or controlled `MED`
- `Volume Buzz` not `Low`

Meaning:

- Price has corrected, but structure is still strong enough for a dip-buy interpretation.
- This is the cleanest reversal-style long scenario.

Practical read:

- better than generic `OVERSOLD`
- better when it happens near `L3` instead of below `L4`

## 4. Weak Oversold Watch

Typical row:

- `Signal = OVERSOLD` or `OVERSOLD (Watch)`
- `RS Tag = Weak RS` or mixed leadership is common here
- `Liquidity Tag` can be weaker here than in premium setups
- `BB Signal = OVERSOLD`
- `Cam Setup = WATCH L3 SUPPORT` or `OVERSOLD BELOW L4`
- `Risk Tag = MED` or `HIGH`

Meaning:

- Price is washed out, but the structure is weaker than the high-quality dip-buy case.
- The script is telling you this is a watch, not a clean entry.

Practical read:

- not a strong buy
- useful only if it stabilizes and improves on later runs

## 5. Standard Bullish Trend

Typical row:

- `Signal = BUY`
- `Signal Quality = PASS - HIGH`, `PASS - MED`, or `PASS - LOW`
- `Signal Regime` preferably `TRENDING`
- `Risk Tag = LOW`
- `BB Signal = NORMAL`
- `Cam Setup = INSIDE L3-H3`
- `Volume Buzz = Normal` or `Above Avg`
- `MTF Alignment` has at least two active timeframes

Meaning:

- Good normal bullish structure without breakout urgency.
- This is the most ordinary healthy long scenario.

Practical read:

- acceptable long candidate
- less explosive than `BREAKOUT`
- less attractive than `STRONG BUY`

## 6. Pullback In Uptrend

Typical row:

- `Signal = PULLBACK`
- `Risk Tag = LOW` or `MED`
- `BB Signal = NORMAL` or `OVERSOLD`
- `Cam Setup = INSIDE L3-H3` or `WATCH L3 SUPPORT`

Meaning:

- Price has pulled back inside a constructive structure.
- The move is not a breakdown yet.

Practical read:

- dip-entry watch
- better than `WEAK`
- not as strong as `STRONG BUY (Oversold)`

## 7. Healthy Trend But Do Not Chase

Typical row:

- `Signal = HOLD (Overbought)`
- `BB Signal = SELL ZONE`, `STRETCHED`, or `NEAR HIGH`
- `Cam Setup = UPPER BAND UNDER H4` or `AT/ABOVE H4 RESISTANCE`
- `Risk Tag = MED` or `HIGH`

Meaning:

- Trend may still be up, but entry timing is poor.
- The script is warning against chasing extension.

Practical read:

- not a fresh long
- better to wait for pullback or reset

## 8. Trend Weakening Internally

Typical row:

- `Signal = HOLD (DI Weakness)`
- `Risk Tag = MED`
- `BB Signal = NORMAL` or `STRETCHED`
- `Cam Setup = INSIDE L3-H3` or upper-zone state

Meaning:

- Price has not fully broken down, but directional internals are weakening.
- This is an early warning state.

Practical read:

- reduce conviction
- avoid treating this as a strong entry

## 9. Below MA200 Caution Case

Typical row:

- `Signal = HOLD (Below MA200)`
- `Risk Tag = MED` or `HIGH`
- `BB Signal` can still look constructive
- `Cam Setup` can still show support or resistance structure

Meaning:

- Shorter-term structure may look acceptable, but the long-term trend filter is not supportive.

Practical read:

- lower-quality long setup
- suitable only for cautious tracking, not aggressive entry

## 10. Weak Structure

Typical row:

- `Signal = WEAK`
- `Risk Tag = MED`
- `BB Signal = NORMAL`
- `Volume Buzz = Low` or `Normal`

Meaning:

- The stock is not broken enough to be a clean bearish failure, but not strong enough to be a useful bullish setup.

Practical read:

- low-priority watchlist candidate
- usually skip unless other conditions improve later

## 11. Bearish / Avoid Case

Typical row:

- `Signal = SELL`
- `Risk Tag = HIGH`
- `Quick Action = CAUTION` or `AVOID`
- `BB Signal` not supportive
- `Cam Setup` often below central structure or failing support

Meaning:

- This is the script’s clear “do not treat as a long” state.

Practical read:

- avoid long entry
- if you are only using the workbook for long ideas, skip it

## 12. Best Long-Term Compounder Case

Typical row:

- `MTF Alignment = D✅ W✅ M✅`
- `Signal = BUY`, `STRONG BUY`, or `BREAKOUT`
- `Risk Tag = LOW`
- `Quick Action = BUY NOW` or `ACCUMULATE`
- `Since Capture Trend = Gaining` or `Strong Gain`

Meaning:

- Multi-timeframe alignment plus low risk is the best durability combination.

Practical read:

- strongest swing or position candidate
- usually better than a one-timeframe fast mover

## 13. Fast Momentum But Risky

Typical row:

- `Signal = BUY` or `BREAKOUT`
- `Risk Tag = HIGH`
- `BB Signal = STRETCHED` or `SELL ZONE`
- `Since Capture Trend = Strong Gain`

Meaning:

- Momentum is present, but the move may be late or overheated.

Practical read:

- not automatically bad
- but it is a poor chase entry

## 14. AI Agrees With Technicals

Typical row:

- `Signal = BUY`, `STRONG BUY`, or `BREAKOUT`
- `AI Decision = BUY` or `STRONG BUY`
- `Consensus Score >= 6`
- `Quick Action = BUY NOW` or `ACCUMULATE`

Meaning:

- Rule engine and AI overlay both point in the same direction.

Practical read:

- highest conviction among AI-enabled rows
- still check `Risk Tag` before acting

## 15. AI Disagrees With Technicals

Typical row:

- `Signal = BUY` or `BREAKOUT`
- `Signal Quality = PASS - HIGH` or `PASS - MED`
- `AI Decision = HOLD`, `REDUCE`, or `SELL`
- `Consensus Score` weak or mixed
- `Quick Action` downgraded to `WATCH` or `CAUTION`

Meaning:

- Structure looks technically positive, but the AI layer sees a weaker situation.

Practical read:

- reduce conviction by one level
- do not treat it like a best-in-class setup

## 16. AI Disabled Scenario

Typical row:

- `Signal` populated
- `AI Decision` blank
- `AI Conf%` blank
- `Consensus Score` blank
- `Quick Action = WATCH`

Meaning:

- The technical engine still works normally.
- Only the AI aggregation layer is missing.

Practical read:

- rely on `Signal`, `Risk Tag`, `BB Signal`, and `Cam Setup`
- do not overread `Quick Action`

## 17. Fresh Capture Scenario

Typical row:

- `Days Tracked = 0`
- `Since Capture% = 0`
- `First Captured` and `Last Seen` are almost the same timestamp

Meaning:

- This is a newly captured stock.
- It has no live follow-through history inside your workbook yet.

Practical read:

- use current technical quality, not capture-performance history

## 18. Mature Tracked Winner

Typical row:

- `Days Tracked` is meaningful
- `Since Capture Trend = Gaining` or `Strong Gain`
- `Total Appearances` and `Unique Scanners` are high

Meaning:

- The stock has stayed relevant across multiple runs.
- This is stronger than a one-off appearance.

Practical read:

- persistence adds credibility
- especially useful when aligned with `LOW` risk and bullish signal

## 19. One-Off Scanner Appearance

Typical row:

- `Total Appearances = 1`
- `Unique Scanners = 1`
- `MTF Alignment` weak, even if `Historical MTF` is broader

Meaning:

- Stock has only appeared once and from one scanner context.
- Even if `Historical MTF` looks broader, treat that as price-structure context rather than proof of repeated scanner history.

Practical read:

- lower trust than repeated multi-scanner presence

## 20. Data Problem Scenario

Typical row:

- `Signal = No Data`
- or `Signal = Symbol Not Found`
- or `Signal = Error`

Meaning:

- This is not a market opinion.
- It is a pipeline/data state.

Practical read:

- do not analyze it as bullish or bearish
- fix symbol resolution or rerun later

## 21. Inactive Dashboard Row

Typical row:

- `In Screener? = No`
- previous `Signal` / `AI Decision` / `BB Signal` values still visible
- row still appears in `Dashboard`

Meaning:

- The stock was tracked before, but it is not active in the current run.
- The script now freezes inactive rows instead of recalculating them.

Practical read:

- treat as historical context
- do not read it as a fresh current setup
- use it for memory, not for a new entry

## 22. Fast Decision Shortcut

Use this shortcut when scanning quickly.

Best bullish scenario:

- `BREAKOUT + SQUEEZE BREAK + SQUEEZE + H4 BREAK + LOW risk`

Best dip-buy scenario:

- `STRONG BUY (Oversold) + BUY ZONE + OVERSOLD AT L3`

Do-not-chase scenario:

- `HOLD (Overbought) + SELL ZONE`

Avoid scenario:

- `SELL` or `HOLD (Below MA200)` with `HIGH` risk

Ignore scenario:

- `No Data`
- `Symbol Not Found`
- `Error`

## 23. Best Practice

Do not make decisions from one field alone.

Good rows usually have agreement across:

- `Signal`
- `Setup Signal`
- `Signal Quality`
- `Signal Regime`
- `Win Prob%`
- `Hist Precision%`
- `Risk Tag`
- `BB Signal`
- `Cam Setup`
- `Volume Buzz`
- `MTF Alignment`
- `Historical MTF`

The strongest rows are the ones where live scanner breadth and price-based D / W / M structure agree in the same direction.

## 24. Raw BUY Rejected By Choppy Regime

Typical row:

- `Setup Signal = BUY`
- `Signal = HOLD (Choppy Regime)`
- `Signal Quality = REJECT - CHOPPY`
- `Signal Regime = CHOPPY`
- `Risk Tag = MED`

Meaning:

- The raw structure looked constructive, but the current tape is too mixed.
- The script is explicitly blocking a low-quality long.

Practical read:

- do not treat this like a normal `BUY`
- keep it on watch only if other conditions improve later

## 25. Raw Breakout Rejected By High Volatility

Typical row:

- `Setup Signal = BREAKOUT` or `STRONG BUY`
- `Signal = HOLD (High Vol)`
- `Signal Quality = REJECT - HIGH-VOL`
- `Signal Regime = HIGH-VOL`
- `BB Signal` can still look bullish

Meaning:

- Price may still be moving fast in the right direction, but the volatility regime is too hot.
- The tracker is telling you the breakout is statistically harder to trust right now.

Practical read:

- avoid chasing
- wait for volatility to normalize or for a cleaner reset

## 26. Raw Bullish Setup Rejected By Weak Edge

Typical row:

- `Setup Signal = BUY`, `STRONG BUY`, or `PULLBACK`
- `Signal = HOLD (Low Quality)`
- `Signal Quality = REJECT - LOW EDGE`
- `Win Prob%` weak or only marginal
- `Hist Precision%` weak or `Exp 10D%` poor

Meaning:

- The raw setup exists, but its historical forward performance is not good enough.

Practical read:

- treat as filtered out
- this is exactly the kind of row the predictive layer is meant to remove

## 27. Thin-History Bullish Setup

Typical row:

- `Setup Signal = BUY` or `OVERSOLD`
- `Signal = HOLD (Thin History)` or `Signal Quality = PASS - UNVERIFIED`
- `WF Samples` very low

Meaning:

- The tracker does not have enough similar historical examples to score the setup confidently.

Practical read:

- use extra caution
- thin evidence is not the same as strong evidence

## 28. AI-Enabled Best Pick Workflow

Typical row:

- `In Screener? = Yes`
- `Signal = BREAKOUT`, `STRONG BUY`, or strong `BUY`
- `Signal Quality = PASS - HIGH` or `PASS - MED`
- `Signal Regime = TRENDING`
- `Risk Tag = LOW` or controlled `MED`
- `AI Decision = BUY`, `STRONG BUY`, or `ACCUMULATE`
- `AI Conf% >= 65`
- `Consensus Score >= 6`
- `Quick Action = BUY NOW` or `ACCUMULATE`

Meaning:

- both the technical engine and the optional AI overlay point in the same direction

Practical read:

- highest-priority shortlist candidate in an AI-enabled workbook
- still check BB/Camarilla and volume context before acting

## 29. AI-Disabled Best Pick Workflow

Typical row:

- `In Screener? = Yes`
- `Signal = BREAKOUT`, `STRONG BUY`, or `BUY`
- `Signal Quality = PASS - HIGH` or `PASS - MED`
- `Signal Regime = TRENDING`
- `Win Prob%`, `Hist Precision%`, and `Exp 10D%` are healthy
- `Risk Tag` not `HIGH`
- `Volume Buzz` not `Low`
- `AI Decision` blank
- `Consensus Score` blank
- `Quick Action = WATCH`

Meaning:

- the technical stack is still strong, but the AI overlay did not run

Practical read:

- do not reject the row only because `Quick Action` is weak
- trust the technical stack first

## 30. AI Strongly Agrees With Final Signal

Typical row:

- bullish final `Signal`
- `AI Decision` equally bullish or stronger
- `Consensus Score >= 7`
- `Quick Action = BUY NOW`

Meaning:

- this is the cleanest AI-confirmed scenario

Practical read:

- strongest combined-conviction case
- best when risk is still controlled and BB/Camarilla context is constructive

## 31. AI Missing But Technicals Still Good

Typical row:

- `Signal` populated and bullish
- `Signal Quality` passed
- `Signal Regime` acceptable
- `AI Decision` blank
- `AI Conf%` blank
- `Consensus Score` blank
- `Quick Action = WATCH`

Meaning:

- AI was disabled, unavailable, or skipped
- the technical setup itself can still be completely valid

Practical read:

- judge the stock from `Signal`, predictive stats, risk, BB, Camarilla, and MTF context
- do not downgrade it automatically just because AI fields are blank

## Practical Example: Verified `Momentum Tag` Output (2026-04-21)

Workbook:

- `gas_stock_tracker_dashboard (16).xlsx`

Observed facts:

- Dashboard columns = `67`
- active rows = `313`
- active blank `Momentum Tag` rows = `0`

Observed active distribution:

- `ELITE = 31`
- `STRONG = 31`
- `HEALTHY = 63`
- `NEUTRAL = 62`
- `WEAK = 63`
- `LAGGING = 63`

Practical use:

- sort by `Momentum Rank`
- use `Momentum Tag` to discard obviously weak momentum groups quickly
- do not treat `Momentum Tag` by itself as a buy trigger

## Practical Example: Intraday `Validation = WARN` (2026-04-21)

Workbook:

- `gas_stock_tracker (5).xlsx`

Latest visible validation row:

- `Checked Rows = 12`
- `Matched Rows = 0`
- `Mismatch Rows = 12`
- `Unresolved Rows = 0`
- `Status = WARN`

Mismatch details included:

- `PRIVISCL`
- `GRAPHITE`
- `NATCOPHARM`
- `UNIPARTS`
- `RPTECH`

And the mismatched fields were mostly:

- `Current Price`
- `1D%`
- `1W%`
- `RSI 14`
- benchmark-relative-strength fields

Practical meaning:

- this is what a live-session drift warning looks like
- not every `WARN` means the workbook is broken
- if the market is open, expect fresh validation to be harsher
