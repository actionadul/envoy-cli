"""envoy CLI commands package.

Registered commands
-------------------
compare  – diff two env targets
export   – export an env target in various formats
list     – list available env targets
merge    – merge two env targets into one
validate – validate an env target against a schema
"""

from envoy.commands import compare, export, list, merge, validate

REGISTRY = {
    "compare": compare,
    "export": export,
    "list": list,
    "merge": merge,
    "validate": validate,
}

__all__ = ["REGISTRY"]
