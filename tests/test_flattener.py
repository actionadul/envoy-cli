import pytest
from envoy.flattener import (
    FlattenResult,
    flatten,
    expand,
    has_changes,
    summary,
)


# ---------------------------------------------------------------------------
# flatten()
# ---------------------------------------------------------------------------

def test_flatten_clean_env_no_changes():
    env = {"DB_HOST": "localhost", "APP_NAME": "envoy"}
    result = flatten(env)
    assert result.result == env
    assert result.changes == []


def test_flatten_collapses_double_separator():
    env = {"DB__HOST": "localhost"}
    result = flatten(env)
    assert "DB_HOST" in result.result
    assert result.result["DB_HOST"] == "localhost"


def test_flatten_strips_leading_separator():
    env = {"_SECRET": "abc"}
    result = flatten(env)
    assert "SECRET" in result.result
    assert "_SECRET" not in result.result


def test_flatten_strips_trailing_separator():
    env = {"TOKEN_": "xyz"}
    result = flatten(env)
    assert "TOKEN" in result.result


def test_flatten_records_changed_keys():
    env = {"DB__HOST": "localhost", "APP_NAME": "envoy"}
    result = flatten(env)
    assert "DB__HOST" in result.changes
    assert "APP_NAME" not in result.changes


def test_flatten_preserves_original():
    env = {"DB__HOST": "localhost"}
    result = flatten(env)
    assert result.original == env
    assert result.original is not result.result


def test_flatten_custom_separator():
    env = {"DB..HOST": "localhost"}
    result = flatten(env, separator=".")
    assert "DB.HOST" in result.result


# ---------------------------------------------------------------------------
# has_changes() / summary()
# ---------------------------------------------------------------------------

def test_has_changes_true_when_keys_renamed():
    env = {"DB__HOST": "localhost"}
    result = flatten(env)
    assert has_changes(result) is True


def test_has_changes_false_when_clean():
    env = {"DB_HOST": "localhost"}
    result = flatten(env)
    assert has_changes(result) is False


def test_summary_no_changes():
    env = {"DB_HOST": "localhost"}
    result = flatten(env)
    assert "No changes" in summary(result)


def test_summary_with_changes():
    env = {"DB__HOST": "localhost", "__APP": "envoy"}
    result = flatten(env)
    msg = summary(result)
    assert "2 key(s) flattened" in msg


# ---------------------------------------------------------------------------
# expand()
# ---------------------------------------------------------------------------

def test_expand_groups_by_prefix():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    nested = expand(env)
    assert "DB" in nested
    assert nested["DB"]["HOST"] == "localhost"
    assert nested["DB"]["PORT"] == "5432"


def test_expand_multiple_prefixes():
    env = {"DB_HOST": "localhost", "APP_NAME": "envoy"}
    nested = expand(env)
    assert "DB" in nested
    assert "APP" in nested


def test_expand_key_without_separator_stored_as_value():
    env = {"SECRET": "topsecret"}
    nested = expand(env)
    assert nested["SECRET"]["__value__"] == "topsecret"


def test_expand_custom_separator():
    env = {"DB.HOST": "localhost"}
    nested = expand(env, separator=".")
    assert "DB" in nested
    assert nested["DB"]["HOST"] == "localhost"
