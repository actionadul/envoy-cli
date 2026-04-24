"""Tests for envoy.commands.merge."""

import argparse
import io
from pathlib import Path

import pytest

from envoy.commands.merge import build_parser, run


@pytest.fixture()
def env_dir(tmp_path):
    d = tmp_path / "envs"
    d.mkdir()
    return d


def _write_target(env_dir, name, content):
    (env_dir / f"{name}.env").write_text(content)


def _make_args(base, overlay, env_dir, output=None, no_overwrite=False):
    return argparse.Namespace(
        base=base,
        overlay=overlay,
        env_dir=str(env_dir),
        output=output,
        no_overwrite=no_overwrite,
    )


def test_build_parser_returns_parser():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["base", "overlay"])
    assert args.base == "base"
    assert args.overlay == "overlay"
    assert args.env_dir == "envs"
    assert args.output is None
    assert args.no_overwrite is False


def test_run_merges_to_stdout(env_dir):
    _write_target(env_dir, "base", "FOO=base_foo\nBAR=base_bar\n")
    _write_target(env_dir, "overlay", "BAR=overlay_bar\nBAZ=overlay_baz\n")

    out = io.StringIO()
    code = run(_make_args("base", "overlay", env_dir), stdout=out)

    assert code == 0
    output = out.getvalue()
    assert "FOO=base_foo" in output
    assert "BAR=overlay_bar" in output
    assert "BAZ=overlay_baz" in output


def test_run_overlay_overrides_base(env_dir):
    _write_target(env_dir, "base", "KEY=from_base\n")
    _write_target(env_dir, "overlay", "KEY=from_overlay\n")

    out = io.StringIO()
    run(_make_args("base", "overlay", env_dir), stdout=out)

    assert "KEY=from_overlay" in out.getvalue()
    assert "KEY=from_base" not in out.getvalue()


def test_run_writes_output_file(env_dir, tmp_path):
    _write_target(env_dir, "base", "A=1\n")
    _write_target(env_dir, "overlay", "B=2\n")
    output_file = tmp_path / "merged.env"

    out = io.StringIO()
    code = run(_make_args("base", "overlay", env_dir, output=str(output_file)), stdout=out)

    assert code == 0
    assert output_file.exists()
    content = output_file.read_text()
    assert "A=1" in content
    assert "B=2" in content


def test_run_no_overwrite_blocks_existing_file(env_dir, tmp_path):
    _write_target(env_dir, "base", "A=1\n")
    _write_target(env_dir, "overlay", "B=2\n")
    output_file = tmp_path / "merged.env"
    output_file.write_text("existing content\n")

    err = io.StringIO()
    code = run(
        _make_args("base", "overlay", env_dir, output=str(output_file), no_overwrite=True),
        stderr=err,
    )

    assert code == 1
    assert "already exists" in err.getvalue()
    assert output_file.read_text() == "existing content\n"


def test_run_missing_base_returns_error(env_dir):
    _write_target(env_dir, "overlay", "B=2\n")
    err = io.StringIO()
    code = run(_make_args("missing", "overlay", env_dir), stderr=err)
    assert code == 1
    assert "base target" in err.getvalue()


def test_run_missing_overlay_returns_error(env_dir):
    _write_target(env_dir, "base", "A=1\n")
    err = io.StringIO()
    code = run(_make_args("base", "missing", env_dir), stderr=err)
    assert code == 1
    assert "overlay target" in err.getvalue()
