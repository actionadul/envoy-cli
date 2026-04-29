"""Tests for envoy.composer."""
import pytest
from envoy.composer import compose, has_conflicts, summary


def test_compose_single_env_returns_all_keys():
    result = compose([("base", {"A": "1", "B": "2"})])
    assert result.composed == {"A": "1", "B": "2"}


def test_compose_later_env_wins_on_conflict():
    result = compose([
        ("base", {"A": "old"}),
        ("prod", {"A": "new"}),
    ])
    assert result.composed["A"] == "new"


def test_compose_records_conflict():
    result = compose([
        ("base", {"A": "old"}),
        ("prod", {"A": "new"}),
    ])
    assert len(result.conflicts) == 1
    key, loser, winner = result.conflicts[0]
    assert key == "A"
    assert loser == "base"
    assert winner == "prod"


def test_compose_no_conflict_when_keys_disjoint():
    result = compose([
        ("base", {"A": "1"}),
        ("prod", {"B": "2"}),
    ])
    assert result.composed == {"A": "1", "B": "2"}
    assert result.conflicts == []


def test_compose_sources_track_winning_env():
    result = compose([
        ("base", {"A": "1", "B": "2"}),
        ("prod", {"B": "99"}),
    ])
    assert result.sources["A"] == "base"
    assert result.sources["B"] == "prod"


def test_compose_three_layers_last_wins():
    result = compose([
        ("base", {"X": "1"}),
        ("stage", {"X": "2"}),
        ("prod", {"X": "3"}),
    ])
    assert result.composed["X"] == "3"
    assert len(result.conflicts) == 2


def test_has_conflicts_true():
    result = compose([
        ("a", {"K": "v1"}),
        ("b", {"K": "v2"}),
    ])
    assert has_conflicts(result) is True


def test_has_conflicts_false():
    result = compose([("a", {"K": "v1"})])
    assert has_conflicts(result) is False


def test_summary_no_conflicts():
    result = compose([("base", {"A": "1", "B": "2"})])
    msg = summary(result)
    assert "2 key(s)" in msg
    assert "no conflicts" in msg


def test_summary_with_conflicts():
    result = compose([
        ("base", {"A": "1"}),
        ("prod", {"A": "2"}),
    ])
    msg = summary(result)
    assert "1 conflict" in msg


def test_compose_empty_envs_returns_empty():
    result = compose([])
    assert result.composed == {}
    assert result.conflicts == []
