#!/usr/bin/env bash
# Rebuild the environment, run tests, and compare the baselines.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt
python -m pip install -q -e .

if [[ ! -f benchmarks/seed42/expected_greedy_abstain.json ]]; then
  python scripts/write_golden.py
fi

echo "=== pytest ==="
python -m pytest

echo ""
echo "=== demo ==="
python -m sparse_city demo --seed 42

echo ""
echo "=== eval greedy_abstain ==="
python -m sparse_city eval --agent greedy_abstain --fixture seed42

echo ""
echo "OK — tests, demo, and scorecard passed."
