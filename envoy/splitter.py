"""Split an env dict into multiple target files based on a key prefix or pattern."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional


@dataclass
class SplitResult:
    buckets: Dict[str, Dict[str, str]] = field(default_factory=dict)
    unmatched: Dict[str, str] = field(default_factory=dict)
    total_keys: int = 0


def has_buckets(result: SplitResult) -> bool:
    return bool(result.buckets)


def summary(result: SplitResult) -> str:
    parts = [f"{name}: {len(keys)} key(s)" for name, keys in result.buckets.items()]
    lines = [f"Split into {len(result.buckets)} bucket(s): " + ", ".join(parts)]
    if result.unmatched:
        lines.append(f"Unmatched: {len(result.unmatched)} key(s)")
    return "\n".join(lines)


def split(
    env: Dict[str, str],
    patterns: Dict[str, str],
    strip_prefix: bool = False,
    include_unmatched: Optional[str] = None,
) -> SplitResult:
    """Split *env* into named buckets using glob patterns.

    Args:
        env: Source environment dict.
        patterns: Mapping of bucket_name -> glob pattern (e.g. {"db": "DB_*"}).
        strip_prefix: When True, remove the matched prefix from keys written to buckets.
        include_unmatched: If given, collect unmatched keys into a bucket with this name.

    Returns:
        SplitResult with populated buckets and unmatched keys.
    """
    result = SplitResult(total_keys=len(env))
    assigned: set = set()

    for bucket_name, pattern in patterns.items():
        bucket: Dict[str, str] = {}
        for key, value in env.items():
            if fnmatch(key, pattern):
                out_key = key
                if strip_prefix:
                    prefix = pattern.rstrip("*")
                    if key.startswith(prefix):
                        out_key = key[len(prefix):]
                bucket[out_key] = value
                assigned.add(key)
        result.buckets[bucket_name] = bucket

    for key, value in env.items():
        if key not in assigned:
            result.unmatched[key] = value

    if include_unmatched and result.unmatched:
        result.buckets[include_unmatched] = dict(result.unmatched)

    return result
