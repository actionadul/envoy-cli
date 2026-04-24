"""Tests for envoy.commands.export."""

import argparse
from io import StringIO
from pathlib import Path

import pytest

from envoy.commands.export import build_parser, run


@pytest.fixture()
def env_dir(tmp_path):
    """Create a minimal env directory with a base and a staging target."""
    d = tmp_path / "envs"
    d.mkdir()
    (d / ".env.base").write_text("APP=myapp\nDEBUG=false\n")
    (d / ".env.staging").write_text("DEBUG=true\nSECRET=s3cr3t\n")
    return d


def _make_args(target, env_dir, output=None, fmt="env"):
    return argparse.Namespace(
        target=target,
        env_dir=str(env_dir),
        output=output,
        fmt=fmt,
    )


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------

def test_build_parser_returns_parser():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["staging"])
    assert args.target == "staging"
    assert args.env_dir == "envs"
    assert args.output is None
    assert args.fmt == "env"


# ---------------------------------------------------------------------------
# run — stdout output
# ---------------------------------------------------------------------------

def test_run_prints_env_format(env_dir):
    stdout, stderr = StringIO(), StringIO()
    args = _make_args("staging", env_dir)
    code = run(args, stdout=stdout, stderr=stderr)
    assert code == 0
    output = stdout.getvalue()
    assert 'DEBUG="true"' in output
    assert 'SECRET="s3cr3t"' in output


def test_run_prints_export_format(env_dir):
    stdout, stderr = StringIO(), StringIO()
    args = _make_args("staging", env_dir, fmt="export")
    code = run(args, stdout=stdout, stderr=stderr)
    assert code == 0
    output = stdout.getvalue()
    assert 'export DEBUG="true"' in output
    assert 'export SECRET="s3cr3t"' in output


def test_run_output_is_sorted(env_dir):
    stdout, stderr = StringIO(), StringIO()
    args = _make_args("staging", env_dir)
    run(args, stdout=stdout, stderr=stderr)
    lines = stdout.getvalue().splitlines()
    keys = [line.split("=")[0] for line in lines if "=" in line]
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# run — file output
# ---------------------------------------------------------------------------

def test_run_writes_file(env_dir, tmp_path):
    out_file = tmp_path / "out.env"
    stdout, stderr = StringIO(), StringIO()
    args = _make_args("staging", env_dir, output=str(out_file))
    code = run(args, stdout=stdout, stderr=stderr)
    assert code == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "DEBUG" in content


# ---------------------------------------------------------------------------
# run — error handling
# ---------------------------------------------------------------------------

def test_run_missing_target_returns_error(env_dir):
    stdout, stderr = StringIO(), StringIO()
    args = _make_args("production", env_dir)
    code = run(args, stdout=stdout, stderr=stderr)
    assert code == 1
    assert "error" in stderr.getvalue().lower()
