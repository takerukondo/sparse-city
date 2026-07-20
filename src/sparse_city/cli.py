"""CLI: sparse-city eval --agent greedy_abstain"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from sparse_city.agents import AGENT_REGISTRY
from sparse_city.eval import leaderboard, run_episode, run_fixture, write_seed42_artifacts
from sparse_city.scoring import assert_abstain_scored


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sparse-city",
        description=(
            "Partial-observability city planning toy: "
            "buy information vs act vs abstain under budget. "
            "Synthetic grids only."
        ),
    )
    sub = p.add_subparsers(dest="command", required=True)

    ev = sub.add_parser("eval", help="Run one agent episode and emit scorecard JSON")
    ev.add_argument(
        "--agent",
        default="greedy_abstain",
        choices=sorted(AGENT_REGISTRY.keys()),
        help="Baseline agent name",
    )
    ev.add_argument("--seed", type=int, default=42)
    ev.add_argument(
        "--fixture",
        default=None,
        help="Fixture name under fixtures/episodes/ (e.g. seed42)",
    )
    ev.add_argument(
        "--write-benchmarks",
        action="store_true",
        help="Also write benchmarks/seed42/ scorecard + leaderboard",
    )

    lb = sub.add_parser("leaderboard", help="Compare baselines on a seed")
    lb.add_argument("--seed", type=int, default=42)

    demo = sub.add_parser("demo", help="10s demo: wasteful vs abstain scorecards")
    demo.add_argument("--seed", type=int, default=42)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "eval":
        if args.fixture:
            card = run_fixture(args.fixture, args.agent)
        else:
            card = run_episode(args.agent, seed=args.seed)
        assert_abstain_scored(card)
        if args.write_benchmarks and args.seed == 42:
            write_seed42_artifacts(args.agent)
        print(json.dumps(card, indent=2, sort_keys=True))
        return 0

    if args.command == "leaderboard":
        board = leaderboard(seed=args.seed)
        print(json.dumps(board, indent=2, sort_keys=True))
        return 0

    if args.command == "demo":
        from sparse_city.env import EpisodeConfig
        from sparse_city.eval import run_episode as _run

        waste = run_episode("wasteful_buyer", seed=args.seed)
        wise = run_episode("greedy_abstain", seed=args.seed)
        # Low budget → cannot buy land_use_cell (cost 3) → abstain scored.
        abstain_card = _run(
            "threshold_abstain",
            seed=args.seed,
            config=EpisodeConfig(seed=args.seed, budget=2.0),
        )
        print("=== 1) wasteful_buyer: buys costly hazard layer, then wrong guess ===")
        print(
            json.dumps(
                {
                    "outcome": waste["outcome"],
                    "reward": waste["reward"],
                    "info_cost": waste["info_cost"],
                    "abstained": waste["abstained"],
                },
                indent=2,
            )
        )
        print("=== 2) greedy_abstain: buys target land_use cell, answers ===")
        print(
            json.dumps(
                {
                    "outcome": wise["outcome"],
                    "reward": wise["reward"],
                    "info_cost": wise["info_cost"],
                    "abstained": wise["abstained"],
                },
                indent=2,
            )
        )
        print("=== 3) threshold_abstain @ budget=2: uncertain → ABSTAIN (avoids μ) ===")
        print(
            json.dumps(
                {
                    "outcome": abstain_card["outcome"],
                    "reward": abstain_card["reward"],
                    "info_cost": abstain_card["info_cost"],
                    "abstained": abstain_card["abstained"],
                    "mu_wrong_avoided": abstain_card["metrics"]["mu_wrong"],
                },
                indent=2,
            )
        )
        print(
            "\nTakeaway: buy the useful observation; abstain when the evidence is not worth its price."
        )
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
