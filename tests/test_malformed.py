"""Hardening: malformed fixtures and out-of-bounds queries fail closed."""

from pathlib import Path

import pytest

from sparse_city.env import EpisodeConfig, SparseCityEnv
from sparse_city.eval import load_fixture_config, run_fixture

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "episodes"


def _write(name: str, body: str) -> Path:
    path = FIXTURES / f"{name}.json"
    path.write_text(body, encoding="utf-8")
    return path


def test_malformed_json_raises_value_error():
    path = _write("_rt_bad_json", "{not json")
    try:
        with pytest.raises(ValueError, match="malformed fixture JSON"):
            load_fixture_config("_rt_bad_json")
    finally:
        path.unlink(missing_ok=True)


def test_non_object_fixture_raises_value_error():
    path = _write("_rt_list", "[]")
    try:
        with pytest.raises(ValueError, match="JSON object"):
            load_fixture_config("_rt_list")
    finally:
        path.unlink(missing_ok=True)


def test_null_fixture_raises_value_error():
    path = _write("_rt_null", "null")
    try:
        with pytest.raises(ValueError, match="JSON object"):
            load_fixture_config("_rt_null")
    finally:
        path.unlink(missing_ok=True)


def test_bad_types_raise_value_error():
    path = _write("_rt_types", '{"seed": "nope", "width": 3, "height": 3}')
    try:
        with pytest.raises(ValueError, match="seed"):
            load_fixture_config("_rt_types")
    finally:
        path.unlink(missing_ok=True)


def test_negative_dimensions_rejected():
    path = _write(
        "_rt_neg",
        '{"seed": 1, "width": -1, "height": 3, "budget": 10, "target": [0, 0], "start": [0, 0]}',
    )
    try:
        with pytest.raises(ValueError, match="width"):
            load_fixture_config("_rt_neg")
    finally:
        path.unlink(missing_ok=True)


def test_out_of_bounds_target_rejected():
    path = _write(
        "_rt_oob_target",
        '{"seed": 1, "width": 3, "height": 3, "target": [9, 9], "start": [0, 0]}',
    )
    try:
        with pytest.raises(ValueError, match="target"):
            load_fixture_config("_rt_oob_target")
    finally:
        path.unlink(missing_ok=True)


def test_path_traversal_fixture_name_rejected():
    with pytest.raises(ValueError, match="invalid fixture name"):
        load_fixture_config("../seed42")
    with pytest.raises(ValueError, match="invalid fixture name"):
        run_fixture("foo/bar", "greedy_abstain")


def test_empty_object_uses_defaults():
    path = _write("_rt_empty", "{}")
    try:
        cfg = load_fixture_config("_rt_empty")
        assert cfg.seed == 42
        assert cfg.width == 3
        card = run_fixture("_rt_empty", "greedy_abstain")
        assert card["scorecard_hash"]
    finally:
        path.unlink(missing_ok=True)


def test_oob_query_fails_closed_no_index_error():
    env = SparseCityEnv(EpisodeConfig(seed=42))
    env.reset(seed=42)
    _, reward, done, info = env.step(
        {"kind": "QUERY", "query": {"type": "land_use_cell", "y": 99, "x": 99}}
    )
    assert done is False
    assert info["query_ok"] is False
    assert info["query_detail"]["reason"] == "out_of_bounds"
    assert reward < 0
