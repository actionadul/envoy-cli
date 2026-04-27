"""Tests for envoy.grouper."""
import pytest
from envoy.grouper import GroupResult, group, has_groups, summary


SAMPLE_ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "mydb",
    "AWS_ACCESS_KEY": "AKIA",
    "AWS_SECRET_KEY": "secret",
    "APP_ENV": "production",
    "DEBUG": "false",
}


def test_group_auto_detects_prefixes():
    result = group(SAMPLE_ENV)
    assert "DB" in result.groups
    assert "AWS" in result.groups


def test_group_auto_excludes_single_key_prefix():
    # APP_ only has one key, so it should not form a group
    result = group(SAMPLE_ENV)
    assert "APP" not in result.groups


def test_group_ungrouped_contains_remainder():
    result = group(SAMPLE_ENV)
    assert "DEBUG" in result.ungrouped
    assert "APP_ENV" in result.ungrouped


def test_group_explicit_prefixes():
    result = group(SAMPLE_ENV, prefixes=["DB", "APP"])
    assert "DB" in result.groups
    assert "APP" in result.groups
    assert "AWS" not in result.groups


def test_group_explicit_prefix_single_key_still_grouped():
    result = group(SAMPLE_ENV, prefixes=["APP"])
    assert "APP" in result.groups
    assert result.groups["APP"] == {"APP_ENV": "production"}


def test_group_total_keys_matches_env():
    result = group(SAMPLE_ENV)
    assert result.total_keys == len(SAMPLE_ENV)


def test_group_members_correct():
    result = group(SAMPLE_ENV)
    assert result.groups["DB"] == {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
    }


def test_has_groups_true():
    result = group(SAMPLE_ENV)
    assert has_groups(result) is True


def test_has_groups_false():
    result = group({"SOLO": "value"})
    assert has_groups(result) is False


def test_summary_contains_group_count():
    result = group(SAMPLE_ENV)
    text = summary(result)
    assert "group(s)" in text


def test_summary_lists_group_names():
    result = group(SAMPLE_ENV)
    text = summary(result)
    assert "[DB]" in text
    assert "[AWS]" in text


def test_summary_mentions_ungrouped():
    result = group(SAMPLE_ENV)
    text = summary(result)
    assert "ungrouped" in text


def test_group_empty_env():
    result = group({})
    assert result.groups == {}
    assert result.ungrouped == {}
    assert result.total_keys == 0


def test_group_custom_separator():
    env = {"DB.HOST": "localhost", "DB.PORT": "5432", "OTHER": "x"}
    result = group(env, separator=".")
    assert "DB" in result.groups
