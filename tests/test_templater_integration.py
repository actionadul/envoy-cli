"""Integration tests: templater + parser round-trip."""

from pathlib import Path

import pytest

from envoy.parser import parse_env_file, write_env_file
from envoy.templater import render


@pytest.fixture()
def env_file(tmp_path: Path):
    """Return a helper that writes an env file and returns its path."""

    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p

    return _write


def test_round_trip_render_and_parse(env_file):
    """Rendered output written to disk can be re-parsed correctly."""
    tmpl = env_file(".env.tmpl", "API_URL=https://{{HOST}}/v1\nDEBUG={{DEBUG}}\n")
    ctx = env_file(".env.ctx", "HOST=api.example.com\nDEBUG=false\n")

    template_env = parse_env_file(tmpl)
    context_env = parse_env_file(ctx)
    result = render(template_env, context_env)

    out = env_file(".env.rendered", "")
    write_env_file(out, result.rendered)

    reparsed = parse_env_file(out)
    assert reparsed["API_URL"] == "https://api.example.com/v1"
    assert reparsed["DEBUG"] == "false"


def test_render_does_not_mutate_original(env_file):
    tmpl = env_file(".env.tmpl", "KEY={{PLACEHOLDER}}\n")
    ctx = env_file(".env.ctx", "PLACEHOLDER=replaced\n")

    template_env = parse_env_file(tmpl)
    original_value = template_env["KEY"]

    render(template_env, parse_env_file(ctx))

    assert template_env["KEY"] == original_value


def test_render_preserves_non_template_keys(env_file):
    tmpl = env_file(".env.tmpl", "STATIC=unchanged\nDYNAMIC={{VAR}}\n")
    ctx = env_file(".env.ctx", "VAR=value\n")

    result = render(parse_env_file(tmpl), parse_env_file(ctx))
    assert result.rendered["STATIC"] == "unchanged"
    assert result.rendered["DYNAMIC"] == "value"
