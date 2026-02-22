#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

for y in {2015..2024}; do
  echo "\n==================== YEAR $y ===================="

  if [[ -n "${SOCRATA_APP_TOKEN:-}" ]]; then
    python3 01_download_ideam_api.py \
      --department RISARALDA \
      --municipality PEREIRA \
      --start-date ${y}-01-01 \
      --end-date ${y}-12-31 \
      --limit 1000 \
      --timeout 20 \
      --sleep 3 \
      --max-attempts 8 \
      --app-token "$SOCRATA_APP_TOKEN"
  else
    python3 01_download_ideam_api.py \
      --department RISARALDA \
      --municipality PEREIRA \
      --start-date ${y}-01-01 \
      --end-date ${y}-12-31 \
      --limit 1000 \
      --timeout 20 \
      --sleep 3 \
      --max-attempts 8
  fi

  echo "Year $y completed."
  sleep 5
done

echo "\nAll years completed (2015-2024)."
