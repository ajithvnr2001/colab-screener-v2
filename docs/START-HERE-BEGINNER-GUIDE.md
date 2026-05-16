# Start Here Beginner Guide

> GitHub reference for this file:
> `https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/START-HERE-BEGINNER-GUIDE.md`
>
> Quick navigation:
> - [Docs README](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/README.md)
> - [JSON Output Workflow](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/JSON-OUTPUT-WORKFLOW.md)
> - [How to Read Data](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/HOW-TO-READ-DATA.md)
> - [Complete Column Glossary](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/COMPLETE-COLUMN-GLOSSARY.md)
> - [Practical Scenario Examples](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/PRACTICAL-SCENARIO-EXAMPLES.md)

This guide is for someone opening the tracker for the first time.

## Current JSON Output

The runnable implementation in this repo writes JSON, not Excel.

Open these files first after a run:

- `./gas_stock_tracker_dashboard.json`
- `./gas_stock_tracker.json`
- `./dashboard_snapshots.json` when dashboard snapshot history is enabled

Use `gas_stock_tracker_dashboard.json` for the main stock shortlist, `gas_stock_tracker.json` when you need scanner rows, price history, dashboard history, validation, errors, and Telegram status in one file, and `dashboard_snapshots.json` for the historical dashboard snapshot records.

Run continuously:

```bash
python screener-colab-appsheet-json.py
```

Run once:

Edit the footer to call `main(max_iterations=1)`.

Run the syntax validation:

```bash
python -m py_compile screener-colab-appsheet-json.py "main scanner/screener-colab-appsheet-json-full.py"
```

The old workbook names in this guide map directly to JSON sections. `Dashboard` is now the `dashboard` array, scanner sheets are now the `scanners` object, and the history sheets are `price_history` and `dashboard_history`.

If you want:

- the shortest daily workflow, read this file
- the exact meaning of every single workbook column, also read `COMPLETE-COLUMN-GLOSSARY.md`
- the exhaustive live label catalog, also read `ALL-POSSIBLE-SCENARIOS.md`
- practical example combinations, also read `PRACTICAL-SCENARIO-EXAMPLES.md`

## What This Tracker Actually Does

The tracker does not predict the future with certainty.

What it does:

- fetch current screener membership from your configured Screener screens
- resolve stock symbols for Yahoo Finance
- fetch Yahoo price history
- compute technical indicators
- build multiple technical signal layers
- optionally ask AI for a second opinion
- aggregate everything into one Dashboard workbook
- preserve history across runs

So the workbook is a decision-support system, not a guaranteed signal machine.

## Current Checked-In Configuration

The docs should match the code you actually run.

Current checked-in facts:

- the `SCANNERS` list currently contains `3` variant screens
- the workbook creates one scanner sheet per configured scanner
- the current AI default is `AI_PRIMARY = "google"`
- the current AI default keeps `AI_SECONDARY_ENABLED = False`
- AI can still be turned off entirely with `AI_ENABLED = False`

Practical meaning:

- this repo is no longer in the older `51`-scanner state described in some past notes
- if you add or remove scanners later, the workbook shape can change accordingly

## Which File To Open First

Open this first:

- `gas_stock_tracker_dashboard.xlsx`

Why:

- it contains only the `Dashboard` sheet
- it is the fastest file to review
- it is the main summary view across all scanners

Open this when you need more detail:

- `gas_stock_tracker.xlsx`

Why:

- it contains all scanner sheets
- it contains `Price History`
- it contains `Dashboard History`
- it contains `Validation`

## What The Main Sheets Mean

### Dashboard

This is the main decision sheet.

Use it to answer:

- which stocks are active right now
- which ones have the strongest technical setup
- whether the predictive filter approved or rejected the raw setup
- whether AI agrees or not

### Scanner Sheets

Each scanner sheet shows one screener's stocks plus their current metrics.

Use them to answer:

- where the stock was found
- whether it is still active in that specific screener
- how that stock looks from the perspective of that single scanner row

### Price History

This is an append-only snapshot log by scanner row.

Use it to answer:

- what the row looked like on previous runs
- when a stock first became stronger or weaker
- how a stock moved through signal states over time

### Dashboard History

This is an append-only snapshot log of the aggregated Dashboard row.

Use it to answer:

- when the final Dashboard view changed
- when `Quick Action`, `Signal`, `Risk Tag`, or AI consensus changed
- how the final decision layer evolved over time

### Validation

This is the run-level freshness check sheet inside the full workbook.

Use it to answer:

- whether the latest run still matched fresh Yahoo recomputation on sampled active rows
- whether the workbook likely stayed clean right after generation
- which rows were named if the validator saw drift

## Latest Verified Workbook Pair

As of the latest local verification pass:

- `gas_stock_tracker_dashboard (15).xlsx` was structurally clean
- `gas_stock_tracker (4).xlsx` was structurally clean on the real populated Dashboard columns
- the latest visible `Validation` rows inside the full workbook both said `PASS`

Important live exceptions in that verified pair:

- `PARTH` -> `No Data`
- one blank-symbol row -> `Symbol Not Found`

Practical meaning:

- those are expected unresolved-data exceptions
- they are not evidence that the technical engine broke for the rest of the workbook

## The First Big Rule: Active vs Inactive

Always check `In Screener?` first.

- `Yes` means the stock is active in the current run
- `No` means the stock is historical context only

Important behavior:

- inactive rows are frozen
- the script does not refresh fresh Yahoo or AI values for inactive rows
- an inactive row is useful as memory, not as a fresh trade candidate

If you are picking stocks for now, start with:

- `In Screener? = Yes`

## The Second Big Rule: Read Columns In The Right Order

Do not start with AI. Do not start with `Quick Action`.

Use this trust order:

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
17. `AI Decision`, `AI Conf%`, `Consensus Score`
18. `Quick Action`
19. `Validation` sheet for run freshness

Why this order:

- `Signal` is the final technical decision
- `Setup Signal` tells you what the raw engine wanted before the predictive filter
- `Core Signal` is the simpler older baseline
- `Signal Quality` tells you whether the raw bullish setup passed the statistical gate
- `Signal Regime` tells you what kind of tape the stock is currently in
- relative-strength and liquidity columns tell you whether the stock is leading and tradeable, not just technically bullish
- `Momentum Rank` gives exact relative ordering
- `Momentum Tag` gives a fast at-a-glance momentum bucket from that same rank
- AI is only a second-opinion layer

## What Relative Strength Means

Relative strength here does not mean the `RSI` indicator.

It means:

- how the stock performed versus `NIFTY 50`
- how the stock performed versus its sector benchmark

Important columns:

- `RS vs NIFTY 1M%`
- `RS vs NIFTY 3M%`
- `RS vs Sector 1M%`
- `RS vs Sector 3M%`
- `RS Tag`

How to think about them:

- positive numbers mean the stock outperformed that benchmark
- negative numbers mean it lagged that benchmark
- `RS Tag = Strong vs Both` or `RS Leader` is healthier
- `RS Tag = Weak RS` or `Lagging` means the stock may still look technically okay, but it is not acting like a leader

## What Liquidity Means

Liquidity answers a different question:

- if this stock looks good, is it liquid enough to trust more easily

Important columns:

- `Avg Traded Value 20D Cr`
- `Liquidity Tag`

How to think about them:

- `Deep` and `Liquid` are strongest
- `Adequate` is usable
- `Thin` and `Illiquid` mean the stock can move erratically and the Dashboard will treat it more cautiously

## What Momentum Rank And Momentum Tag Mean

These two belong together.

`Momentum Rank` is the exact relative ordering of stocks across the Dashboard.

- lower number = stronger recent momentum and leadership
- `1` = strongest current Dashboard momentum

`Momentum Tag` is the simplified bucket made from that rank percentile.

Current buckets:

- `ELITE`
- `STRONG`
- `HEALTHY`
- `NEUTRAL`
- `WEAK`
- `LAGGING`

How to think about them:

- `Momentum Rank` is for exact sorting
- `Momentum Tag` is for quick human reading
- neither one replaces `Signal`
- a row can have strong momentum but still be a bad buy if `Signal Quality`, `Risk Tag`, or `Signal Regime` are weak

## The Three Signal Layers

### `Core Signal`

This is the older stable baseline signal.

It is useful for:

- cross-checking the newer logic
- understanding whether the basic structure still looks bullish or weak

### `Setup Signal`

This is the raw enhanced setup signal before the predictive gate.

It can be bullish even when the final signal is downgraded later.

Example:

- `Setup Signal = BREAKOUT`
- final `Signal = HOLD (High Vol)`

That means:

- the raw setup looked bullish
- but the final live filter blocked it

### `Signal`

This is the final technical signal you should trust first.

This is the live answer to:

- is the tracker willing to treat this as a current bullish setup or not

## What `Signal Quality` Means

`Signal Quality` is not the signal itself.

It is the predictive verdict on the raw bullish setup.

Common values:

- `PASS - HIGH`
- `PASS - MED`
- `PASS - LOW`
- `PASS - UNVERIFIED`
- `N/A - NON-BULL`
- `REJECT - HIGH-VOL`
- `REJECT - CHOPPY`
- `REJECT - THIN HISTORY`
- `REJECT - LOW EDGE`

How to think about it:

- `PASS - HIGH` = best evidence
- `PASS - MED` = good enough
- `PASS - LOW` = passed, but weaker
- `PASS - UNVERIFIED` = not enough usable walk-forward evidence to score strongly
- `N/A - NON-BULL` = the row was not a bullish setup, so the bullish quality gate did not apply
- `REJECT - ...` = the raw bullish setup was blocked

Important correction:

- `PASS - UNVERIFIED` belongs to `Signal Quality`
- it is not a `Signal Regime`

## What `Signal Regime` Means

`Signal Regime` is the current market texture classification for that row.

Current values:

- `TRENDING`
- `CHOPPY`
- `HIGH-VOL`

What they mean:

- `TRENDING` = trend stack and directional context are healthy enough for normal trend-following confidence
- `CHOPPY` = the tape is mixed and more likely to whipsaw
- `HIGH-VOL` = normalized volatility is too hot for normal breakout confidence

Important distinction:

- `Signal Quality` asks: did the setup pass the predictive gate?
- `Signal Regime` asks: what kind of tape is the stock currently in?

## Why Some Stocks Show `PASS - UNVERIFIED`

This is one of the most important beginner questions.

`PASS - UNVERIFIED` does not mean:

- fake signal
- broken math
- certain failure

It means:

- the setup did not have enough usable walk-forward evidence to score strongly
- or the available evidence was too thin to produce a proper quality score

Why this happens:

- the exact current setup label may not have enough recent historical matches
- the broader signal family may also still have thin sample coverage
- the row may still be technically bullish right now, but the predictive layer cannot claim strong historical evidence

How to treat it:

- more cautious than `PASS - HIGH` or `PASS - MED`
- better than a hard `REJECT - ...`
- acceptable only when the rest of the row is strong:
- bullish final `Signal`
- acceptable `Risk Tag`
- constructive `BB Signal` and `Cam Setup`
- decent `MTF Alignment`
- not obviously overheated

## What AI Does And Does Not Do

AI does not generate the base technical indicators.

AI does:

- read the computed metrics
- give a second opinion
- populate `AI Decision`, `AI Reason`, and `AI Conf%`
- influence `Consensus Score`
- influence the AI-assisted part of `Quick Action`

AI does not:

- replace the technical engine
- override bad data into good data
- make a row bullish by itself if the technical stack is weak

If AI is disabled:

- the technical columns still work
- `AI Decision`, `AI Reason`, `AI Conf%`, and `Consensus Score` stay blank
- `Quick Action` becomes a weaker routing helper

Current runtime note:

- with the checked-in defaults, AI currently uses Google as the primary provider
- the secondary provider family is disabled by default
- if you enable the secondary path later, the other provider is only used after the primary chain fails

## How To Read A Stock In 30 Seconds

For a quick pass:

1. is `In Screener? = Yes`?
2. is final `Signal` bullish?
3. is `Signal Quality` not `REJECT - ...`?
4. is `Signal Regime` acceptable?
5. are `Win Prob%`, `Hist Precision%`, and `Exp 10D%` decent?
6. is `RS Tag` not weak and are the `3M` relative-strength numbers not poor?
7. is `Liquidity Tag` not `Thin` / `Illiquid`?
8. is `Momentum Tag` at least `HEALTHY`?
9. is `Risk Tag` not `HIGH`?
10. are `BB Signal` and `Cam Setup` constructive?
11. if AI is enabled, does AI agree?

If most answers are yes, the stock is shortlist-worthy.

## How To Pick Stocks With AI Enabled

Best-case pattern:

- `In Screener? = Yes`
- final `Signal` bullish
- `Signal Quality = PASS - HIGH` or `PASS - MED`
- `Signal Regime = TRENDING`
- predictive fields not weak
- `RS Tag = Strong vs Both` or `RS Leader`
- `Liquidity Tag = Deep`, `Liquid`, or at least `Adequate`
- `Momentum Tag = ELITE`, `STRONG`, or at least `HEALTHY`
- `Risk Tag` not `HIGH`
- bullish `AI Decision`
- `AI Conf% >= 65`
- `Consensus Score >= 6`
- `Quick Action = BUY NOW` or `ACCUMULATE`

## How To Pick Stocks Without AI

If AI is disabled, ignore:

- `AI Decision`
- `AI Reason`
- `AI Conf%`
- `Consensus Score`

Then judge the row from:

- `Signal`
- `Signal Quality`
- `Signal Regime`
- predictive stats
- relative strength
- liquidity
- `Risk Tag`
- `BB Signal`
- `Cam Setup`
- `Volume Buzz`
- `MTF Alignment`
- `Historical MTF`

## Common Beginner Mistakes

### Mistake 1: starting with `Quick Action`

Do not do that.

`Quick Action` is a routing layer, not the core truth layer.

### Mistake 2: treating inactive rows as fresh signals

If `In Screener? = No`, do not treat it as a current setup.

### Mistake 3: confusing `Setup Signal` with final `Signal`

The final `Signal` matters more.

### Mistake 4: thinking `PASS - UNVERIFIED` means broken

It means thin evidence, not broken math.

### Mistake 5: letting AI override bad technicals

AI should confirm strong rows, not rescue weak ones.

## What To Trust Most

The strongest current rows usually have:

- `In Screener? = Yes`
- final `Signal = BREAKOUT`, `STRONG BUY`, or good `BUY`
- `Signal Quality = PASS - HIGH` or `PASS - MED`
- `Signal Regime = TRENDING`
- `RS Tag` not weak
- liquidity not thin
- `Risk Tag = LOW` or controlled `MED`
- good DI direction
- acceptable volatility
- constructive BB/Camarilla context
- AI agreement if AI is enabled

## What To Avoid First

Fresh long entries should usually avoid:

- `Signal = SELL`
- `Signal = WEAK`
- `Signal = HOLD (Below MA200)`
- `Signal = HOLD (High Vol)`
- `Signal = HOLD (Choppy Regime)`
- `Signal = HOLD (Low Quality)`
- `Risk Tag = HIGH`
- unresolved-data rows such as `No Data`, `Symbol Not Found`, or `Error`

## What To Read Next

After this guide:

1. `HOW-TO-READ-DATA.md`
2. `COMPLETE-COLUMN-GLOSSARY.md`
3. `ALL-POSSIBLE-SCENARIOS.md`
4. `PRACTICAL-SCENARIO-EXAMPLES.md`

## April 21, 2026 Beginner Note

### `Momentum Tag` is now verified

The generated file `gas_stock_tracker_dashboard (16).xlsx` confirmed:

- `Momentum Tag` appears on the Dashboard
- it is populated on all active rows
- it is a real live field you can read now, not a planned future field

### Do not overreact to intraday `Validation = WARN`

The full workbook `gas_stock_tracker (5).xlsx` later showed:

- `12` checked rows
- `0` matched rows
- `12` mismatched rows
- `0` unresolved rows
- `Status = WARN`

That warning happened during market hours and the mismatches were on moving fields like:

- `Current Price`
- `1D%`
- `1W%`
- `RSI 14`
- relative-strength fields

So the beginner rule is:

- if `Validation = WARN` during the session, read the mismatch details first
- if the details are mostly live prices and short return windows, it can be normal intraday drift
- if you want the cleanest freshness check, look at `Validation` after the market session is over
