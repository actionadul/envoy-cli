"""Tests for envoy.splitter."""

import pytest
from envoy.splitter import split, has_buckets, summary, SplitResult


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "REDIS_URL": "redis://localhost",
    "APP_DEBUG": "true",
    "SECRET_KEY": "abc123",
}


def test_split_assigns_keys_to_matching_bucket():
    result = split(ENV, {"db": "DB_*"})
    assert "DB_HOST" in result.buckets["db"]
    assert "DB_PORT" in result.buckets["db"]


def test_split_unmatched_keys_collected():
    result = split(ENV, {"db": "DB_*"})
    assert "REDIS_URL" in result.unmatched
    assert "APP_DEBUG" in result.unmatched
    assert "SECRET_KEY" in result.unmatched


def test_split_multiple_buckets():
    result = split(ENV, {"db": "DB_*", "redis": "REDIS_*"})
    assert set(result.buckets["db"]) == {"DB_HOST", "DB_PORT"}
    assert set(result.buckets["redis"]) == {"REDIS_URL"}


def test_split_strip_prefix_removes_prefix():
    result = split(ENV, {"db": "DB_*"}, strip_prefix=True)
    assert "HOST" in result.buckets["db"]
    assert "PORT" in result.buckets["db"]
    assert "DB_HOST" not in result.buckets["db"]


def test_split_strip_prefix_preserves_values():
    result = split(ENV, {"db": "DB_*"}, strip_prefix=True)
    assert result.buckets["db"]["HOST"] == "localhost"
    assert result.buckets["db"]["PORT"] == "5432"


def test_split_include_unmatched_creates_bucket():
    result = split(ENV, {"db": "DB_*"}, include_unmatched="rest")
    assert "rest" in result.buckets
    assert "REDIS_URL" in result.buckets["rest"]


def test_split_total_keys_matches_input():
    result = split(ENV, {"db": "DB_*"})
    assert result.total_keys == len(ENV)


def test_has_buckets_true_when_patterns_given():
    result = split(ENV, {"db": "DB_*"})
    assert has_buckets(result) is True


def test_has_buckets_false_when_no_patterns():
    result = split(ENV, {})
    assert has_buckets(result) is False


def test_summary_lists_bucket_counts():
    result = split(ENV, {"db": "DB_*", "redis": "REDIS_*"})
    text = summary(result)
    assert "db" in text
    assert "redis" in text
    assert "2 bucket(s)" in text


def test_summary_mentions_unmatched():
    result = split(ENV, {"db": "DB_*"})
    text = summary(result)
    assert "Unmatched" in text


def test_split_no_match_yields_empty_bucket():
    result = split(ENV, {"svc": "SVC_*"})
    assert result.buckets["svc"] == {}
    assert len(result.unmatched) == len(ENV)
