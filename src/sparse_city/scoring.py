"""Scorecard construction and reproducibility helpers."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional


SCORECARD_SCHEMA_VERSION = "sparse-city.scorecard.v1"


def build_scorecard(
    *,
    seed: int,
    agent: str,
    outcome: str,
    reward: float,
    info_cost: float,
    budget_left: float,
    steps: int,
    truth_land_use: Optional[int],
    guess_land_use: Optional[int],
    abstained: bool,
    trajectory: List[Dict[str, Any]],
    lambda_info: float,
    mu_wrong: float,
    delta_abstain: float,
) -> Dict[str, Any]:
    """Build a JSON-serializable scorecard.

    Kill gate: `abstained` and abstain-related fields must always be present
    so abstain is part of scoring, not a silent no-op.
    """
    card = {
        "schema": SCORECARD_SCHEMA_VERSION,
        "seed": seed,
        "agent": agent,
        "outcome": outcome,
        "reward": round(float(reward), 6),
        "info_cost": round(float(info_cost), 6),
        "budget_left": round(float(budget_left), 6),
        "steps": int(steps),
        "truth_land_use": truth_land_use,
        "guess_land_use": guess_land_use,
        "abstained": bool(abstained),
        "metrics": {
            "task_accuracy": 1.0 if outcome == "correct" else 0.0,
            "overconfidence_penalty_applied": outcome == "wrong",
            "abstain_scored": abstained or outcome in {"abstain", "timeout_abstain"},
            "lambda_info": lambda_info,
            "mu_wrong": mu_wrong,
            "delta_abstain": delta_abstain,
        },
        "trajectory": trajectory,
    }
    card["scorecard_hash"] = scorecard_hash(card)
    return card


def _canonical(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _canonical(obj[k]) for k in sorted(obj)}
    if isinstance(obj, list):
        return [_canonical(x) for x in obj]
    if isinstance(obj, float):
        return round(obj, 6)
    return obj


def scorecard_hash(card: Dict[str, Any]) -> str:
    payload = {k: v for k, v in card.items() if k != "scorecard_hash"}
    blob = json.dumps(_canonical(payload), separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def assert_abstain_scored(card: Dict[str, Any]) -> None:
    """Fail closed if abstain is missing from the scoring contract."""
    metrics = card.get("metrics") or {}
    if "abstain_scored" not in metrics:
        raise AssertionError("kill gate: abstain not scored (metrics.abstain_scored missing)")
    if "abstained" not in card:
        raise AssertionError("kill gate: abstain not scored (abstained missing)")
    if "delta_abstain" not in metrics:
        raise AssertionError("kill gate: abstain not scored (delta_abstain missing)")
