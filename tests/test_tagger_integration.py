"""Integration tests: tagger round-trip with parser and file I/O."""
import json
from pathlib import Path

import pytest

from envoy.parser import parse_env_file, write_env_file
from envoy.tagger import tag, keys_with_tag, tags_for_key


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / "staging.env"
    p.write_text("DB_HOST=db.internal\nDB_PASS=s3cr3t\nAPP_ENV=staging\n")
    return p


def test_round_trip_tag_and_reparse(env_file: Path):
    env = parse_env_file(str(env_file))
    result = tag(env, add={"DB_PASS": ["sensitive"], "DB_HOST": ["infra"]})
    # Persist env (unchanged) and tags separately
    write_env_file(str(env_file), result.env)
    tags_path = env_file.with_suffix("").with_suffix(".tags.json")
    tags_path.write_text(json.dumps(result.tags, indent=2))

    reloaded_env = parse_env_file(str(env_file))
    reloaded_tags = json.loads(tags_path.read_text())
    re_result = tag(reloaded_env, existing_tags=reloaded_tags)

    assert tags_for_key(re_result, "DB_PASS") == ["sensitive"]
    assert "DB_HOST" in keys_with_tag(re_result, "infra")


def test_tag_does_not_mutate_parsed_env(env_file: Path):
    env = parse_env_file(str(env_file))
    original = dict(env)
    tag(env, add={"DB_PASS": ["pii"]}, remove={"APP_ENV": ["deploy"]})
    assert env == original


def test_tag_preserves_all_keys(env_file: Path):
    env = parse_env_file(str(env_file))
    result = tag(env, add={"DB_HOST": ["internal"]})
    assert set(result.env.keys()) == set(env.keys())
