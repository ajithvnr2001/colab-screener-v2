# All Possible Scenarios Guide

Code-derived reference for the live script:

- `screener-colab-appsheet-parallel.py`

This guide is about the live workbook output, not the backtest. It covers the exact scenario families the script can produce and how to interpret them.

## AI Optimization Status

The AI-layer optimization in the live script did not increase dependencies.

- Same providers: NVIDIA NIM + Gemini
- Same package footprint: no new pip dependency added
- Optimization scope: prompt logic, richer context passed to AI, cache-key hardening, JSON repair, and better explanation preservation

## Dashboard Stability Fix (2026-04-11)

The live dashboard rebuild now normalizes preserved Dashboard values before reuse.

- older workbook numeric cells are coerced back into numeric types
- inactive preserved rows remain safe to rank, sort, color, and append into history
- this removes the mixed-type dashboard crash: `'<` not supported between instances of `str` and `int'`

## Iteration Loop Behavior (2026-04-11)

Each successful live iteration now follows this order:

- upload `gas_stock_tracker.xlsx`
- build and upload `gas_stock_tracker_dashboard.xlsx` from the real populated `Dashboard` range only
- send Telegram status with both download links
- sleep `60` seconds
- start the next iteration and repeat

This is a live-tracker loop behavior change, not a signal-logic change.

## Walk-Forward Predictive Signal Upgrade (2026-04-17)

The live script now has a predictive signal-quality layer on top of the rule engine.

Current technical stack:

- `Setup Signal` = raw enhanced rule-engine output
- `Signal` = final live label after the predictive quality gate
- `Core Signal` = older stable base-rule reference

New predictive columns:

- `Signal Quality`
- `Signal Regime`
- `Win Prob%`
- `Hist Precision%`
- `Exp 5D%`
- `Exp 10D%`
- `WF Samples`

Current method:

- replay recent bars using only historical information available at each bar
- use a trailing `320`-bar context window for each replay
- evaluate the most recent `180` eligible bars
- measure forward `5D` and `10D` returns from each historical setup
- use exact-label statistics first
- fall back to the broader signal family when exact-label coverage is too thin

Current predictive meanings:

- `Signal Regime = TRENDING`
- `Signal Regime = CHOPPY`
- `Signal Regime = HIGH-VOL`
- `Win Prob%` = weighted blend of `5D` and `10D` win rates
- `Hist Precision%` = historical `10D` win rate for the chosen exact/family setup bucket
- `Exp 5D%` / `Exp 10D%` = average forward returns of those historical samples
- `WF Samples` = number of walk-forward examples behind the row

Quality gate behavior:

- bullish raw setups can be downgraded into final `Signal` values like `HOLD (High Vol)`, `HOLD (Choppy Regime)`, `HOLD (Thin History)`, or `HOLD (Low Quality)`
- `Signal Quality` now reports `PASS - HIGH`, `PASS - MED`, `PASS - LOW`, `PASS - UNVERIFIED`, `N/A - NON-BULL`, or `REJECT - ...`
- this is a stricter live filter, not a claim of perfect prediction

## Relative Strength, Liquidity, And Validation Upgrade (2026-04-18)

The live script now has three additional scenario layers:

- sector-aware relative strength
- liquidity quality screening
- automatic post-run self-validation

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

New run-level sheet:

- `Validation`

Current relative-strength label family:

- `Strong vs Both`
- `RS Leader`
- `Mixed`
- `Weak RS`
- `Lagging`
- `—`

Current liquidity label family:

- `Deep`
- `Liquid`
- `Adequate`
- `Thin`
- `Illiquid`
- `—`

Current validation status family:

- `PASS`
- `WARN`
- `SKIP`

## Validation Notes

Historical pre-upgrade reference (`2026-04-17`):

- the previous dashboard-only export had `321` active rows
- `318` active rows matched exactly on visible Dashboard metrics plus both `Signal` and `Core Signal`
- the remaining `3` active unresolved-data rows were:
- `NDRINVIT` -> `No Data`
- `IWARE` -> `No Data`
- `PropsharePlatina` -> `Symbol Not Found`

Freshness bug reference (`2026-04-18`):

- `gas_stock_tracker_dashboard (12).xlsx` was not random corruption
- it was largely one completed trading session stale on many active rows
- examples:
- `QPOWER`: workbook `1138.05` matched Yahoo `2026-04-16`, while fresh Yahoo `2026-04-17` close was `1206.05`
- `GOODLUCK`: workbook `1187.00` matched Yahoo `2026-04-16`, while fresh Yahoo `2026-04-17` close was `1229.05`
- `SCI`: workbook `288.93` matched Yahoo `2026-04-16`, while fresh Yahoo `2026-04-17` close was `305.87`
- root cause: chart history could be accepted before the fallback path was checked for fresher data

Current post-fix reference (`2026-04-18`):

- validation target: `gas_stock_tracker_dashboard (13).xlsx`
- `372` active rows were present
- `370` active rows matched exactly on prices, returns, indicators, signal fields, and predictive fields
- `0` active mismatch rows were found
- expected active unresolved-data cases:
- `PropsharePlatina` -> `Symbol Not Found`
- `PARTH` -> `No Data`

Practical meaning:

- treat `(12)` as the stale historical example
- treat `(13)` as the first clean post-fix reference export for active rows with resolved data

Latest structural verification reference (`2026-04-19`):

- dashboard-only target: `gas_stock_tracker_dashboard (15).xlsx`
- full-workbook target: `gas_stock_tracker (4).xlsx`
- the real Dashboard schema remained `66` columns
- the later dashboard-only export had `359` active rows with:
- `0` blank active `Signal`
- `0` blank active `Setup Signal`
- `0` blank active `Core Signal`
- only `2` blank active `AI Decision` rows, both unresolved-data cases:
- `PARTH`
- one blank-symbol `Symbol Not Found` row
- the later full workbook kept matching real Dashboard content and its latest visible `Validation` rows both said `PASS`
- the full workbook carried a stale far-right Excel used-range, but that was empty-cell metadata, not shifted Dashboard data

## Scope

The live script produces scenarios in five layers:

1. Scanner row lifecycle
2. Raw rule-based setup signal
3. Predictive quality gate
4. Dashboard interpretation layers
5. AI overlay

It also produces two workbook artifacts on each successful iteration:

- `gas_stock_tracker.xlsx`
- `gas_stock_tracker_dashboard.xlsx`

If you want the short practical reader, use:

- `HOW-TO-READ-DATA.md`

If you are completely new to the tracker, start with:

- `START-HERE-BEGINNER-GUIDE.md`

If you want the exact meaning of every workbook column, use:

- `COMPLETE-COLUMN-GLOSSARY.md`

If you want example-driven combinations, use:

- `PRACTICAL-SCENARIO-EXAMPLES.md`

If you want the exhaustive label catalog, use this file.

## 1. Scanner Row Lifecycle

Every symbol row on a scanner sheet is in one of these practical states.

| State | Where seen | Meaning |
|---|---|---|
| `In Screener? = Yes` | Scanner sheets | Symbol is currently present in that screener |
| `In Screener? = No` | Scanner sheets | Symbol was seen before but is not in the latest fetch |
| `Signal = Pending...` | Scanner sheets during processing | Temporary processing state before Yahoo metrics are written |
| `Signal = No Data` | Scanner sheets | Symbol resolved, but usable market history could not be computed |
| `Signal = Symbol Not Found` | Scanner sheets | Screener row could not be mapped to a valid Yahoo symbol |
| `Signal = Error` | Scanner sheets | Runtime error while processing that symbol |

Use `In Screener? = Yes` first. If it is `No`, the row is historical context, not a fresh live setup.

Important implementation detail:

- inactive scanner rows are frozen
- the script does not refresh their AI or non-AI runtime values
- the Dashboard still shows them, but marks them `In Screener? = No`

## 2. Rule-Based Signal Scenarios

The default live profile is:

- `balanced`

Other profiles:

- `precision`
- `conservative`
- `aggressive`

The label family stays mostly the same across profiles, but thresholds change. `precision` is stricter and may suppress weaker bearish outputs.

Current live signal wiring:

- `Signal` = final quality-gated live signal
- `Setup Signal` = enhanced raw rule engine
- `Core Signal` = older stable base-rule engine

Operationally, read `Signal` first, then `Setup Signal`, then `Core Signal`.

### Exact Signal Family

These are the live signal outcomes that matter operationally.

| Signal | Meaning | Typical interpretation |
|---|---|---|
| `BREAKOUT` | Full bullish stack with breakout confirmation | Highest-quality continuation setup |
| `STRONG BUY (Oversold)` | Strong bullish structure after a controlled oversold reset | Strong dip-buy scenario |
| `STRONG BUY` | Strong bullish structure with trend confirmation | High-quality long setup |
| `BUY (Squeeze)` | Bullish setup with squeeze context | Breakout watch with early trigger |
| `BUY` | Valid bullish setup, not as strong as breakout or strong buy | Standard long candidate |
| `HOLD (Overbought)` | Uptrend remains, but stretched or extended | Do not chase fresh entry |
| `HOLD (DI Weakness)` | Price still looks acceptable, but directional internals are weakening | Reduce conviction |
| `HOLD` | Neutral to mildly constructive | Watch, not a strong entry |
| `HOLD (Below MA200)` | Structure is not strong enough relative to long-term trend | Avoid aggressive long entry |
| `PULLBACK` | Pullback within a still-constructive structure | Buy-on-dip candidate, not breakout |
| `OVERSOLD` | Oversold while still having some structural support | Reversal watch |
| `OVERSOLD (Watch)` | Oversold in weaker structure | Watch only, not immediate action |
| `WEAK` | Mixed or underpowered trend structure | Low conviction |
| `SELL` | Clear bearish structure | Avoid long or treat as breakdown state |
| `No Data` | No usable metrics | Ignore until data issue is resolved |

### Signal Logic Summary

The signal engine combines:

- MA structure: `MA 20`, `MA 50`, `MA 200`
- momentum: `RSI 14`
- trend strength: `ADX 14`
- direction: `+DI 14`, `-DI 14`
- participation: `Vol Ratio 20`
- acceleration: `MACD Line`, `MACD Hist`
- proximity to highs: `52W High Dist%`
- breakout state: `20D Breakout%`
- volatility filter: `NATR 14`
- Bollinger context: `%B`, squeeze, width percentile

### Predictive Quality Gate Scenarios

The quality gate only downgrades bullish raw setups. It does not rewrite clearly bearish or neutral ones.

Exact `Signal Quality` families:

| Signal Quality | Meaning |
|---|---|
| `PASS - HIGH` | Best live predictive quality bucket |
| `PASS - MED` | Good enough to pass, but not elite |
| `PASS - LOW` | Passed with weaker evidence |
| `PASS - UNVERIFIED` | Not enough usable walk-forward evidence to score properly |
| `N/A - NON-BULL` | Raw setup was not bullish, so bullish quality gate does not apply |
| `REJECT - HIGH-VOL` | Current volatility regime is too hot |
| `REJECT - CHOPPY` | Market structure is too mixed |
| `REJECT - THIN HISTORY` | Too few walk-forward examples outside a clearly trending regime |
| `REJECT - LOW EDGE` | Win rate / precision / expected return failed the gate |

Exact quality-reject final labels:

| Final Signal | Meaning |
|---|---|
| `HOLD (High Vol)` | Raw bullish setup blocked by hot volatility |
| `HOLD (Choppy Regime)` | Raw bullish setup blocked by mixed regime |
| `HOLD (Thin History)` | Raw bullish setup blocked by weak sample support |
| `HOLD (Low Quality)` | Raw bullish setup blocked by weak predictive edge |

### Regime Classification

Current live regime family:

| Signal Regime | Meaning |
|---|---|
| `TRENDING` | Trend stack, ADX, and DI context are healthy enough for normal trend-following confidence |
| `CHOPPY` | Current tape is mixed and more likely to whipsaw |
| `HIGH-VOL` | Current normalized volatility is too hot for normal breakout confidence |

### Best-Quality Bullish Path

The cleanest continuation setup is usually:

- `Signal = BREAKOUT`
- `Setup Signal = BREAKOUT`
- `Signal Quality = PASS - HIGH` or `PASS - MED`
- `Signal Regime = TRENDING`
- above `MA 20`, `MA 50`, and `MA 200`
- strong `ADX`
- positive `MACD Line` and `MACD Hist`
- good `Vol Ratio 20`
- positive `+DI` over `-DI`
- acceptable `NATR`
- supportive Bollinger state

### Weak / Avoid Paths

Lowest-quality long setups usually involve:

- `HOLD (High Vol)`
- `HOLD (Choppy Regime)`
- `HOLD (Thin History)`
- `HOLD (Low Quality)`
- `HOLD (Below MA200)`
- `WEAK`
- `OVERSOLD (Watch)`
- `SELL`
- or any row with `No Data`, `Error`, or `Symbol Not Found`

## 3. Dashboard Scenario Layers

The Dashboard adds interpretation layers on top of the raw signal.

### 3.0 Dashboard `In Screener?`

The Dashboard now also carries:

- `In Screener? = Yes`
- `In Screener? = No`

Meaning:

- `Yes`: stock is active in at least one scanner in the current run
- `No`: stock is retained for context, but is not active in the current run

Current behavior:

- `Yes` rows can be refreshed by new Yahoo/AI results
- `No` rows keep their last live values and should be treated as historical context

### 3.1 Quick Action

`Quick Action` is a routing layer built from:

- `Consensus Score`
- final `Signal`
- `Signal Quality`
- `Signal Regime`
- `Win Prob%`
- timeframe alignment
- momentum ranking
- relative strength
- liquidity
- risk tag

Exact family:

| Quick Action | Meaning |
|---|---|
| `BUY NOW` | Strongest aggregated live setup |
| `ACCUMULATE` | Bullish, but better to scale in |
| `WATCH` | Worth tracking, not strong enough for immediate action |
| `CAUTION` | Weak or conflicting setup |
| `AVOID` | Low consensus plus high risk |

Current dashboard logic:

- quality-gated `REJECT - ...` rows are forced down into `WATCH`, `CAUTION`, or `AVOID`
- `BUY NOW`: `Consensus Score >= 7`, at least 2 timeframes, top 30 percent momentum rank, not `HIGH` risk
- `BUY NOW` also prefers `Signal` family `BREAKOUT` or `STRONG BUY` and decent `Win Prob%`
- `BUY NOW` also expects non-negative `3M` relative strength vs NIFTY and sector when those values exist
- `ACCUMULATE`: `Consensus Score >= 6`, at least 2 timeframes, not `HIGH` risk, final `Signal` still bullish, and regime not `HIGH-VOL`
- weak / lagging relative strength or thin / illiquid liquidity force the row down into `CAUTION` or `AVOID`
- `WATCH`: `Consensus Score >= 5` and not `HIGH` risk, or fallback when AI is absent
- `CAUTION`: `Consensus Score < 4`
- `AVOID`: `Consensus Score < 4` and `Risk Tag = HIGH`

Without AI:

- `Consensus Score` is blank
- `Quick Action` usually falls back to `WATCH`, unless risk/quality rules already force a weaker warning state

### 3.2 Consensus Score

`Consensus Score` is derived from AI decision votes.

AI score map:

- `STRONG BUY = 3`
- `BUY = 2`
- `ACCUMULATE = 1`
- `HOLD = 0`
- `REDUCE = -1`
- `SELL = -2`
- `STRONG SELL = -3`

The dashboard maps the average AI score into a `1.0` to `10.0` range.

Practical ranges:

| Range | Interpretation |
|---|---|
| `8.0-10.0` | Very strong bullish AI consensus |
| `6.0-7.9` | Bullish consensus |
| `4.0-5.9` | Mixed |
| `1.0-3.9` | Bearish consensus |

### 3.2A Predictive Columns

Current predictive families shown directly on the Dashboard:

| Column | Meaning |
|---|---|
| `Signal Quality` | Whether the raw setup passed the predictive gate |
| `Signal Regime` | Current market texture of the row |
| `Win Prob%` | Weighted forward win-rate estimate from walk-forward replay |

### 3.2B Relative-Strength Columns

Current relative-strength families shown directly on the live workbook:

| Column | Meaning |
|---|---|
| `Sector` | Normalized Yahoo sector used for benchmark mapping |
| `Industry` | Yahoo industry text for human context |
| `Sector Benchmark` | NSE thematic benchmark used for sector-relative comparison when available |
| `RS Tag` | Compressed leadership label from the four RS comparisons |
| `RS vs NIFTY 1M%` | 1-month stock return minus 1-month NIFTY return |
| `RS vs NIFTY 3M%` | 3-month stock return minus 3-month NIFTY return |
| `RS vs Sector 1M%` | 1-month stock return minus 1-month sector benchmark return |
| `RS vs Sector 3M%` | 3-month stock return minus 3-month sector benchmark return |

Practical interpretation:

- `Strong vs Both` = leader vs both broad market and sector
- `RS Leader` = mostly healthy leadership
- `Mixed` = not clean leadership
- `Weak RS` = weak leadership
- `Lagging` = clear benchmark underperformance

### 3.2C Liquidity Columns

Current liquidity families shown directly on the live workbook:

| Column | Meaning |
|---|---|
| `Avg Traded Value 20D Cr` | Average daily traded-value estimate in crores |
| `Liquidity Tag` | Compressed liquidity label |

Practical interpretation:

- `Deep` / `Liquid` = best practical tradeability
- `Adequate` = usable
- `Thin` / `Illiquid` = more slippage / noisier action / lower Dashboard conviction

### 3.2D Validation Sheet

Current `Validation` families:

| Status | Meaning |
|---|---|
| `PASS` | Sampled active rows matched fresh recomputation |
| `WARN` | At least one sampled active row drifted |
| `SKIP` | Validation disabled or no eligible active rows |

Current validation behavior:

- runs after each successful Dashboard rebuild
- samples active `Dashboard` rows across the sheet, not only the very top rows
- refetches fresh stock history and fresh benchmark history
- compares prices, indicators, signal-layer fields, relative-strength fields, and liquidity fields
| `Hist Precision%` | Historical `10D` win rate of the setup bucket |
| `Exp 5D%` | Average `5D` forward return of the setup bucket |
| `Exp 10D%` | Average `10D` forward return of the setup bucket |
| `WF Samples` | Number of historical samples behind the estimates |

Operational use:

- final `Signal` matters more than raw `Setup Signal`
- if `Setup Signal` is bullish but `Signal Quality` says `REJECT - ...`, trust the final downgraded `Signal`
- treat low `WF Samples` as weaker evidence

### 3.3 MTF Alignment

`MTF Alignment` shows whether the stock appears in active scanners across:

- Daily
- Weekly
- Monthly

All possible normalized combinations:

| Alignment | Meaning |
|---|---|
| `D✅ W✅ M✅` | Full multi-timeframe alignment |
| `D✅ W✅ M❌` | Daily + weekly aligned |
| `D✅ W❌ M✅` | Daily + monthly aligned |
| `D❌ W✅ M✅` | Weekly + monthly aligned |
| `D✅ W❌ M❌` | Daily only |
| `D❌ W✅ M❌` | Weekly only |
| `D❌ W❌ M✅` | Monthly only |
| `D❌ W❌ M❌` | Should be rare and usually not meaningful |

More aligned timeframes usually mean more persistent trends.

`Historical MTF` uses the same format, but it is now derived from actual Yahoo price history resampled into Daily / Weekly / Monthly bars.

So the two fields now mean different things:

- `MTF Alignment` = live active scanner breadth
- `Historical MTF` = price-based D / W / M structure

When `Historical MTF` is stronger than `MTF Alignment`, the stock's actual D / W / M price structure still looks healthier than its current scanner breadth.

When `MTF Alignment` is stronger than `Historical MTF`, the stock is active across scanners now, but the higher-timeframe price structure is not equally constructive.

If `Historical MTF` is blank, the script did not have enough usable Yahoo price history to compute the price-based D / W / M state.

### 3.4 Momentum Rank

`Momentum Rank` is a relative dashboard rank.

It is built from:

- `1D%` weighted 3x
- `1W%` weighted 2x
- `1M%` weighted 1x

Lower rank number means stronger recent momentum.

### 3.4A Momentum Tag

`Momentum Tag` is the readable bucket derived from `Momentum Rank`.

Current family:

- `ELITE`
- `STRONG`
- `HEALTHY`
- `NEUTRAL`
- `WEAK`
- `LAGGING`

Meaning:

- `ELITE` = top `10%` of the current Dashboard by momentum rank
- `STRONG` = next `10%`
- `HEALTHY` = next `20%`
- `NEUTRAL` = middle `20%`
- `WEAK` = next `20%`
- `LAGGING` = bottom `20%`

Practical rule:

- `Momentum Rank` is for exact ordering
- `Momentum Tag` is for fast filtering
- neither one overrides the final `Signal`

### 3.5 Risk Tag

Exact family:

| Risk Tag | Meaning |
|---|---|
| `LOW` | Few or no major warning flags |
| `MED` | Some caution needed |
| `HIGH` | Multiple warning flags stacked |

Current risk scoring:

- `RSI > 78` or `RSI < 30`: `+2`
- `ADX < 16`: `+1`
- `NATR >= 8`: `+1`
- `ADX >= 20` and `-DI > +DI`: `+1`
- `52W High Dist% < 2`: `+1`
- `52W High Dist% > 30`: `+2`

Thresholds:

- `HIGH`: total flags `>= 3`
- `MED`: total flags `>= 1`
- `LOW`: otherwise

### 3.6 Volume Buzz

Derived from `Vol Ratio 20`.

| Volume Buzz | Threshold |
|---|---|
| `High` | `> 1.5` |
| `Above Avg` | `> 1.2` |
| `Normal` | `>= 0.8` |
| `Low` | `< 0.8` |
| `-` | missing data |

Breakouts with `Low` volume are weaker than breakouts with `High` or `Above Avg`.

### 3.7 Since Capture Trend

Derived from `Since Capture%`.

| Since Capture Trend | Threshold |
|---|---|
| `Strong Gain` | `>= 20%` |
| `Gaining` | `>= 5%` |
| `Flat` | `>= -5%` |
| `Losing` | `>= -20%` |
| `Heavy Loss` | `< -20%` |
| `-` | missing capture context |

This is a tracking label, not a fresh-entry label.

## 4. Bollinger Scenarios

`BB Signal` is a dashboard-only interpretation layer.

Exact family:

| BB Signal | Meaning |
|---|---|
| `SELL ZONE` | Above upper band with overbought confirmation |
| `SQUEEZE BREAK` | Compression expanding upward |
| `STRETCHED` | Above upper band but not the strongest sell state |
| `NEAR HIGH` | Near upper-band extension |
| `BUY ZONE` | Below lower band with stronger oversold confirmation |
| `OVERSOLD` | Below lower band |
| `SQUEEZE` | Volatility compression |
| `NORMAL` | No major Bollinger event |
| `-` | Bollinger context unavailable |

Current dashboard interpretation rules:

- `SELL ZONE`: `%B > 1.0` and `RSI > 70`
- `SQUEEZE BREAK`: squeeze active and `%B >= 0.8`
- `STRETCHED`: `%B > 1.0`
- `NEAR HIGH`: `%B >= 0.85` and `RSI > 65`
- `BUY ZONE`: `%B < 0.0` and `RSI < 35`
- `OVERSOLD`: `%B < 0.0`
- `SQUEEZE`: squeeze active or width percentile very low

## 5. Camarilla Scenarios

The dashboard combines Bollinger context with Camarilla levels from the previous completed bar.

Raw Camarilla columns:

- `Cam H3`
- `Cam H4`
- `Cam L3`
- `Cam L4`
- `Ideal Enter Price`
- `Possible Sell Value`
- `Stop Loss Value`

### 5.1 Base Price Zone States

These are the base zone labels before BB-driven overrides:

| Cam Setup | Meaning |
|---|---|
| `ABOVE H4` | Price has already cleared the main breakout level |
| `BETWEEN H3-H4` | Price is in the upper resistance zone |
| `INSIDE L3-H3` | Price is in the neutral central zone |
| `BETWEEN L4-L3` | Price is in lower support zone |
| `BELOW L4` | Price is below breakdown support |
| `-` | Camarilla data unavailable |

### 5.2 Combined BB + Camarilla States

These are the practical dashboard scenarios you will actually use most.

| Cam Setup | Meaning |
|---|---|
| `SQUEEZE + H4 BREAK` | Best Camarilla-confirmed breakout state |
| `WATCH H4 BREAK` | Squeeze is constructive, but H4 is not broken yet |
| `SQUEEZE NEAR H4` | Price is constructive and approaching H4 |
| `OVERSOLD BELOW L4` | Deep washout under lower support |
| `OVERSOLD AT L3` | Cleaner support-based oversold setup |
| `WATCH L3 SUPPORT` | Early oversold watch around support |
| `AT/ABOVE H4 RESISTANCE` | Price is already at or beyond key resistance |
| `UPPER BAND UNDER H4` | Upper-band strength, but still under the breakout line |

### 5.3 Camarilla Price Plan Logic

The live dashboard derives plan values this way:

- breakout plan uses `H4` as ideal trigger
- breakout target uses `H4 + (H4 - H3)`
- breakout stop uses `H3 - buffer`
- oversold plan uses `L3` as ideal entry
- oversold target uses `H3`
- oversold stop uses `L4 - buffer`

Current buffer:

- `0.2%` of `max(price, H4, L3)`

## 6. AI Decision Scenarios

Exact AI decision family:

| AI Decision | Meaning |
|---|---|
| `STRONG BUY` | Strongest AI bullish opinion |
| `BUY` | Bullish |
| `ACCUMULATE` | Bullish, but staged entry preferred |
| `HOLD` | Neutral |
| `REDUCE` | Light bearish or trim bias |
| `SELL` | Bearish |
| `STRONG SELL` | Strongest AI bearish opinion |

Use AI only as a second layer.

AI runtime dependency summary:

- the AI path currently uses `openai` plus `requests`
- NVIDIA NIM is called through an OpenAI-compatible API path
- Gemini is called through Google's native `generateContent` JSON path
- `AI_ENABLED` can disable AI completely without disabling the technical stack
- if no valid provider is available, the workbook still gets technical signals; AI fields simply remain blank

Current provider flow:

- `AI_PRIMARY = "nvidia"` or `AI_PRIMARY = "google"` selects the primary provider family
- `AI_SECONDARY_ENABLED = False` -> only the primary provider family is used
- `AI_SECONDARY_ENABLED = True` -> the other provider family is tried only after the primary chain fails
- valid NIM usage needs at least one valid key plus at least one configured model
- valid Gemini usage needs at least one real key in `GEMINI_API_KEYS`
- the current checked-in default is `AI_PRIMARY = "google"` with `AI_SECONDARY_ENABLED = False`
- multiple keys scale throughput within a provider; they do not change the scoring rubric
- deterministic settings are intentionally conservative: fixed model lists, `temperature = 0.0`, `top_p = 1.0`

Recommended trust order:

1. `In Screener?`
2. `Signal`
3. `Setup Signal`
4. `Core Signal`
5. `Signal Quality`
6. `Signal Regime`
7. `Win Prob%` / `Hist Precision%` / `Exp 10D%`
8. `Momentum Rank` / `Momentum Tag`
9. `Risk Tag`
10. `BB Signal`
11. `Cam Setup`
12. `AI Decision`
13. `Quick Action`

### AI-Enabled Shortlist Workflow

Best AI-enabled shortlist flow:

1. keep `In Screener? = Yes`
2. require bullish final `Signal`
3. reject any `Signal Quality = REJECT - ...`
4. prefer `Signal Regime = TRENDING`
5. prefer good predictive stats
6. prefer low or medium `Risk Tag`
7. prefer constructive BB/Camarilla context
8. then require bullish AI alignment:
- `AI Decision` bullish
- `AI Conf%` healthy
- `Consensus Score >= 6`
9. finally use `Quick Action` to prioritize:
- `BUY NOW`
- `ACCUMULATE`
- then `WATCH`

### AI-Disabled Shortlist Workflow

If AI is off or blank:

1. ignore `AI Decision`, `AI Conf%`, and `Consensus Score`
2. treat `Quick Action` mostly as a fallback watchlist label
3. rely on the technical stack:
- `Signal`
- `Setup Signal`
- `Core Signal`
- `Signal Quality`
- `Signal Regime`
- walk-forward evidence
- `Risk Tag`
- `BB Signal`
- `Cam Setup`
- `Volume Buzz`
- `MTF Alignment`
- `Historical MTF`
4. prefer rows where the final signal already survived the quality gate and the predictive stats are not weak

## 7. Most Important Combined Live Scenarios

### Best continuation scenario

Look for:

- `Signal = BREAKOUT`
- `Setup Signal = BREAKOUT`
- `Signal Quality = PASS - HIGH` or `PASS - MED`
- `Signal Regime = TRENDING`
- `BB Signal = SQUEEZE BREAK`
- `Cam Setup = SQUEEZE + H4 BREAK`
- `Risk Tag = LOW`
- `Volume Buzz = High` or `Above Avg`
- `Quick Action = BUY NOW` or `ACCUMULATE`
- if AI is enabled, `AI Decision` should also be bullish and `Consensus Score` should usually be `>= 6`

### Good dip-buy scenario

Look for:

- `Signal = STRONG BUY (Oversold)` or `OVERSOLD`
- `Signal Quality` not `REJECT - ...`
- `BB Signal = BUY ZONE` or `OVERSOLD`
- `Cam Setup = OVERSOLD AT L3` or `WATCH L3 SUPPORT`
- `Risk Tag` not `HIGH`
- if AI is enabled, bullish or at least non-bearish AI alignment is preferred

### Trend still alive, but do not chase

Look for:

- `Signal = HOLD (Overbought)`
- `BB Signal = SELL ZONE`, `STRETCHED`, or `NEAR HIGH`
- `Cam Setup = AT/ABOVE H4 RESISTANCE` or `UPPER BAND UNDER H4`

### Weak or damaged long scenario

Look for:

- `Signal = HOLD (Below MA200)` or `SELL`
- `Signal = HOLD (High Vol)` or `HOLD (Choppy Regime)` or `HOLD (Low Quality)`
- `Risk Tag = HIGH`
- `Volume Buzz = Low`
- `Quick Action = CAUTION` or `AVOID`

### Ignore / fix-data scenario

Look for:

- `Signal = No Data`
- `Signal = Symbol Not Found`
- `Signal = Error`

These are not trading opinions. They are data-pipeline states.

## 8. What Is Pure Math vs What Is Strategy

Pure math:

- `MA`
- `RSI`
- `ATR`
- `NATR`
- `+DI`, `-DI`, `ADX`
- `MACD`
- Bollinger values
- Camarilla values
- return percentages

Strategy or interpretation layers:

- `Signal`
- `BB Signal`
- `Cam Setup`
- `Risk Tag`
- `Volume Buzz`
- `Quick Action`
- `Consensus Score`

This matters because:

- the math can be correct
- while the strategy thresholds can still be debatable

## 9. Recommended Reading Order

When you open a fresh workbook, use this order:

1. `Dashboard`
2. `Signal`
3. `Risk Tag`
4. `BB Signal`
5. `Cam Setup`
6. `Volume Buzz`
7. `MTF Alignment`
8. `Historical MTF`
9. `Quick Action`
10. `Dashboard History`
11. `Price History`

If AI is disabled:

- ignore `Consensus Score`
- ignore `AI Decision`
- treat `Quick Action` mostly as a fallback watchlist label

## 10. Final Rule of Thumb

If you want the shortest decision shortcut:

- strongest bullish live scenario:
  `BREAKOUT + SQUEEZE BREAK + SQUEEZE + H4 BREAK + LOW risk`
- strongest reversal watch:
  `STRONG BUY (Oversold) + BUY ZONE + OVERSOLD AT L3`
- avoid chasing:
  `HOLD (Overbought) + SELL ZONE`
- avoid low-quality entries:
  `HOLD (Below MA200)`, `WEAK`, `SELL`, `HIGH` risk, or missing data states

With AI enabled, the best rows also have bullish `AI Decision` and `Consensus Score >= 6`.

Without AI, ignore consensus and judge the row purely from the technical stack.

## 11. Verified `Momentum Tag` And Intraday Validation Warning (2026-04-21)

### Scenario A: new Dashboard column is present and correct

Verified workbook:

- `gas_stock_tracker_dashboard (16).xlsx`

Observed facts:

- `67` Dashboard columns
- `313` active rows
- `0` active blank `Momentum Tag` rows

Meaning:

- the `Momentum Tag` feature is verified in live output
- you can use it for quick filtering, while still sorting by `Momentum Rank`

### Scenario B: full workbook says `Validation = WARN` even though structure is fine

Verified workbook:

- `gas_stock_tracker (5).xlsx`

Latest visible validation row:

- `Checked Rows = 12`
- `Matched Rows = 0`
- `Mismatch Rows = 12`
- `Unresolved Rows = 0`
- `Status = WARN`

Mismatch details included:

- `Current Price`
- `1D%`
- `1W%`
- `RSI 14`
- benchmark-relative-strength fields

Meaning:

- this is the intraday drift scenario
- market moved before the validator finished its fresh recomputation
- the workbook can still be structurally correct

Decision rule:

- market-hours `WARN` = freshness caution
- off-market `WARN` = stronger sign that something deserves investigation
