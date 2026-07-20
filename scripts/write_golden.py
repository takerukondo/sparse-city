#!/usr/bin/env python3
"""Regenerate benchmarks/seed42 expected scorecards (local only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sparse_city.eval import leaderboard, run_episode  # noqa: E402


def main() -> int:
    out = ROOT / "benchmarks" / "seed42"
    out.mkdir(parents=True, exist_ok=True)
    card = run_episode("greedy_abstain", seed=42)
    (out / "expected_greedy_abstain.json").write_text(
        json.dumps(card, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out / "scorecard_greedy_abstain.json").write_text(
        json.dumps(card, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    board = leaderboard(seed=42)
    (out / "leaderboard.json").write_text(
        json.dumps(board, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {out}")
    print(f"greedy_abstain hash={card['scorecard_hash']} reward={card['reward']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
