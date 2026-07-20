"""Unit: price deduction from budget."""

from sparse_city.env import EpisodeConfig, SparseCityEnv


def test_land_use_cell_deducts_price():
    env = SparseCityEnv(EpisodeConfig(seed=42, budget=10.0))
    env.reset(seed=42)
    obs, reward, done, info = env.step(
        {"kind": "QUERY", "query": {"type": "land_use_cell", "y": 1, "x": 1}}
    )
    assert info["query_ok"] is True
    assert env.info_cost == 3.0
    assert env.budget_left == 7.0
    assert done is False
    assert obs["target_known_land_use"] is not None


def test_insufficient_budget_rejects_query():
    env = SparseCityEnv(EpisodeConfig(seed=42, budget=1.0))
    env.reset(seed=42)
    _, reward, done, info = env.step(
        {"kind": "QUERY", "query": {"type": "land_use_layer"}}
    )
    assert info["query_ok"] is False
    assert env.info_cost == 0.0
    assert env.budget_left == 1.0
    assert done is False
    assert reward < 0
