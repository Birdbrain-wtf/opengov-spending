#!/usr/bin/env bash
# Rebuild everything from public sources. Needs python3 with matplotlib and openpyxl.
set -euo pipefail
cd "$(dirname "$0")/.."
export RAW="${RAW:-.cache/raw}"
if [ "${SKIP_FETCH:-0}" != "1" ]; then
  for c in kusama polkadot; do python3 -I scripts/fetch_referenda.py "$c"; done
  for c in kusama polkadot; do for e in treasury/spends treasury/bounties; do python3 -I scripts/fetch_treasury.py "$c" "$e"; done; done
  python3 -I scripts/fetch_details.py
  python3 -I scripts/fetch_prices.py
  cp "$RAW"/price-*.csv data/raw-prices/
fi
mkdir -p .cache/build
python3 -I scripts/extract.py data/raw-prices .cache/build/extract.json inputs/overrides.csv
python3 -I scripts/categorise.py .cache/build/extract.json inputs/manual-categories.csv .cache/build/cat.json inputs/status-overrides.csv
python3 -I scripts/build.py .cache/build/cat.json inputs/model-assumptions.csv .
python3 -I scripts/charts.py .
python3 -I scripts/workbook.py .
