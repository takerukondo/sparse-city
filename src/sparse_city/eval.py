"""Deterministic evaluation runner → JSON scorecards."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sparse_city.agents import get_agent
from sparse_city.env import EpisodeConfig, SparseCityEnv
from sparse_city.scoring import assert_abstain_scored, build_scorecard

ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS = ROOT / "benchmarks"
FIXTURES = ROOT / "fixtures" / "episodes"


def run_episode(
    agent_name: str,
    seed: int = 42,
    config: Optional[EpisodeConfig] = None,
) -> Dict[str, Any]:
    cfg = config or EpisodeConfig(seed=seed)
    cfg.seed = seed
    env = SparseCityEnv(cfg)
    agent = get_agent(agent_name)
    # Fresh agent instance each episode (stateful baselines).
    obs = env.reset(seed=seed)
    total_reward = 0.0
    last_info: Dict[str, Any] = {}
    while True:
        action = agent.act(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        last_info = info
        if done:
            break

    outcome = env.last_outcome or "unknown"
    abstained = outcome in {"abstain", "timeout_abstain"}
    traj = [
        {
            "action": h["action"],
            "reward": round(float(h["reward"]), 6),
            "outcome": (h.get("info") or {}).get("outcome"),
        }
        for h in env.history
    ]
    card = build_scorecard(
        seed=seed,
        agent=agent_name,
        outcome=outcome,
        reward=total_reward,
        info_cost=env.info_cost,
        budget_left=env.budget_left,
        steps=env.steps,
        truth_land_use=last_info.get("truth", env.ground_truth_target_land_use()),
        guess_land_use=last_info.get("guess"),
        abstained=abstained,
        trajectory=traj,
        lambda_info=cfg.lambda_info,
        mu_wrong=cfg.mu_wrong,
        delta_abstain=cfg.delta_abstain,
    )
    assert_abstain_scored(card)
    return card


def _resolve_fixture_path(fixture_name: str) -> Path:
    """Resolve a fixture basename under fixtures/episodes/ (no path traversal)."""
    if (
        not fixture_name
        or fixture_name.strip() != fixture_name
        or "/" in fixture_name
        or "\\" in fixture_name
        or ".." in fixture_name
        or fixture_name.startswith(".")
    ):
        raise ValueError(
            f"invalid fixture name {fixture_name!r}: use a single basename "
            "(e.g. 'seed42'), no path separators"
        )
    root = FIXTURES.resolve()
    path = (FIXTURES / f"{fixture_name}.json").resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            f"fixture path escapes fixtures/episodes/: {fixture_name!r}"
        ) from exc
    return path


def _coord_pair(raw: Any, *, field: str, default: Tuple[int, int]) -> Tuple[int, int]:
    if raw is None:
        return default
    if not isinstance(raw, (list, tuple)) or len(raw) != 2:
        raise ValueError(f"fixture field {field!r} must be [y, x] with two integers")
    try:
        return (int(raw[0]), int(raw[1]))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"fixture field {field!r} must be [y, x] integers") from exc


def _positive_int(raw: Any, *, field: str, default: int) -> int:
    if raw is None:
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"fixture field {field!r} must be an integer") from exc
    if value <= 0:
        raise ValueError(f"fixture field {field!r} must be positive (got {value})")
    return value


def _nonneg_float(raw: Any, *, field: str, default: float) -> float:
    if raw is None:
        return default
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"fixture field {field!r} must be a number") from exc
    if value < 0:
        raise ValueError(f"fixture field {field!r} must be >= 0 (got {value})")
    return value


def load_fixture_config(fixture_name: str) -> EpisodeConfig:
    """Load and validate a synthetic episode fixture → EpisodeConfig."""
    path = _resolve_fixture_path(fixture_name)
    if not path.exists():
        if fixture_name == "seed42":
            return EpisodeConfig(seed=42)
        raise FileNotFoundError(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed fixture JSON ({path.name}): {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(
            f"fixture must be a JSON object ({path.name}); got {type(data).__name__}"
        )

    if "seed" in data:
        try:
            seed = int(data["seed"])
        except (TypeError, ValueError) as exc:
            raise ValueError("fixture field 'seed' must be an integer") from exc
        if seed < 0:
            raise ValueError(f"fixture field 'seed' must be >= 0 (got {seed})")
    else:
        seed = 42

    width = _positive_int(data.get("width"), field="width", default=3)
    height = _positive_int(data.get("height"), field="height", default=3)
    budget = _nonneg_float(data.get("budget"), field="budget", default=10.0)
    target = _coord_pair(data.get("target"), field="target", default=(1, 1))
    start = _coord_pair(data.get("start"), field="start", default=(0, 0))
    for name, pair in (("target", target), ("start", start)):
        y, x = pair
        if not (0 <= y < height and 0 <= x < width):
            raise ValueError(
                f"fixture field {name!r} {pair} out of bounds for "
                f"{height}x{width} grid"
            )
    max_steps = _positive_int(data.get("max_steps"), field="max_steps", default=16)
    try:
        lambda_info = float(data.get("lambda_info", 0.05))
        mu_wrong = float(data.get("mu_wrong", 2.0))
        delta_abstain = float(data.get("delta_abstain", 0.1))
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "fixture fields lambda_info / mu_wrong / delta_abstain must be numbers"
        ) from exc

    return EpisodeConfig(
        seed=seed,
        width=width,
        height=height,
        budget=budget,
        target=target,
        start=start,
        lambda_info=lambda_info,
        mu_wrong=mu_wrong,
        delta_abstain=delta_abstain,
        max_steps=max_steps,
    )


def run_fixture(fixture_name: str, agent_name: str) -> Dict[str, Any]:
    cfg = load_fixture_config(fixture_name)
    return run_episode(agent_name, seed=cfg.seed, config=cfg)


def leaderboard(seed: int = 42, agents: Optional[List[str]] = None) -> Dict[str, Any]:
    names = agents or [
        "always_guess",
        "wasteful_buyer",
        "threshold_abstain",
        "greedy_abstain",
    ]
    rows = []
    for name in names:
        card = run_episode(name, seed=seed)
        rows.append(
            {
                "agent": name,
                "reward": card["reward"],
                "outcome": card["outcome"],
                "info_cost": card["info_cost"],
                "abstained": card["abstained"],
                "scorecard_hash": card["scorecard_hash"],
            }
        )
    rows.sort(key=lambda r: r["reward"], reverse=True)
    return {
        "schema": "sparse-city.leaderboard.v1",
        "seed": seed,
        "rows": rows,
    }


def write_seed42_artifacts(agent_name: str = "greedy_abstain") -> Path:
    out_dir = BENCHMARKS / "seed42"
    out_dir.mkdir(parents=True, exist_ok=True)
    card = run_episode(agent_name, seed=42)
    path = out_dir / f"scorecard_{agent_name}.json"
    path.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    board = leaderboard(seed=42)
    (out_dir / "leaderboard.json").write_text(
        json.dumps(board, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return path
