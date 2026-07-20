"""Baseline ordering: always_guess worse than threshold_abstain on fixture set."""

from sparse_city.eval import leaderboard, run_episode


def test_threshold_abstain_beats_always_guess_on_seed42():
    guess = run_episode("always_guess", seed=42)
    abstain = run_episode("threshold_abstain", seed=42)
    assert abstain["reward"] > guess["reward"]


def test_greedy_abstain_beats_wasteful_buyer_on_seed42():
    waste = run_episode("wasteful_buyer", seed=42)
    wise = run_episode("greedy_abstain", seed=42)
    assert wise["reward"] > waste["reward"]


def test_leaderboard_orders_by_reward():
    board = leaderboard(seed=42)
    rewards = [r["reward"] for r in board["rows"]]
    assert rewards == sorted(rewards, reverse=True)
    names = {r["agent"] for r in board["rows"]}
    assert "always_guess" in names
    assert "threshold_abstain" in names
