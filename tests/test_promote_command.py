"""Tests for envoy.commands.promote."""

import os
import io
import pytest

from envoy.commands.promote import build_parser, run


@pytest.fixture
def env_dir(tmp_path):
    return str(tmp_path)


def _write_target(env_dir, name, content):
    path = os.path.join(env_dir, f"{name}.env")
    with open(path, "w") as f:
        f.write(content)
    return path


def _make_args(env_dir, source, destination, keys=None, overwrite=False, dry_run=False):
    parser = build_parser()
    argv = [source, destination, "--env-dir", env_dir]
    if keys:
        argv += ["--keys"] + keys
    if overwrite:
        argv.append("--overwrite")
    if dry_run:
        argv.append("--dry-run")
    return parser.parse_args(argv)


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["staging", "production"])
    assert args.source == "staging"
    assert args.destination == "production"
    assert args.keys is None
    assert args.overwrite is False
    assert args.dry_run is False
    assert args.env_dir == "."


def test_run_promotes_and_writes(env_dir):
    _write_target(env_dir, "staging", "NEW_KEY=hello\n")
    _write_target(env_dir, "production", "EXISTING=yes\n")

    args = _make_args(env_dir, "staging", "production", keys=["NEW_KEY"])
    out = io.StringIO()
    code = run(args, stdout=out)

    assert code == 0
    dest = os.path.join(env_dir, "production.env")
    contents = open(dest).read()
    assert "NEW_KEY" in contents


def test_run_dry_run_does_not_write(env_dir):
    _write_target(env_dir, "staging", "DRY=value\n")
    _write_target(env_dir, "production", "")

    args = _make_args(env_dir, "staging", "production", keys=["DRY"], dry_run=True)
    out = io.StringIO()
    code = run(args, stdout=out)

    assert code == 0
    output = out.getvalue()
    assert "Dry run" in output
    dest = os.path.join(env_dir, "production.env")
    assert open(dest).read() == ""


def test_run_prints_summary(env_dir):
    _write_target(env_dir, "staging", "FOO=1\n")
    _write_target(env_dir, "production", "")

    args = _make_args(env_dir, "staging", "production")
    out = io.StringIO()
    run(args, stdout=out)

    output = out.getvalue()
    assert "staging" in output
    assert "production" in output


def test_run_skips_without_overwrite(env_dir):
    _write_target(env_dir, "staging", "FOO=new\n")
    _write_target(env_dir, "production", "FOO=old\n")

    args = _make_args(env_dir, "staging", "production", keys=["FOO"])
    out = io.StringIO()
    run(args, stdout=out)

    dest = os.path.join(env_dir, "production.env")
    contents = open(dest).read()
    assert "old" in contents
