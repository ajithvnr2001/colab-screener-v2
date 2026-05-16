# Complete Column Glossary

> GitHub reference for this file:
> `https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/COMPLETE-COLUMN-GLOSSARY.md`
>
> Quick navigation:
> - [Docs README](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/README.md)
> - [Start Here Beginner Guide](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/START-HERE-BEGINNER-GUIDE.md)
> - [JSON Output Workflow](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/JSON-OUTPUT-WORKFLOW.md)
> - [How to Read Data](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/HOW-TO-READ-DATA.md)
> - [All Possible Scenarios](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/ALL-POSSIBLE-SCENARIOS.md)

This file explains the tracker columns in depth.

## JSON Output Note

The runnable implementation now emits these columns as JSON object keys instead of Excel worksheet columns.

JSON mappings:

- `Dashboard` -> `dashboard`
- scanner sheets -> `scanners`
- `Price History` -> `price_history`
- `Dashboard History` -> `dashboard_history`
- `Validation` -> `validation`

The schema arrays are embedded in every full output under `schema`, and the display order below is preserved in the JSON rows.

For run commands and Telegram behavior, read `JSON-OUTPUT-WORKFLOW.md`.

Use it when you want:

- the meaning of a specific column
- where a column appears
- how that column is generated
- how to actually use it when reading the workbook

For a first-time reader, start with:

- `START-HERE-BEGINNER-GUIDE.md`

## How To Read This File

Important rule:

- many columns repeat across multiple sheets
- when the same column name appears on multiple sheets, its core meaning stays the same
- the sheet changes the context, not the basic meaning

Sheet abbreviations used below:

- `Scanner` = scanner sheets
- `Dashboard` = main aggregated Dashboard sheet
- `Price History` = append-only per-scanner snapshot history
- `Dashboard History` = append-only aggregated Dashboard snapshot history

## Sheet Purpose Quick Reference

| Sheet | Purpose |
|---|---|
| `Dashboard` | Main decision sheet for current stock selection |
| `Scanner` | One row per stock per screener sheet |
| `Price History` | Historical snapshots of scanner-row metrics |
| `Dashboard History` | Historical snapshots of Dashboard decisions |
| `Validation` | Run-level freshness check after Dashboard rebuild |

## Identity And Lifecycle Columns

| Column | Appears In | What it means | How to use it |
|---|---|---|---|
| `Symbol` | All sheets | Resolved Yahoo symbol used by the runtime, including `BSE:` prefix when applicable | Primary machine identity for the stock |
| `Name` | All sheets | Human-readable stock name from Screener data | Use for recognition only; `Symbol` is more exact |
| `Scanner` | `Price History` | Source screener sheet for that history row | Helps trace where the row came from |
| `First Captured` | `Scanner`, `Dashboard` | First time the stock was captured into tracker history | Tells you how long the stock has been in your system |
| `Last Seen` | `Scanner`, `Dashboard` | Most recent time the stock was seen active in the source flow | Helps separate recent vs stale relevance |
| `In Screener?` | All sheets except where snapshot context already implies it | Whether the stock is active in the current run | Always check this first |
| `Days Tracked` | `Dashboard` | Number of days since first capture | Useful for persistence and maturity of the idea |
| `Snapshot At` | `Price History`, `Dashboard History` | Time that historical snapshot row was written | Use to reconstruct timeline changes |

## Tracker Breadth And Persistence Columns

| Column | Appears In | What it means | How to use it |
|---|---|---|---|
| `Total Appearances` | `Dashboard`, `Dashboard History` | Total number of active appearances accumulated across runs | Higher values suggest repeated persistence |
| `Unique Scanners` | `Dashboard`, `Dashboard History` | Number of different screener sheets that have captured the stock | Higher values suggest broader scanner support |
| `Scanner List` | `Dashboard`, `Dashboard History` | Comma-separated list of scanners linked to that stock in tracker history | Good for manual context and audit trail |
| `Best Scanner` | `Dashboard` | Scanner that has contributed the most active hits for that stock | Useful when you want to know the dominant source context |
| `MTF Alignment` | `Dashboard`, `Dashboard History` | Live active scanner breadth across Daily / Weekly / Monthly groups | Stronger D/W/M agreement is better |
| `Historical MTF` | `Dashboard`, `Dashboard History` | Price-based Daily / Weekly / Monthly structure from resampled Yahoo history | Use as higher-timeframe confirmation, not scanner breadth |

### `MTF Alignment` vs `Historical MTF`

These two are not the same thing.

- `MTF Alignment` = where the stock is currently active across your Daily / Weekly / Monthly scanner families
- `Historical MTF` = whether Yahoo price structure itself still looks constructive across D / W / M bars

Strongest case:

- both are constructive

Mixed case:

- `MTF Alignment` uses scanner-ID classification, not magic inference from the stock itself
- if your configured scanner names do not expose weekly/monthly hints, many rows can remain `D`-only even when the price chart looks healthy on higher timeframes
- the current checked-in `Variant-*` scanner IDs fall into that default-`D` case unless you rename or extend them
- strong `MTF Alignment` but weak `Historical MTF` means scanner interest is active now, but higher-timeframe price structure is weaker
- strong `Historical MTF` but weak `MTF Alignment` means price structure is healthier than current scanner breadth

## Price And Return Columns

| Column | Appears In | What it means | How it is used |
|---|---|---|---|
| `Capture Price` | All main sheets | Price when the stock was first captured or current tracking basis was established | Used for `Since Capture%` tracking |
| `Current Price` | All main sheets | Latest price from the selected Yahoo history basis | Base anchor for most live interpretation |
| `Since Capture%` | All main sheets | Percentage move from capture price to current price | Useful for tracking how much the stock has moved since entry into tracker history |
| `1D%` | All main sheets | 1-session return | Very short-term momentum |
| `1W%` | All main sheets | 5-session return | Useful for short swing momentum |
| `1M%` | All main sheets | 21-session return | Useful for recent trend strength |
| `3M%` | All main sheets | 63-session return | Intermediate trend strength |
| `6M%` | All main sheets | 126-session return | Medium-term trend strength |
| `1Y%` | All main sheets | 252-session return | Long-term trend strength |
| `2Y%` | `Scanner` | 504-session return | Long-run context only |
| `3Y%` | `Scanner` | 756-session return | Long-run context only |
| `Avg Weekly%` | `Scanner` | Average 5-session return over the lookback logic used by the script | Smoother performance context |
| `Avg Monthly%` | `Scanner` | Average 21-session return over the longer lookback | Smoother medium-term context |
| `Avg 3M%` | `Scanner` | Average 63-session return | Broader trend context |
| `Avg 6M%` | `Scanner` | Average 126-session return | Broader trend context |
| `Avg 1Y%` | `Scanner` | Average 252-session return | Long-term average performance context |

## Core Trend And Indicator Columns

| Column | Appears In | What it means | How to use it |
|---|---|---|---|
| `RSI 14` | All main sheets | 14-period Relative Strength Index | Momentum state and stretch level |
| `MA 20` | `Scanner` | 20-period moving average | Short-term trend reference |
| `MA 50` | `Scanner` | 50-period moving average | Medium-term trend reference |
| `MA 200` | `Scanner` | 200-period moving average | Long-term trend filter |
| `ADX 14` | All main sheets | 14-period Average Directional Index | Trend strength, not direction |
| `+DI 14` | All main sheets | Positive Directional Index | Bullish directional control |
| `-DI 14` | All main sheets | Negative Directional Index | Bearish directional control |
| `ATR 14` | All main sheets | 14-period Average True Range | Absolute volatility |
| `NATR 14` | All main sheets | ATR normalized by price | Comparable volatility across stocks |
| `Vol Ratio 20` | `Scanner`, `Price History` | Current volume relative to recent average | Participation / breakout support |
| `MACD Line` | `Scanner`, `Price History` | MACD directional component | Trend bias and acceleration context |
| `MACD Hist` | `Scanner`, `Price History` | MACD histogram | Momentum acceleration / deceleration |
| `52W High Dist%` | `Scanner`, `Price History` | Distance below the 52-week high | Lower values mean closer to breakout territory |
| `20D Breakout%` | `Scanner`, `Price History` | Distance above or below the prior 20-day high | Positive values mean breakout is active |

### How To Think About The Advanced Indicators

- `ADX 14` tells you whether trend strength exists
- `+DI 14` and `-DI 14` tell you who is in control
- `ATR 14` and `NATR 14` tell you how noisy the move is
- `Vol Ratio 20` tells you whether participation supports the move
- `MACD Line` and `MACD Hist` tell you whether momentum is improving or fading
- `52W High Dist%` and `20D Breakout%` tell you where price sits relative to breakout structure

## Signal Stack Columns

| Column | Appears In | What it means | How to use it |
|---|---|---|---|
| `Core Signal` | All main sheets | Older stable baseline signal | Cross-check layer |
| `Setup Signal` | All main sheets | Raw enhanced signal before predictive filtering | Shows what the raw engine wanted |
| `Signal` | All main sheets | Final live technical signal after predictive gating | Main technical decision column |
| `Signal Quality` | All main sheets | Predictive verdict on the raw setup | Tells you whether the setup passed, failed, or had thin evidence |
| `Signal Regime` | All main sheets | Current market texture classification | Tells you what kind of tape the stock is currently in |

### `Signal`

This is the most important technical label.

It is the final answer after the predictive gate has had a chance to downgrade a raw bullish setup.

### `Setup Signal`

This is the raw enhanced signal before the quality gate.

If `Setup Signal` is bullish but final `Signal` is weaker, the predictive filter intentionally blocked it.

### `Core Signal`

This is the older simpler baseline.

Use it to see whether the older model agrees with the newer structure.

## `Signal Quality` Deep Explanation

`Signal Quality` is a predictive evidence label, not the signal itself.

Exact family:

| Value | Meaning | Practical reading |
|---|---|---|
| `PASS - HIGH` | Strongest evidence bucket | Best-quality bullish pass state |
| `PASS - MED` | Good but not elite | Still strong enough to trust more seriously |
| `PASS - LOW` | Passed with weaker evidence | Acceptable but not premium |
| `PASS - UNVERIFIED` | Not enough usable walk-forward evidence to score strongly | Technically valid, but less statistically proven |
| `N/A - NON-BULL` | Setup was not bullish, so the bullish quality gate did not apply | Normal for neutral or bearish rows |
| `REJECT - HIGH-VOL` | Raw bullish setup blocked by hot volatility | Too noisy or overheated |
| `REJECT - CHOPPY` | Raw bullish setup blocked by mixed tape | Too whipsaw-prone |
| `REJECT - THIN HISTORY` | Raw bullish setup blocked because historical evidence is too thin outside a strong regime | Too little evidence |
| `REJECT - LOW EDGE` | Raw bullish setup blocked because win rate, precision, or expected return were too weak | Statistically unattractive |

### Why `PASS - UNVERIFIED` Happens

`PASS - UNVERIFIED` is a `Signal Quality` state.

It appears when:

- the row does not have enough usable walk-forward evidence
- or there is not enough quality-score information to grade it strongly

What it does not mean:

- broken row
- fake data
- wrong indicator math

What it does mean:

- the current technical setup can still be valid
- but the predictive layer cannot claim strong historical evidence behind it

## `Signal Regime` Deep Explanation

`Signal Regime` is separate from `Signal Quality`.

Exact family:

| Value | Meaning | Practical reading |
|---|---|---|
| `TRENDING` | Trend stack and directional context are healthy enough for normal trend-following confidence | Best regime for continuation setups |
| `CHOPPY` | Current tape is mixed and more likely to whipsaw | Be skeptical even if the raw setup looks bullish |
| `HIGH-VOL` | Normalized volatility is too hot for normal breakout confidence | Avoid chasing overheated moves |

Practical difference:

- `Signal Quality` = did the setup pass the predictive filter?
- `Signal Regime` = what kind of tape is the stock in right now?

## Predictive Evidence Columns

| Column | Appears In | What it means | How to use it |
|---|---|---|---|
| `Win Prob%` | All main sheets | Weighted blend of historical forward 5D and 10D win rates from walk-forward replay | Higher is better |
| `Hist Precision%` | All main sheets | Historical 10D win rate of the chosen setup bucket | Higher is better |
| `Exp 5D%` | All main sheets | Average forward 5-session return of the chosen setup bucket | Positive is healthier |
| `Exp 10D%` | All main sheets | Average forward 10-session return of the chosen setup bucket | Positive is healthier |
| `WF Samples` | All main sheets | Number of usable walk-forward historical examples backing the setup stats | More samples = stronger evidence |

### How These Columns Work Together

- `Win Prob%` tells you how often that kind of setup historically moved up
- `Hist Precision%` focuses on the 10-day precision outcome
- `Exp 5D%` and `Exp 10D%` tell you the average payoff, not just the hit rate
- `WF Samples` tells you how much evidence exists behind the stats

## Sector, Relative Strength, And Liquidity Columns

| Column | Appears In | What it means | How to use it |
|---|---|---|---|
| `Sector` | `Scanner`, `Price History`, `Dashboard`, `Dashboard History` | Normalized Yahoo sector classification used by the tracker | Helps group the stock into a benchmark bucket |
| `Industry` | `Scanner`, `Price History`, `Dashboard`, `Dashboard History` | Yahoo industry label or sector fallback | Human context only; less standardized than `Sector` |
| `Sector Benchmark` | `Scanner`, `Price History`, `Dashboard`, `Dashboard History` | NSE thematic benchmark chosen for that normalized sector when available | Tells you what the stock is being compared against besides NIFTY |
| `RS Tag` | `Scanner`, `Price History`, `Dashboard`, `Dashboard History` | Compressed relative-strength label from 1M/3M comparisons vs NIFTY and sector | Quick leadership check |
| `RS vs NIFTY 1M%` | `Scanner`, `Price History`, `Dashboard`, `Dashboard History` | 1-month stock return minus 1-month NIFTY return | Positive is better |
| `RS vs NIFTY 3M%` | `Scanner`, `Price History`, `Dashboard`, `Dashboard History` | 3-month stock return minus 3-month NIFTY return | More important medium-term leadership check |
| `RS vs Sector 1M%` | `Scanner`, `Price History`, `Dashboard`, `Dashboard History` | 1-month stock return minus 1-month sector benchmark return | Positive is better |
| `RS vs Sector 3M%` | `Scanner`, `Price History`, `Dashboard`, `Dashboard History` | 3-month stock return minus 3-month sector benchmark return | Strongest sector-leadership check |
| `Avg Traded Value 20D Cr` | `Scanner`, `Price History`, `Dashboard`, `Dashboard History` | Average recent daily traded-value estimate in crores from price x volume | Practical liquidity screen |
| `Liquidity Tag` | `Scanner`, `Price History`, `Dashboard`, `Dashboard History` | Readable liquidity class derived from `Avg Traded Value 20D Cr` | Helps avoid illiquid names |

### `Sector` And `Sector Benchmark`

The runtime pulls Yahoo asset-profile data first.

- `Sector` is normalized into a smaller live set so different raw Yahoo labels still map into one tracker bucket
- `Sector Benchmark` is then chosen from a preferred NSE benchmark list for that bucket when one is available
- if `Sector Benchmark` is blank, sector-relative numbers may also remain blank

### `RS Tag`

`RS Tag` is not the same as `RSI`.

It compresses four relative-strength comparisons:

- `1M` vs NIFTY
- `3M` vs NIFTY
- `1M` vs sector
- `3M` vs sector

Current label family:

- `Strong vs Both`
- `RS Leader`
- `Mixed`
- `Weak RS`
- `Lagging`
- `—`

Practical reading:

- `Strong vs Both` and `RS Leader` are healthiest for breakout or momentum names
- `Mixed` means leadership is not clean
- `Weak RS` or `Lagging` means the stock is not acting like a leader even if the raw technical setup looks okay

### `Liquidity Tag`

Current liquidity thresholds:

- `Deep` for `>= 100 Cr`
- `Liquid` for `>= 20 Cr`
- `Adequate` for `>= 5 Cr`
- `Thin` for `>= 1 Cr`
- `Illiquid` for `< 1 Cr`

Practical reading:

- `Deep` / `Liquid` are strongest
- `Adequate` is acceptable
- `Thin` / `Illiquid` deserve extra caution and will weaken Dashboard routing

## Dashboard Decision And Ranking Columns

| Column | Appears In | What it means | How to use it |
|---|---|---|---|
| `Quick Action` | `Dashboard`, `Dashboard History` | Aggregated routing label built from signal, quality, consensus, timeframe support, momentum, relative strength, liquidity, and risk | Use only after reading the technical stack |
| `Consensus Score` | `Dashboard`, `Dashboard History` | Aggregated AI score mapped into a `1.0` to `10.0` range | Useful only when AI is enabled |
| `Momentum Rank` | `Dashboard`, `Dashboard History` | Relative rank built from weighted recent returns plus medium-term relative strength | Lower rank number = stronger recent momentum and leadership |
| `Momentum Tag` | `Dashboard` | Readable bucket derived from `Momentum Rank` percentile | Faster human scan of momentum leadership |
| `Risk Tag` | `Dashboard`, `Dashboard History` | Compressed risk summary from stretch, volatility, DI structure, predictive weakness, poor liquidity, and weak relative strength | Avoid `HIGH` risk fresh longs |
| `Volume Buzz` | `Dashboard` | Simplified volume participation state from `Vol Ratio 20` | Breakouts are stronger when participation is not weak |
| `Since Capture Trend` | `Dashboard` | Simple interpretation of `Since Capture%` | Tracking label, not a primary entry signal |

### `Quick Action`

This is a routing label, not the core truth.

Read it last, not first.

Why:

- it is downstream of other logic
- it can weaken when AI is missing
- it can also be forced down by risk, predictive rejection, weak relative strength, or poor liquidity

### `Consensus Score`

This exists only because of AI decisions.

Without AI:

- it is blank

So do not use it in AI-disabled analysis.

### `Momentum Rank` And `Momentum Tag`

`Momentum Rank` is the exact ordering field.

`Momentum Tag` is the quick-reading bucket from that same ordering.

Implementation note:

- `Momentum Tag` is appended at the end of the Dashboard schema
- this avoids shifting older legacy Dashboard columns during the first upgraded run

Current `Momentum Tag` family:

- `ELITE`
- `STRONG`
- `HEALTHY`
- `NEUTRAL`
- `WEAK`
- `LAGGING`

Use:

- `Momentum Rank` when you want precise ordering
- `Momentum Tag` when you want a fast visual filter
- neither one should override the final signal stack

### `Risk Tag`

This compresses multiple risk flags into:

- `LOW`
- `MED`
- `HIGH`

It is a warning summary, not a signal replacement.

## Validation Columns

| Column | Appears In | What it means | How to use it |
|---|---|---|---|
| `Snapshot At` | `Validation` | Timestamp when that validation row was appended | Use to identify the exact run time being checked |
| `Iteration` | `Validation` | Iteration number of the run | Lets you map validation rows back to loop runs |
| `Mode` | `Validation` | Validation mode string, currently the fresh-sample size | Confirms how the validator was run |
| `Checked Rows` | `Validation` | Number of active rows sampled for comparison | More checked rows = wider coverage |
| `Matched Rows` | `Validation` | Sampled rows with no compared-field drift | Higher is better |
| `Mismatch Rows` | `Validation` | Sampled rows with at least one compared-field mismatch | Non-zero means investigate the run |
| `Unresolved Rows` | `Validation` | Sampled rows whose fresh Yahoo history could not be fetched | Treat as data-availability exceptions |
| `Latest Session` | `Validation` | Latest completed market-session date observed in the fresh histories | Useful freshness reference |
| `Status` | `Validation` | Run-level verdict: `PASS`, `WARN`, or `SKIP` | `PASS` is best |
| `Details` | `Validation` | Human-readable mismatch summary or pass note | Read this first when status is not `PASS` |

### How To Use The `Validation` Sheet

- this sheet exists only in the full workbook, not the Dashboard-only export
- one row is appended after each successful Dashboard rebuild
- the validator checks sampled active `Dashboard` rows, not inactive history rows
- it refetches fresh stock history and fresh benchmark history, recomputes the row, and compares key technical / predictive / relative-strength / liquidity fields
- `PASS` means the sampled rows matched
- `WARN` means drift was found somewhere in the sampled rows
- `SKIP` means the validator was disabled or no eligible active rows existed

## Dashboard Context Columns

| Column | Appears In | What it means | How to use it |
|---|---|---|---|
| `BB Signal` | `Dashboard` | Bollinger-based interpretation layer | Helps read squeeze, stretch, and oversold context |
| `Cam Setup` | `Dashboard`, `Dashboard History` | Combined Bollinger + Camarilla timing interpretation | Helps read breakout and dip-buy location |
| `Cam H3` | `Dashboard`, `Price History`, `Dashboard History` | Camarilla upper reference level 3 | Upper reference / resistance context |
| `Cam H4` | `Dashboard`, `Price History`, `Dashboard History` | Main breakout trigger reference | Breakout line |
| `Cam L3` | `Dashboard`, `Price History`, `Dashboard History` | Main support / dip-buy reference | Controlled support zone |
| `Cam L4` | `Dashboard`, `Price History`, `Dashboard History` | Lower breakdown / stop reference | Breakdown line |
| `Ideal Enter Price` | `Dashboard`, `Dashboard History` | System-derived preferred trigger or support entry level | Timing aid, not a guarantee |
| `Possible Sell Value` | `Dashboard`, `Dashboard History` | System-derived target estimate | Contextual target, not certainty |
| `Stop Loss Value` | `Dashboard`, `Dashboard History` | System-derived stop reference | Risk planning aid |

## AI Columns

| Column | Appears In | What it means | How to use it |
|---|---|---|---|
| `AI Decision` | `Scanner`, `Dashboard`, `Price History`, `Dashboard History` | AI second-opinion label after reading supplied metrics | Confirmation layer only |
| `AI Reason` | `Scanner` | AI summary of why it made that decision | Read when you want a textual explanation |
| `AI Conf%` | All AI-enabled sheets except where text is omitted | AI confidence estimate | Higher confidence is better, but still secondary to technicals |

### Important AI Rule

AI does not replace the technical engine.

Use AI to confirm, not to rescue weak rows.

### Current AI Runtime Notes

- current checked-in default: `AI_PRIMARY = "google"` and `AI_SECONDARY_ENABLED = False`
- Gemini currently uses a native JSON-schema `generateContent` path
- NVIDIA remains available if you switch the primary provider or enable the secondary provider family
- multiple API keys rotate within the active provider family so you can scale throughput without changing the scoring rubric
- blank AI fields do not automatically mean the stock is bad; they can also mean:
- AI is disabled
- the configured provider failed or was unavailable
- the row itself is unresolved (`No Data`, `Symbol Not Found`, `Error`)
- the Dashboard only shows `AI Decision` and `AI Conf%`; `AI Reason` is preserved on scanner rows, not on the Dashboard sheet

## Meta Columns

| Column | Appears In | What it means | How to use it |
|---|---|---|---|
| `Screener Link` | `Dashboard` | Direct Screener company URL | Convenience only |
| `Last Updated` | `Scanner`, `Dashboard` | Timestamp of latest metric write | Useful for freshness checking |

## Sheet-Specific Column Sets

## Dashboard Columns In Display Order

These are the exact `Dashboard` columns in order:

1. `Symbol`
2. `Name`
3. `In Screener?`
4. `Quick Action`
5. `Consensus Score`
6. `MTF Alignment`
7. `Historical MTF`
8. `Sector`
9. `Industry`
10. `Sector Benchmark`
11. `RS Tag`
12. `RS vs NIFTY 1M%`
13. `RS vs NIFTY 3M%`
14. `RS vs Sector 1M%`
15. `RS vs Sector 3M%`
16. `Avg Traded Value 20D Cr`
17. `Liquidity Tag`
18. `Momentum Rank`
19. `Risk Tag`
20. `BB Signal`
21. `Cam Setup`
22. `Volume Buzz`
23. `Since Capture Trend`
24. `First Captured`
25. `Days Tracked`
26. `Last Seen`
27. `Total Appearances`
28. `Unique Scanners`
29. `Scanner List`
30. `Best Scanner`
31. `Capture Price`
32. `Current Price`
33. `Cam H3`
34. `Cam H4`
35. `Cam L3`
36. `Cam L4`
37. `Ideal Enter Price`
38. `Possible Sell Value`
39. `Stop Loss Value`
40. `Since Capture%`
41. `1D%`
42. `1W%`
43. `1M%`
44. `3M%`
45. `6M%`
46. `1Y%`
47. `RSI 14`
48. `ADX 14`
49. `+DI 14`
50. `-DI 14`
51. `ATR 14`
52. `NATR 14`
53. `Signal`
54. `Setup Signal`
55. `Core Signal`
56. `Signal Quality`
57. `Signal Regime`
58. `Win Prob%`
59. `Hist Precision%`
60. `Exp 5D%`
61. `Exp 10D%`
62. `WF Samples`
63. `AI Decision`
64. `AI Conf%`
65. `Screener Link`
66. `Last Updated`
67. `Momentum Tag`

## Scanner Sheet Columns In Display Order

These are the exact `Scanner` sheet columns in order:

1. `Symbol`
2. `Name`
3. `First Captured`
4. `Last Seen`
5. `In Screener?`
6. `Capture Price`
7. `Current Price`
8. `Since Capture%`
9. `1D%`
10. `1W%`
11. `1M%`
12. `3M%`
13. `6M%`
14. `1Y%`
15. `2Y%`
16. `3Y%`
17. `Avg Weekly%`
18. `Avg Monthly%`
19. `Avg 3M%`
20. `Avg 6M%`
21. `Avg 1Y%`
22. `RSI 14`
23. `MA 20`
24. `MA 50`
25. `MA 200`
26. `Signal`
27. `Setup Signal`
28. `Core Signal`
29. `Signal Quality`
30. `Signal Regime`
31. `Win Prob%`
32. `Hist Precision%`
33. `Exp 5D%`
34. `Exp 10D%`
35. `WF Samples`
36. `Sector`
37. `Industry`
38. `Sector Benchmark`
39. `RS Tag`
40. `RS vs NIFTY 1M%`
41. `RS vs NIFTY 3M%`
42. `RS vs Sector 1M%`
43. `RS vs Sector 3M%`
44. `Avg Traded Value 20D Cr`
45. `Liquidity Tag`
46. `AI Decision`
47. `AI Reason`
48. `AI Conf%`
49. `Last Updated`
50. `ADX 14`
51. `Vol Ratio 20`
52. `MACD Line`
53. `MACD Hist`
54. `52W High Dist%`
55. `20D Breakout%`
56. `ATR 14`
57. `NATR 14`
58. `+DI 14`
59. `-DI 14`

## Price History Columns In Display Order

These are the exact `Price History` columns in order:

1. `Snapshot At`
2. `Scanner`
3. `Symbol`
4. `Name`
5. `In Screener?`
6. `Capture Price`
7. `Current Price`
8. `Since Capture%`
9. `1D%`
10. `1W%`
11. `1M%`
12. `3M%`
13. `6M%`
14. `1Y%`
15. `Cam H3`
16. `Cam H4`
17. `Cam L3`
18. `Cam L4`
19. `RSI 14`
20. `ADX 14`
21. `+DI 14`
22. `-DI 14`
23. `ATR 14`
24. `NATR 14`
25. `Vol Ratio 20`
26. `MACD Line`
27. `MACD Hist`
28. `52W High Dist%`
29. `20D Breakout%`
30. `Signal`
31. `Setup Signal`
32. `Core Signal`
33. `Signal Quality`
34. `Signal Regime`
35. `Win Prob%`
36. `Hist Precision%`
37. `Exp 5D%`
38. `Exp 10D%`
39. `WF Samples`
40. `Sector`
41. `Industry`
42. `Sector Benchmark`
43. `RS Tag`
44. `RS vs NIFTY 1M%`
45. `RS vs NIFTY 3M%`
46. `RS vs Sector 1M%`
47. `RS vs Sector 3M%`
48. `Avg Traded Value 20D Cr`
49. `Liquidity Tag`
50. `AI Decision`
51. `AI Conf%`

## Dashboard History Columns In Display Order

These are the exact `Dashboard History` columns in order:

1. `Snapshot At`
2. `Symbol`
3. `Name`
4. `In Screener?`
5. `Quick Action`
6. `Consensus Score`
7. `MTF Alignment`
8. `Historical MTF`
9. `Sector`
10. `Industry`
11. `Sector Benchmark`
12. `RS Tag`
13. `RS vs NIFTY 1M%`
14. `RS vs NIFTY 3M%`
15. `RS vs Sector 1M%`
16. `RS vs Sector 3M%`
17. `Avg Traded Value 20D Cr`
18. `Liquidity Tag`
19. `Momentum Rank`
20. `Risk Tag`
21. `Cam Setup`
22. `Total Appearances`
23. `Unique Scanners`
24. `Scanner List`
25. `Capture Price`
26. `Current Price`
27. `Cam H3`
28. `Cam H4`
29. `Cam L3`
30. `Cam L4`
31. `Ideal Enter Price`
32. `Possible Sell Value`
33. `Stop Loss Value`
34. `Since Capture%`
35. `1D%`
36. `1W%`
37. `1M%`
38. `RSI 14`
39. `ADX 14`
40. `+DI 14`
41. `-DI 14`
42. `ATR 14`
43. `NATR 14`
44. `Signal`
45. `Setup Signal`
46. `Core Signal`
47. `Signal Quality`
48. `Signal Regime`
49. `Win Prob%`
50. `Hist Precision%`
51. `Exp 5D%`
52. `Exp 10D%`
53. `WF Samples`
54. `AI Decision`
55. `AI Conf%`

## Validation Columns In Display Order

These are the exact `Validation` columns in order:

1. `Snapshot At`
2. `Iteration`
3. `Mode`
4. `Checked Rows`
5. `Matched Rows`
6. `Mismatch Rows`
7. `Unresolved Rows`
8. `Latest Session`
9. `Status`
10. `Details`

## Final Reading Rule

If you remember only one thing from this glossary, remember this:

- `Signal` tells you the final technical stance
- `Signal Quality` tells you whether the raw bullish setup passed the evidence gate
- `Signal Regime` tells you what type of tape the stock is currently trading in
- `RS Tag` and `Liquidity Tag` tell you whether the stock is leading and tradeable
- `PASS - UNVERIFIED` is a `Signal Quality` state, not a `Signal Regime`

## April 21, 2026 Glossary Update

### `Momentum Tag`

Latest output verification:

- `gas_stock_tracker_dashboard (16).xlsx`
- active blank `Momentum Tag` rows = `0`

That means `Momentum Tag` is now verified as a real generated Dashboard column.

Verified active distribution in that workbook:

- `ELITE = 31`
- `STRONG = 31`
- `HEALTHY = 63`
- `NEUTRAL = 62`
- `WEAK = 63`
- `LAGGING = 63`

### `Validation`

Latest important interpretation case:

- `gas_stock_tracker (5).xlsx`
- latest visible validation row = `Checked 12`, `Matched 0`, `Mismatch 12`, `Unresolved 0`, `Status WARN`

The mismatch details were fields such as:

- `Current Price`
- `1D%`
- `1W%`
- `RSI 14`
- `RS vs NIFTY 1M%`
- `RS vs NIFTY 3M%`

Glossary meaning of that pattern:

- it is an intraday drift warning
- it is not automatically a schema corruption warning
- it is not evidence that `Momentum Tag` caused a calculation failure

Best interpretation rule:

- if `WARN` is dominated by live-moving fields, treat it as a freshness caution
- if `WARN` happens off-market on stable fields, investigate more aggressively
