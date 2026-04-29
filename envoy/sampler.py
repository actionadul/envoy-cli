"""Sample a subset of keys from an env dict."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SampleResult:
    sampled: Dict[str, str]
    excluded: Dict[str, str]
    seed: Optional[int]
    requested: int
    changed: List[str] = field(default_factory=list)


def has_changes(result: SampleResult) -> bool:
    return len(result.sampled) < result.requested or len(result.excluded) > 0


def summary(result: SampleResult) -> str:
    total = len(result.sampled) + len(result.excluded)
    seed_info = f", seed={result.seed}" if result.seed is not None else ""
    return (
        f"Sampled {len(result.sampled)} of {total} keys"
        f" (requested {result.requested}{seed_info})"
    )


def sample(
    env: Dict[str, str],
    n: int,
    *,
    seed: Optional[int] = None,
    keys: Optional[List[str]] = None,
) -> SampleResult:
    """Return a random sample of *n* key/value pairs from *env*.

    Parameters
    ----------
    env:  source environment dict.
    n:    number of keys to include in the sample.
    seed: optional RNG seed for reproducibility.
    keys: if provided, restrict sampling to these keys only.
    """
    pool = {k: v for k, v in env.items() if keys is None or k in keys}
    all_keys = list(pool.keys())

    rng = random.Random(seed)
    k = min(n, len(all_keys))
    chosen = set(rng.sample(all_keys, k))

    sampled = {k: v for k, v in pool.items() if k in chosen}
    excluded = {k: v for k, v in env.items() if k not in chosen}

    return SampleResult(
        sampled=sampled,
        excluded=excluded,
        seed=seed,
        requested=n,
        changed=list(chosen),
    )
