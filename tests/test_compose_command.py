"""Tests for envoy.commands.compose."""
import argparse
import pytest
from pathlib import Path
from envoy.commands.compose import build_parser, run
from envoy.parser import write_env_file


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    d = tmp_path / "envs"
    d.mkdir()
    return d


def _write_target(env_dir: Path, name: str, env: dict) -> None:
    write_env_file(str(env_dir / f"{name}.env"), env)


def _make_args(env_dir, targets, output=None, strict=False):
    parser = build_parser()
    argv = [*targets, "--env-dir", str(env_dir)]
    if output:
        argv += ["--output", output]
    if strict:
        argv.append("--strict")
    return parser.parse_args(argv)


def test_build_parser_returns_parser():
    assert isinstance(build_parser(), argparse.ArgumentParser)


def test_build_parser_defaults():
    p = build_parser()
    args = p.parse_args(["base"])
    assert args.env_dir == "envs"
    assert args.output is None
    assert args.strict is False


def test_run_merges_two_targets(env_dir, capsys):
    _write_target(env_dir, "base", {"A": "1", "B": "2"})
    _write_target(env_dir, "prod", {"B": "99", "C": "3"})
    args = _make_args(env_dir, ["base", "prod"])
    rc = run(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "A=1" in out
    assert "B=99" in out
    assert "C=3" in out


def test_run_exit_code_0_without_strict_even_with_conflict(env_dir, capsys):
    _write_target(env_dir, "base", {"X": "old"})
    _write_target(env_dir, "prod", {"X": "new"})
    args = _make_args(env_dir, ["base", "prod"])
    assert run(args) == 0


def test_run_strict_exits_1_on_conflict(env_dir, capsys):
    _write_target(env_dir, "base", {"X": "old"})
    _write_target(env_dir, "prod", {"X": "new"})
    args = _make_args(env_dir, ["base", "prod"], strict=True)
    assert run(args) == 1


def test_run_strict_exits_0_no_conflict(env_dir, capsys):
    _write_target(env_dir, "base", {"A": "1"})
    _write_target(env_dir, "prod", {"B": "2"})
    args = _make_args(env_dir, ["base", "prod"], strict=True)
    assert run(args) == 0


def test_run_writes_output_file(env_dir, tmp_path, capsys):
    _write_target(env_dir, "base", {"A": "1"})
    out_file = str(tmp_path / "out.env")
    args = _make_args(env_dir, ["base"], output=out_file)
    rc = run(args)
    assert rc == 0
    content = Path(out_file).read_text()
    assert "A=1" in content


def test_run_returns_1_for_missing_target(env_dir, capsys):
    args = _make_args(env_dir, ["nonexistent"])
    assert run(args) == 1
