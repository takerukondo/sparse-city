"""Golden episode: seed42 trajectory → fixed scorecard hash."""

import json
from pathlib import Path

from sparse_city.eval import run_episode, run_fixture
from sparse_city.scoring import scorecard_hash

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "benchmarks" / "seed42" / "expected_greedy_abstain.json"


def test_seed42_greedy_abstain_matches_expected():
    card = run_fixture("seed42", "greedy_abstain")
    assert EXPECTED.exists(), "missing expected golden; regenerate via scripts/write_golden.py"
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    assert card["outcome"] == expected["outcome"]
    assert card["reward"] == expected["reward"]
    assert card["info_cost"] == expected["info_cost"]
    assert card["scorecard_hash"] == expected["scorecard_hash"]
    # Recompute hash from card body for bit-stability.
    assert scorecard_hash(card) == expected["scorecard_hash"]


def test_seed42_reproducible_across_calls():
    a = run_episode("greedy_abstain", seed=42)
    b = run_episode("greedy_abstain", seed=42)
    assert a["scorecard_hash"] == b["scorecard_hash"]
    assert a["trajectory"] == b["trajectory"]
