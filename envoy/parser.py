"""Parser module for reading and writing .env files."""

import os
import re
from typing import Dict, Optional


ENV_LINE_PATTERN = re.compile(
    r'^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$'
)
COMMENT_PATTERN = re.compile(r'^\s*#.*$')


def parse_env_file(filepath: str) -> Dict[str, str]:
    """Parse a .env file and return a dictionary of key-value pairs.

    Args:
        filepath: Path to the .env file.

    Returns:
        A dictionary mapping environment variable names to their values.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If a line cannot be parsed.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Env file not found: {filepath}")

    env_vars: Dict[str, str] = {}

    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.rstrip("\n")

            if not line.strip() or COMMENT_PATTERN.match(line):
                continue

            match = ENV_LINE_PATTERN.match(line)
            if not match:
                raise ValueError(
                    f"Invalid syntax at {filepath}:{lineno} — '{line}'"
                )

            key = match.group("key")
            value = _strip_quotes(match.group("value").strip())
            env_vars[key] = value

    return env_vars


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def write_env_file(filepath: str, env_vars: Dict[str, str], comment: Optional[str] = None) -> None:
    """Write a dictionary of environment variables to a .env file.

    Args:
        filepath: Destination path for the .env file.
        env_vars: Dictionary of environment variable names to values.
        comment: Optional header comment written at the top of the file.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        if comment:
            for line in comment.splitlines():
                f.write(f"# {line}\n")
            f.write("\n")

        for key, value in sorted(env_vars.items()):
            # Quote values that contain spaces or special characters
            if any(c in value for c in (" ", "#", "'", '"')):
                value = f'"{value}"'
            f.write(f"{key}={value}\n")
