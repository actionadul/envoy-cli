"""Tests for envoy.commands.template."""

import argparse
from pathlib import Path

import pytest

from envoy.commands.template import build_parser, run


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    d = tmp_path / "envs"
    d.mkdir()
    return d


def _write_env(env_dir: Path, name: str, content: str) -> None:
    (env_dir / f".env.{name}").write_text(content)


def _make_args(env_dir: Path, target: str, context: str, **kwargs) -> argparse.Namespace:
    defaults = {
        "env_dir": str(env_dir),
        "output": None,
        "strict": False,
        "quiet": True,
    }
    defaults.update(kwargs)
    return argparse.Namespace(target=target, context=context, **defaults)


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------

def test_build_parser_returns_parser():
    p = build_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_build_parser_defaults():
    p = build_parser()
    args = p.parse_args(["staging", "production"])
    assert args.env_dir == "envs"
    assert args.strict is False
    assert args.quiet is False
    assert args.output is None


# ---------------------------------------------------------------------------
# run()
# ---------------------------------------------------------------------------

def test_run_renders_placeholders(env_dir: Path, capsys):
    _write_env(env_dir, "staging", "URL=https://{{HOST}}/api\nDEBUG=true\n")
    _write_env(env_dir, "context", "HOST=staging.example.com\n")
    args = _make_args(env_dir, "staging", "context")
    code = run(args)
    assert code == 0
    out = capsys.readouterr().out
    assert "URL=https://staging.example.com/api" in out
    assert "DEBUG=true" in out


def test_run_missing_target_returns_1(env_dir: Path):
    _write_env(env_dir, "context", "HOST=x\n")
    args = _make_args(env_dir, "nonexistent", "context")
    assert run(args) == 1


def test_run_missing_context_returns_1(env_dir: Path):
    _write_env(env_dir, "staging", "URL={{HOST}}\n")
    args = _make_args(env_dir, "staging", "nonexistent")
    assert run(args) == 1


def test_run_strict_returns_1_on_unresolved(env_dir: Path):
    _write_env(env_dir, "staging", "URL={{MISSING}}\n")
    _write_env(env_dir, "context", "OTHER=val\n")
    args = _make_args(env_dir, "staging", "context", strict=True)
    assert run(args) == 1


def test_run_writes_output_file(env_dir: Path, tmp_path: Path):
    _write_env(env_dir, "staging", "KEY={{VAL}}\n")
    _write_env(env_dir, "ctx", "VAL=hello\n")
    out_file = tmp_path / "rendered.env"
    args = _make_args(env_dir, "staging", "ctx", output=str(out_file))
    code = run(args)
    assert code == 0
    assert out_file.exists()
    assert "KEY=hello" in out_file.read_text()
