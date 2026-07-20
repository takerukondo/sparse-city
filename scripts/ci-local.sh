#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -d .venv ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

pytest -q
python -m sparse_city eval --fixture seed42 --agent greedy_abstain >/dev/null
echo "ci-local OK"
