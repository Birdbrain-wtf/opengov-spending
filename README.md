# OpenGov spending: Kusama and Polkadot

Every treasury spend Kusama and Polkadot approved through OpenGov, from November 2022 to 8 November 2026, priced in US dollars, with an estimate of what the same work would cost a new network using agentic development.

**Read the report: [REPORT.md](REPORT.md)**

| | |
| --- | ---: |
| Approved through OpenGov | US$305.7m |
| Polkadot (from June 2023) | US$289.9m |
| Kusama (from November 2022) | US$15.8m |
| Referenda with a spend | 965 |
| Paid in DOT or KSM | 82% |
| Those tokens at 8 November 2026 prices | 15% of their value on the day |
| Software and infrastructure share | 37% |
| Same work with agentic development (assumptions) | US$204.6m to US$246.4m |

## The spreadsheet

GitHub shows each CSV as a searchable table. The same tables are in one workbook, [`opengov-spending.xlsx`](opengov-spending.xlsx).

| File | What it holds |
| --- | --- |
| [`data/spend-lines.csv`](data/spend-lines.csv) | One row per spend: referendum, date, track, title, category, asset, amount, price, US$ on the day, US$ at today's price, payout status, link |
| [`data/referenda.csv`](data/referenda.csv) | One row per referendum, largest first |
| [`data/summary-by-year.csv`](data/summary-by-year.csv) | Totals by network and year |
| [`data/summary-by-category.csv`](data/summary-by-category.csv) | Totals by category |
| [`data/summary-by-network-category.csv`](data/summary-by-network-category.csv) | Totals by network and category |
| [`data/agentic-cost-model.csv`](data/agentic-cost-model.csv) | The model's assumptions, with the reasoning for each, and its results |
| [`data/governance-tooling.csv`](data/governance-tooling.csv) | Every governance tooling spend, by platform |
| [`data/raw-prices/`](data/raw-prices/) | Daily DOT and KSM prices used |

Columns worth knowing:

- `usd_at_approval` is the amount at the closing price on the day the referendum was enacted. Stablecoins count at US$1.
- `counted` is `no` where the spend expired, was voided, or failed and was re-approved later. `usd_counted` is zero on those lines.
- `category_method` says whether a category was set by hand (`manual`) or by keyword (`keyword`).
- `agentic_low_usd` and `agentic_high_usd` come from the model. They are assumptions, not measurements.

## Method in one paragraph

All referenda come from Subsquare's public API. For every enacted referendum the proposal's calls are decoded, including those nested in batches and whitelisted calls: treasury spends in any asset, bounty approvals and multi-asset bounty funding. Two cross-chain transfers were decoded by hand (`inputs/overrides.csv`). Payout status for scheduled spends comes from the treasury spend index. Categories for the 320 largest referenda (93% of value) were set by reading each one, the rest by keyword. The caveats are in section 5 of the report.

## Rebuild it

```bash
bash scripts/run.sh            # fetch everything and rebuild
SKIP_FETCH=1 bash scripts/run.sh   # rebuild from .cache/raw
```

Needs Python 3 with `matplotlib` and `openpyxl`. Hand-set inputs are in `inputs/`: change a category, a status or an assumption there and rerun.

## Corrections

Open an issue or a pull request. Categories and the model's assumptions are the parts most worth arguing with.

Written by [Birdbrain](https://birdbrain.wtf). Our interest is set out in section 6 of the report. Data and text CC BY 4.0, code MIT.
