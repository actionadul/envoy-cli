"""Integration tests: splitter -> parser round-trip."""

from pathlib import Path

import pytest

from envoy.parser import parse_env_file, write_env_file
from envoy.splitter import split


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / "source.env"
    p.write_text(
        "DB_HOST=db.internal\n"
        "DB_PASS=secret\n"
        "REDIS_URL=redis://localhost\n"
        "APP_NAME=myapp\n"
    )
    return p


def test_round_trip_split_and_parse(env_file: Path, tmp_path: Path):
    env = parse_env_file(env_file)
    result = split(env, {"db": "DB_*", "cache": "REDIS_*"})

    for bucket, bucket_env in result.buckets.items():
        out = tmp_path / f"{bucket}.env"
        write_env_file(out, bucket_env)
        parsed = parse_env_file(out)
        assert parsed == bucket_env


def test_split_does_not_mutate_original(env_file: Path):
    env = parse_env_file(env_file)
    original = dict(env)
    split(env, {"db": "DB_*"}, strip_prefix=True)
    assert env == original


def test_all_keys_accounted_for(env_file: Path):
    env = parse_env_file(env_file)
    result = split(env, {"db": "DB_*", "cache": "REDIS_*"})
    assigned = {k for bucket in result.buckets.values() for k in bucket}
    unmatched = set(result.unmatched)
    assert assigned | unmatched == set(env)
