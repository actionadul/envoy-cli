"""Tests for envoy.templater."""

import pytest

from envoy.templater import TemplateResult, render, summary


# ---------------------------------------------------------------------------
# render()
# ---------------------------------------------------------------------------

def test_render_substitutes_single_placeholder():
    result = render({"URL": "https://{{HOST}}/api"}, {"HOST": "example.com"})
    assert result.rendered["URL"] == "https://example.com/api"


def test_render_substitutes_multiple_placeholders_in_one_value():
    result = render(
        {"DSN": "postgres://{{USER}}:{{PASS}}@{{HOST}}/db"},
        {"USER": "admin", "PASS": "secret", "HOST": "localhost"},
    )
    assert result.rendered["DSN"] == "postgres://admin:secret@localhost/db"


def test_render_counts_substitutions():
    result = render(
        {"A": "{{X}}", "B": "{{X}}-{{Y}}"},
        {"X": "1", "Y": "2"},
    )
    assert result.substitutions == 3


def test_render_leaves_literal_values_unchanged():
    result = render({"KEY": "plain_value"}, {})
    assert result.rendered["KEY"] == "plain_value"
    assert result.substitutions == 0


def test_render_records_missing_placeholders():
    result = render({"URL": "https://{{HOST}}/path"}, {})
    assert "HOST" in result.missing
    assert result.rendered["URL"] == "https://{{HOST}}/path"


def test_render_deduplicates_missing():
    result = render(
        {"A": "{{X}}", "B": "{{X}}"},
        {},
    )
    assert result.missing.count("X") == 1


def test_render_strict_raises_on_missing():
    with pytest.raises(KeyError, match="HOST"):
        render({"URL": "https://{{HOST}}"}, {}, strict=True)


def test_render_strict_succeeds_when_all_resolved():
    result = render({"URL": "https://{{HOST}}"}, {"HOST": "example.com"}, strict=True)
    assert result.rendered["URL"] == "https://example.com"
    assert result.missing == []


def test_render_handles_whitespace_in_placeholder():
    result = render({"K": "{{ VAR }}"}, {"VAR": "hello"})
    assert result.rendered["K"] == "hello"


def test_render_empty_env_returns_empty_rendered():
    result = render({}, {"X": "1"})
    assert result.rendered == {}
    assert result.substitutions == 0


# ---------------------------------------------------------------------------
# summary()
# ---------------------------------------------------------------------------

def test_summary_all_resolved():
    result = render({"A": "{{X}}"}, {"X": "val"})
    out = summary(result)
    assert "All placeholders resolved" in out
    assert "Substitutions made: 1" in out


def test_summary_unresolved_lists_keys():
    result = render({"A": "{{MISSING}}"}, {})
    out = summary(result)
    assert "MISSING" in out
    assert "Unresolved placeholders" in out
