"""Optional Gymnasium adapter around SparseCityEnv."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import gymnasium as gym
from gymnasium import spaces

from sparse_city.env import EpisodeConfig, SparseCityEnv


class SparseCityGymnasium(gym.Env):
    """Thin adapter; dict actions for QUERY/ANSWER/ABSTAIN remain primary API."""

    metadata = {"render_modes": ["ansi"]}

    def __init__(self, config: Optional[EpisodeConfig] = None):
        super().__init__()
        self._env = SparseCityEnv(config)
        # Placeholder spaces — real control uses dict actions via step_dict.
        self.observation_space = spaces.Dict(
            {
                "budget_left": spaces.Box(low=0.0, high=1e6, shape=(), dtype=float),
                "info_cost": spaces.Box(low=0.0, high=1e6, shape=(), dtype=float),
            }
        )
        self.action_space = spaces.Discrete(4)  # MOVE/QUERY/ANSWER/ABSTAIN indices unused

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        obs = self._env.reset(seed=seed)
        return obs, {}

    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float, bool, bool, Dict[str, Any]]:
        obs, reward, done, info = self._env.step(action)
        return obs, reward, done, False, info

    def render(self):
        return self._env.render_ansi()
