# Dashboard Heavy Analysis For Colab

> GitHub reference for this file:
> `https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/DASHBOARD-HEAVY-ANALYSIS-COLAB.md`
>
> Related files:
> - [Docs README](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/README.md)
> - [How to Read Data](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/docs/HOW-TO-READ-DATA.md)
> - [main scanner/screener-colab-appsheet-parallel.py](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/main%20scanner/screener-colab-appsheet-parallel.py)
> - [dashboard_heavy_analysis_colab.py](https://github.com/ajithvnr2001/colab-screener-v2/blob/main/dashboard_heavy_analysis_colab.py)

This analyzer is for the dashboard-only workbook:

- input: `gas_stock_tracker_dashboard.xlsx`
- required sheet: `Dashboard`
- script: `dashboard_heavy_analysis_colab.py`

## Fastest Colab Flow

1. Download the dashboard-only files.
2. Upload or keep the required markdown docs in `/content`.
3. Run the analyzer.

If you want the easiest download path, use:

- `download_dashboard_only_files.py`

That script is Colab-friendly and downloads:

- `gas_stock_tracker_dashboard.xlsx`
- `dashboard_snapshots.db`

into:

- `/content/downloaded_dashboard`

## Install In Colab

```python
!pip install boto3 openpyxl openai -q
```

## Download Dashboard Files In Colab

If you paste `download_dashboard_only_files.py` into a cell and run it, it will download both dashboard artifacts by default.

If you save the script as a file in Colab, you can also run:

```python
!python download_dashboard_only_files.py
```

Default download location:

- `/content/downloaded_dashboard/gas_stock_tracker_dashboard.xlsx`
- `/content/downloaded_dashboard/dashboard_snapshots.db`

## Docs To Upload Beside The Analyzer

Upload these repo docs into the same Colab folder if you want full doc-aware analysis:

- `README.md`
- `ALL-POSSIBLE-SCENARIOS.md`
- `PRACTICAL-SCENARIO-EXAMPLES.md`
- `HOW-TO-READ-DATA.md`
- `camarilla_bb_integration.md`
- `bugfixana.md`

## Run Without AI

```python
!python dashboard_heavy_analysis_colab.py \
  --dashboard-xlsx /content/downloaded_dashboard/gas_stock_tracker_dashboard.xlsx \
  --docs-dir /content \
  --out-dir /content/dashboard_analysis_output
```

## Run With NVIDIA NIM AI

Keep `screener-colab-appsheet-parallel.py` in the same Colab folder, or pass its path explicitly.

Important:

- `--parallel-script-path /content/screener-colab-appsheet-parallel.py` does not run the parallel tracker
- it is only used to read NVIDIA NIM keys/models from that file

Top-candidates AI only:

```python
!python dashboard_heavy_analysis_colab.py \
  --dashboard-xlsx /content/downloaded_dashboard/gas_stock_tracker_dashboard.xlsx \
  --use-ai \
  --ai-mode top \
  --ai-top-n 12 \
  --docs-dir /content \
  --parallel-script-path /content/screener-colab-appsheet-parallel.py \
  --out-dir /content/dashboard_analysis_output
```

All-stocks AI:

```python
!python dashboard_heavy_analysis_colab.py \
  --dashboard-xlsx /content/downloaded_dashboard/gas_stock_tracker_dashboard.xlsx \
  --use-ai \
  --ai-mode all \
  --docs-dir /content \
  --parallel-script-path /content/screener-colab-appsheet-parallel.py \
  --out-dir /content/dashboard_analysis_output
```

Faster all-stocks AI with parallel NVIDIA calls:

```python
!python dashboard_heavy_analysis_colab.py \
  --dashboard-xlsx /content/downloaded_dashboard/gas_stock_tracker_dashboard.xlsx \
  --use-ai \
  --ai-mode all \
  --ai-workers 14 \
  --ai-timeout-sec 25 \
  --ai-max-tokens 280 \
  --docs-dir /content \
  --parallel-script-path /content/screener-colab-appsheet-parallel.py \
  --out-dir /content/dashboard_analysis_output
```

Notes:

- `--ai-workers 0` means auto-size from NVIDIA key count.
- with your current parallel tracker keys, auto mode will fan out across NVIDIA keys instead of sending one request at a time.
- if Colab or NVIDIA starts rate-limiting, reduce `--ai-workers` to `8` or `10`.
- `--ai-max-tokens 280` keeps the AI reply compact and faster.
- repeated reruns with the same output folder now reuse `dashboard_ai_nvidia_cache.json`, which makes results more stable and much faster.

Stable rerun command with an explicit cache file:

```python
!python dashboard_heavy_analysis_colab.py \
  --dashboard-xlsx /content/downloaded_dashboard/gas_stock_tracker_dashboard.xlsx \
  --use-ai \
  --ai-mode all \
  --ai-workers 14 \
  --ai-timeout-sec 25 \
  --ai-max-tokens 280 \
  --ai-cache-file /content/dashboard_ai_nvidia_cache.json \
  --docs-dir /content \
  --parallel-script-path /content/screener-colab-appsheet-parallel.py \
  --out-dir /content/dashboard_analysis_output
```

## What It Does

- reads the `Dashboard` sheet only
- normalizes the dashboard columns into typed rows
- scores every stock with a non-AI scenario engine
- loads and parses all core tracker markdown docs
- retrieves the most relevant doc sections per stock
- tags each stock against multiple scenario families
- ranks the strongest upside candidates
- optionally refines the candidates with NVIDIA NIM using dashboard data plus matched doc context
- writes:
  - `analysis_report.md`
  - `rankings.csv`
  - `analysis_full.json`
  - `guide.md`

## Recommendation Fixes Now Applied

These fixes were added after runtime review showed overly aggressive recommendations:

- `WATCH` rows are no longer treated like strong actionable entries in the core ranking model.
- the `best_stock` selector now prefers only active rows that are not excluded, have `BUY NOW` or `ACCUMULATE`, and have at least `2` live MTF confirmations.
- score inflation was reduced, so fewer rows should pin at `100`.
- ranking order now prefers actionability and live strength over weak watchlist persistence.
- markdown retrieval was tightened so persistence-style rows are less likely to get generic breakout sections as their top doc match.
- `Historical MTF` wording and prompt usage were corrected to the new price-based meaning.

## Speed Optimizations Now Applied

- NVIDIA AI requests now run in parallel instead of one-by-one.
- worker count can auto-scale from the number of NVIDIA keys found in `screener-colab-appsheet-parallel.py`.
- AI prompts were trimmed to fewer doc snippets and shorter strengths/risks context.
- per-request token budget was reduced to improve turnaround.
- per-request timeout is now configurable from CLI.
- repeated same-input reruns can reuse a persistent NVIDIA AI cache file instead of re-calling the model.

## What Changed Versus The Older Analyzer Behavior

- earlier, a `WATCH` stock could still become `BEST STOCK` if it floated to the top of the score list.
- earlier, many rows could saturate at `100`, which made the ordering unreliable.
- earlier, `persistent_leadership` rows could attach overly generic docs like breakout continuation sections.
- now, the analyzer is more conservative and tries to separate:
  - actionable live candidates
  - constructive watchlist candidates
  - historical or weaker-context rows

## How To Read The Result

- `best_stock` is now a stricter top current upside candidate from the dashboard snapshot, not just the highest loose score.
- `MTF Alignment` is the live active-now scanner breadth across `D / W / M`.
- `Historical MTF` is now price-based `D / W / M` structure from Yahoo history resampled into daily, weekly, and monthly bars.
- `Historical MTF` is not scanner-history anymore.
- if `Historical MTF` is stronger than `MTF Alignment`, the stock's actual D / W / M price structure looks healthier than its current scanner breadth.
- if `MTF Alignment` is stronger than `Historical MTF`, scanner breadth is live now but higher-timeframe price structure is weaker.
- if `Historical MTF` is blank, usable Yahoo history was not sufficient for the price-based D / W / M calculation.
- `Quick Action`, `Risk Tag`, `BB Signal`, `Cam Setup`, and `Volume Buzz` are used together, not alone.
- the report includes `Relevant Documentation Context` for the best stock.
- if docs are missing in Colab, the console summary and JSON output show which files were not loaded.

## Output Scope

- console output shows the top 10 ranked rows only
- `analysis_report.md` also summarizes the top 10
- `rankings.csv` contains all ranked rows
- `analysis_full.json` contains all ranked rows plus detailed payloads

So if you want all rows, open:

- `rankings.csv`
- `analysis_full.json`

## AI vs Non-AI

Non-AI mode still works well because it uses:

- `Signal`
- `Quick Action`
- `Consensus Score` if present
- `MTF Alignment`
- `Historical MTF`
- `Risk Tag`
- `BB Signal`
- `Cam Setup`
- `Volume Buzz`
- `Momentum Rank`
- `ADX`, `+DI`, `-DI`, `RSI`, `NATR`
- persistence fields like `Total Appearances` and `Unique Scanners`

AI mode adds:

- an extra per-candidate upside review
- a risk-vs-reward sanity check
- a score adjustment on the analyzed live candidates

## Known Limits

- this is still a ranking assistant, not a guarantee engine
- if the dashboard row itself is stale or wrong, the recommendation can still be wrong
- if uploaded markdown docs are missing, the analyzer still runs but with weaker context
- console output and `analysis_report.md` show only the top 10, while full ranking is in `rankings.csv` and `analysis_full.json`
- AI mode can still vary slightly between truly fresh runs because model output is probabilistic, but this is reduced by deterministic settings and cache reuse
- `Historical MTF` depends on the dashboard value already being populated correctly by the tracker pipeline

## If The Result Still Looks Wrong

Check these first:

- did the row have `WATCH` but still look too high in the top 10
- did too many names still cluster near the same score
- did the top doc section look unrelated to the row scenario
- did the dashboard workbook have stale `Quick Action`, `Signal`, or `Historical MTF`

If that happens, inspect:

- `rankings.csv` for full ordering
- `analysis_full.json` for score breakdown, scenario hits, and doc matches

Those two files are the best place to see why a stock ranked where it did.

## Recommended Commands

Best balanced run:

```python
!python dashboard_heavy_analysis_colab.py \
  --dashboard-xlsx /content/downloaded_dashboard/gas_stock_tracker_dashboard.xlsx \
  --docs-dir /content \
  --use-ai \
  --ai-mode top \
  --ai-top-n 12 \
  --parallel-script-path /content/screener-colab-appsheet-parallel.py \
  --out-dir /content/dashboard_analysis_output
```

True all-stock AI run:

```python
!python dashboard_heavy_analysis_colab.py \
  --dashboard-xlsx /content/downloaded_dashboard/gas_stock_tracker_dashboard.xlsx \
  --docs-dir /content \
  --use-ai \
  --ai-mode all \
  --parallel-script-path /content/screener-colab-appsheet-parallel.py \
  --out-dir /content/dashboard_analysis_output
```
