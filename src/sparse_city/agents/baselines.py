"""Baseline agents for the sparse-city eval bench."""

from __future__ import annotations

from typing import Any, Dict, Protocol


class Agent(Protocol):
    name: str

    def act(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        ...


class AlwaysGuessAgent:
    """Guess residential without buying information (overconfident baseline)."""

    name = "always_guess"

    def act(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        return {"kind": "ANSWER", "land_use": 0}


class WastefulBuyerAgent:
    """Buys expensive wrong layer (hazard), then guesses blindly (residential)."""

    name = "wasteful_buyer"

    def __init__(self) -> None:
        self._bought = False

    def act(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        if not self._bought and obs["budget_left"] >= 8.0:
            self._bought = True
            return {"kind": "QUERY", "query": {"type": "hazard_layer"}}
        # Still does not know land_use — overconfident residential guess.
        return {"kind": "ANSWER", "land_use": 0}


class ThresholdAbstainAgent:
    """Buy target land_use cell if affordable; else abstain if unknown."""

    name = "threshold_abstain"

    def act(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        ty, tx = obs["target"]
        known = obs["target_known_land_use"]
        if known is not None:
            return {"kind": "ANSWER", "land_use": int(known)}
        # Price for land_use_cell is 3.0 in default table.
        if obs["budget_left"] >= 3.0:
            return {
                "kind": "QUERY",
                "query": {"type": "land_use_cell", "y": ty, "x": tx},
            }
        return {"kind": "ABSTAIN"}


class GreedyAbstainAgent:
    """Prefer cheap target query; abstain rather than overconfident guess."""

    name = "greedy_abstain"

    def act(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        ty, tx = obs["target"]
        known = obs["target_known_land_use"]
        if known is not None:
            return {"kind": "ANSWER", "land_use": int(known)}
        if obs["budget_left"] >= 3.0 and not obs["saw_full_land_use"]:
            return {
                "kind": "QUERY",
                "query": {"type": "land_use_cell", "y": ty, "x": tx},
            }
        # Uncertain → abstain (avoids mu_wrong).
        return {"kind": "ABSTAIN"}


AGENT_REGISTRY = {
    AlwaysGuessAgent.name: AlwaysGuessAgent,
    WastefulBuyerAgent.name: WastefulBuyerAgent,
    ThresholdAbstainAgent.name: ThresholdAbstainAgent,
    GreedyAbstainAgent.name: GreedyAbstainAgent,
}


def get_agent(name: str) -> Agent:
    if name not in AGENT_REGISTRY:
        known = ", ".join(sorted(AGENT_REGISTRY))
        raise KeyError(f"unknown agent {name!r}; choose from: {known}")
    return AGENT_REGISTRY[name]()
