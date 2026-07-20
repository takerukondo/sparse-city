"""Unit: abstain vs wrong-answer penalty ordering + kill gate."""

from sparse_city.agents import get_agent
from sparse_city.env import EpisodeConfig, SparseCityEnv
from sparse_city.scoring import assert_abstain_scored, build_scorecard


def test_abstain_better_than_wrong_answer():
    cfg = EpisodeConfig(seed=42, mu_wrong=2.0, delta_abstain=0.1, lambda_info=0.05)

    env_a = SparseCityEnv(cfg)
    env_a.reset(seed=42)
    truth = env_a.ground_truth_target_land_use()
    wrong = (truth + 1) % 4
    _, r_wrong, done_w, _ = env_a.step({"kind": "ANSWER", "land_use": wrong})
    assert done_w
    assert env_a.last_outcome == "wrong"

    env_b = SparseCityEnv(cfg)
    env_b.reset(seed=42)
    _, r_abs, done_a, _ = env_b.step({"kind": "ABSTAIN"})
    assert done_a
    assert env_b.last_outcome == "abstain"

    assert r_abs > r_wrong
    assert abs(r_abs - (-cfg.delta_abstain)) < 1e-9
    assert abs(r_wrong - (-cfg.mu_wrong)) < 1e-9


def test_zero_budget_threshold_abstains_and_is_scored():
    cfg = EpisodeConfig(seed=99, budget=0.0)
    env = SparseCityEnv(cfg)
    agent = get_agent("threshold_abstain")
    obs = env.reset(seed=99)
    total = 0.0
    last = {}
    while True:
        obs, r, done, info = env.step(agent.act(obs))
        total += r
        last = info
        if done:
            break

    card = build_scorecard(
        seed=99,
        agent="threshold_abstain",
        outcome=env.last_outcome or "",
        reward=total,
        info_cost=env.info_cost,
        budget_left=env.budget_left,
        steps=env.steps,
        truth_land_use=last.get("truth"),
        guess_land_use=last.get("guess"),
        abstained=True,
        trajectory=[],
        lambda_info=cfg.lambda_info,
        mu_wrong=cfg.mu_wrong,
        delta_abstain=cfg.delta_abstain,
    )
    assert_abstain_scored(card)
    assert card["abstained"] is True
    assert card["metrics"]["abstain_scored"] is True
    assert card["outcome"] == "abstain"


def test_kill_gate_missing_abstain_fields():
    bad = {"schema": "x", "metrics": {"task_accuracy": 0.0}}
    try:
        assert_abstain_scored(bad)
        raise AssertionError("expected AssertionError")
    except AssertionError as e:
        assert "abstain" in str(e).lower()
