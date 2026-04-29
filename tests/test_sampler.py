"""Tests for envoy.sampler."""
import pytest
from envoy.sampler import SampleResult, has_changes, sample, summary


ENV = {
    "ALPHA": "1",
    "BETA": "2",
    "GAMMA": "3",
    "DELTA": "4",
    "EPSILON": "5",
}


def test_sample_returns_correct_count():
    result = sample(ENV, 3, seed=0)
    assert len(result.sampled) == 3


def test_sample_excluded_contains_remainder():
    result = sample(ENV, 3, seed=0)
    assert len(result.sampled) + len(result.excluded) == len(ENV)


def test_sample_sampled_and_excluded_are_disjoint():
    result = sample(ENV, 3, seed=0)
    assert set(result.sampled).isdisjoint(set(result.excluded))


def test_sample_reproducible_with_same_seed():
    r1 = sample(ENV, 3, seed=42)
    r2 = sample(ENV, 3, seed=42)
    assert set(r1.sampled.keys()) == set(r2.sampled.keys())


def test_sample_different_seeds_may_differ():
    r1 = sample(ENV, 3, seed=1)
    r2 = sample(ENV, 3, seed=999)
    # Not guaranteed to differ for every seed, but very likely with 5 keys
    # We just assert the structure is valid regardless.
    assert len(r1.sampled) == len(r2.sampled) == 3


def test_sample_n_larger_than_pool_returns_all():
    result = sample(ENV, 100, seed=0)
    assert len(result.sampled) == len(ENV)
    assert result.excluded == {}


def test_sample_n_zero_returns_empty_sampled():
    result = sample(ENV, 0, seed=0)
    assert result.sampled == {}
    assert len(result.excluded) == len(ENV)


def test_sample_keys_filter_restricts_pool():
    result = sample(ENV, 2, seed=0, keys=["ALPHA", "BETA"])
    assert set(result.sampled.keys()).issubset({"ALPHA", "BETA"})


def test_sample_keys_filter_puts_unselected_env_in_excluded():
    result = sample(ENV, 1, seed=0, keys=["ALPHA", "BETA"])
    # GAMMA, DELTA, EPSILON must always be excluded
    for key in ("GAMMA", "DELTA", "EPSILON"):
        assert key in result.excluded


def test_sample_preserves_values():
    result = sample(ENV, 3, seed=7)
    for k, v in result.sampled.items():
        assert ENV[k] == v


def test_sample_requested_stored():
    result = sample(ENV, 3, seed=0)
    assert result.requested == 3


def test_sample_seed_stored():
    result = sample(ENV, 2, seed=99)
    assert result.seed == 99


def test_sample_seed_none_stored():
    result = sample(ENV, 2)
    assert result.seed is None


def test_has_changes_true_when_excluded():
    result = sample(ENV, 3, seed=0)
    assert has_changes(result) is True


def test_has_changes_false_when_all_sampled():
    result = sample(ENV, 100, seed=0)
    assert has_changes(result) is False


def test_summary_contains_sampled_count():
    result = sample(ENV, 3, seed=0)
    s = summary(result)
    assert "3" in s


def test_summary_contains_seed_when_set():
    result = sample(ENV, 2, seed=42)
    assert "seed=42" in summary(result)


def test_summary_no_seed_info_when_none():
    result = sample(ENV, 2)
    assert "seed=" not in summary(result)
