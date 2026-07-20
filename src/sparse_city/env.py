"""Synthetic sparse city POMDP-lite environment.

Grid is fully invented (Toyville). No real geographies, no Somaliland
personal data, no DTLA LIDAR, no Planet City exhibition assets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

LAND_USES = ("residential", "commercial", "industrial", "park")
HAZARDS = ("none", "flood", "fire")


class ActionKind(str, Enum):
    MOVE = "MOVE"
    QUERY = "QUERY"
    ANSWER = "ANSWER"
    ABSTAIN = "ABSTAIN"


@dataclass(frozen=True)
class PriceTable:
    """Priced observation queries (synthetic units)."""

    land_use_cell: float = 3.0
    hazard_cell: float = 2.0
    land_use_layer: float = 12.0
    hazard_layer: float = 8.0
    move: float = 0.0


DEFAULT_PRICES = PriceTable()


@dataclass
class EpisodeConfig:
    seed: int = 42
    width: int = 3
    height: int = 3
    budget: float = 10.0
    target: Tuple[int, int] = (1, 1)
    start: Tuple[int, int] = (0, 0)
    lambda_info: float = 0.05
    mu_wrong: float = 2.0
    delta_abstain: float = 0.1
    max_steps: int = 16
    prices: PriceTable = field(default_factory=PriceTable)


@dataclass
class HiddenCity:
    land_use: np.ndarray  # (H, W) int indices into LAND_USES
    hazard: np.ndarray  # (H, W) int indices into HAZARDS


def generate_city(cfg: EpisodeConfig) -> HiddenCity:
    rng = np.random.default_rng(cfg.seed)
    land_use = rng.integers(0, len(LAND_USES), size=(cfg.height, cfg.width))
    hazard = rng.integers(0, len(HAZARDS), size=(cfg.height, cfg.width))
    # Seeded ambiguity trap: target land_use is often hard without query.
    # Keep deterministic under seed — do not overwrite after draw; instead
    # document that agents must query or abstain when belief is flat.
    return HiddenCity(land_use=land_use, hazard=hazard)


@dataclass
class Belief:
    """Partial observability: known cells / layers only after QUERY."""

    known_land_use: Dict[Tuple[int, int], int] = field(default_factory=dict)
    known_hazard: Dict[Tuple[int, int], int] = field(default_factory=dict)
    saw_full_land_use: bool = False
    saw_full_hazard: bool = False


class SparseCityEnv:
    """Gymnasium-shaped but self-contained; no exhibition assets."""

    metadata = {"render_modes": ["ansi"]}

    def __init__(self, config: Optional[EpisodeConfig] = None):
        self.config = config or EpisodeConfig()
        self.prices = self.config.prices
        self.city: Optional[HiddenCity] = None
        self.belief = Belief()
        self.agent_pos = self.config.start
        self.budget_left = self.config.budget
        self.info_cost = 0.0
        self.steps = 0
        self.done = False
        self.last_outcome: Optional[str] = None
        self.history: List[Dict[str, Any]] = []

    def reset(self, seed: Optional[int] = None) -> Dict[str, Any]:
        if seed is not None:
            self.config.seed = seed
        self.city = generate_city(self.config)
        self.belief = Belief()
        self.agent_pos = self.config.start
        self.budget_left = self.config.budget
        self.info_cost = 0.0
        self.steps = 0
        self.done = False
        self.last_outcome = None
        self.history = []
        return self.observe()

    def observe(self) -> Dict[str, Any]:
        assert self.city is not None
        ty, tx = self.config.target
        return {
            "pos": self.agent_pos,
            "target": self.config.target,
            "budget_left": self.budget_left,
            "info_cost": self.info_cost,
            "steps": self.steps,
            "known_land_use": dict(self.belief.known_land_use),
            "known_hazard": dict(self.belief.known_hazard),
            "saw_full_land_use": self.belief.saw_full_land_use,
            "saw_full_hazard": self.belief.saw_full_hazard,
            "width": self.config.width,
            "height": self.config.height,
            "land_use_labels": list(LAND_USES),
            "hazard_labels": list(HAZARDS),
            # Soft prior only — not ground truth. Agents must not treat as answer.
            "fog_hint": "partial; no free target land_use",
            "target_known_land_use": self.belief.known_land_use.get((ty, tx)),
            "target_known_hazard": self.belief.known_hazard.get((ty, tx)),
        }

    def ground_truth_target_land_use(self) -> int:
        assert self.city is not None
        ty, tx = self.config.target
        return int(self.city.land_use[ty, tx])

    def _charge(self, cost: float) -> bool:
        if cost > self.budget_left + 1e-9:
            return False
        self.budget_left -= cost
        self.info_cost += cost
        return True

    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        if self.done:
            raise RuntimeError("episode already finished")
        assert self.city is not None
        self.steps += 1
        kind = ActionKind(action["kind"])
        reward = 0.0
        info: Dict[str, Any] = {"action": action}

        if kind == ActionKind.MOVE:
            dy, dx = action.get("delta", (0, 0))
            y = int(np.clip(self.agent_pos[0] + dy, 0, self.config.height - 1))
            x = int(np.clip(self.agent_pos[1] + dx, 0, self.config.width - 1))
            self.agent_pos = (y, x)
            self._charge(self.prices.move)
            info["pos"] = self.agent_pos

        elif kind == ActionKind.QUERY:
            q = action["query"]
            ok, detail = self._apply_query(q)
            info["query_ok"] = ok
            info["query_detail"] = detail
            if not ok:
                reward = -0.01  # tiny invalid-action nudge

        elif kind == ActionKind.ANSWER:
            guess = int(action["land_use"])
            truth = self.ground_truth_target_land_use()
            correct = guess == truth
            if correct:
                reward = 1.0 - self.config.lambda_info * self.info_cost
                self.last_outcome = "correct"
            else:
                reward = -self.config.mu_wrong - self.config.lambda_info * self.info_cost
                self.last_outcome = "wrong"
            self.done = True
            info.update(
                {
                    "guess": guess,
                    "truth": truth,
                    "correct": correct,
                    "outcome": self.last_outcome,
                }
            )

        elif kind == ActionKind.ABSTAIN:
            # Abstain is explicitly scored: small cost, avoids mu_wrong.
            reward = -self.config.delta_abstain - self.config.lambda_info * self.info_cost
            self.last_outcome = "abstain"
            self.done = True
            info["outcome"] = "abstain"
            info["truth"] = self.ground_truth_target_land_use()

        else:
            raise ValueError(f"unknown action kind: {kind}")

        if self.steps >= self.config.max_steps and not self.done:
            # Forced timeout → treat as abstain-scored (not free maze wander).
            reward = -self.config.delta_abstain - self.config.lambda_info * self.info_cost
            self.last_outcome = "timeout_abstain"
            self.done = True
            info["outcome"] = self.last_outcome
            info["truth"] = self.ground_truth_target_land_use()

        self.history.append({"action": action, "reward": reward, "info": info})
        return self.observe(), reward, self.done, info

    def _in_bounds(self, y: int, x: int) -> bool:
        return 0 <= y < self.config.height and 0 <= x < self.config.width

    def _apply_query(self, q: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        assert self.city is not None
        if not isinstance(q, dict) or "type" not in q:
            return False, {"reason": "malformed_query"}
        qtype = q["type"]
        if qtype == "land_use_cell":
            try:
                y, x = int(q["y"]), int(q["x"])
            except (KeyError, TypeError, ValueError):
                return False, {"reason": "malformed_query"}
            if not self._in_bounds(y, x):
                return False, {"reason": "out_of_bounds", "y": y, "x": x}
            cost = self.prices.land_use_cell
            if not self._charge(cost):
                return False, {"reason": "budget"}
            val = int(self.city.land_use[y, x])
            self.belief.known_land_use[(y, x)] = val
            return True, {"y": y, "x": x, "land_use": val, "cost": cost}

        if qtype == "hazard_cell":
            try:
                y, x = int(q["y"]), int(q["x"])
            except (KeyError, TypeError, ValueError):
                return False, {"reason": "malformed_query"}
            if not self._in_bounds(y, x):
                return False, {"reason": "out_of_bounds", "y": y, "x": x}
            cost = self.prices.hazard_cell
            if not self._charge(cost):
                return False, {"reason": "budget"}
            val = int(self.city.hazard[y, x])
            self.belief.known_hazard[(y, x)] = val
            return True, {"y": y, "x": x, "hazard": val, "cost": cost}

        if qtype == "land_use_layer":
            cost = self.prices.land_use_layer
            if not self._charge(cost):
                return False, {"reason": "budget"}
            for y in range(self.config.height):
                for x in range(self.config.width):
                    self.belief.known_land_use[(y, x)] = int(self.city.land_use[y, x])
            self.belief.saw_full_land_use = True
            return True, {"cost": cost, "layer": "land_use"}

        if qtype == "hazard_layer":
            cost = self.prices.hazard_layer
            if not self._charge(cost):
                return False, {"reason": "budget"}
            for y in range(self.config.height):
                for x in range(self.config.width):
                    self.belief.known_hazard[(y, x)] = int(self.city.hazard[y, x])
            self.belief.saw_full_hazard = True
            return True, {"cost": cost, "layer": "hazard"}

        return False, {"reason": "unknown_query"}

    def render_ansi(self) -> str:
        assert self.city is not None
        lines = [
            f"sparse-city seed={self.config.seed} pos={self.agent_pos} "
            f"budget={self.budget_left:.1f} info_cost={self.info_cost:.1f}",
            "fogged belief (L=land_use known, H=hazard known, .=unknown):",
        ]
        for y in range(self.config.height):
            row = []
            for x in range(self.config.width):
                mark = ""
                if (y, x) in self.belief.known_land_use:
                    mark += "L"
                if (y, x) in self.belief.known_hazard:
                    mark += "H"
                if not mark:
                    mark = "."
                if (y, x) == self.config.target:
                    mark = f"[{mark}]"
                elif (y, x) == self.agent_pos:
                    mark = f"<{mark}>"
                row.append(f"{mark:^5}")
            lines.append(" ".join(row))
        return "\n".join(lines)
