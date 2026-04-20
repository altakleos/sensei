"""Validator for instance/goals/<slug>.yaml (per docs/design/curriculum-graph.md).

Runs JSON Schema validation followed by cross-field invariants:
  1. At most one node has state 'active'
  2. All prerequisite references point to existing nodes
  3. No cycles in the prerequisite DAG (topological sort)

Exits:
    0 — goal is valid
    1 — parse failure, schema violation, or cross-field invariant violation

Always prints a single JSON line to stdout summarizing what was checked and
what failed, so protocols can surface the failure to the learner without
parsing stderr.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "goal.schema.json"


def _load_schema() -> dict[str, Any]:
    with _SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        schema: dict[str, Any] = json.load(fh)
    return schema


def _check_cross_field(goal: dict[str, Any]) -> list[str]:
    """Return a list of cross-field invariant violations (empty if valid)."""
    violations: list[str] = []
    nodes: dict[str, Any] = goal.get("nodes", {}) or {}

    # (a) At most one node active
    active_nodes = [slug for slug, node in nodes.items() if node.get("state") == "active"]
    if len(active_nodes) > 1:
        violations.append(
            f"multiple active nodes: {active_nodes!r} (at most one allowed)"
        )

    # (b) All prerequisite references point to existing nodes
    for slug, node in nodes.items():
        for prereq in node.get("prerequisites", []):
            if prereq not in nodes:
                violations.append(
                    f"node {slug!r}: prerequisite {prereq!r} does not exist"
                )

    # (c) No cycles — Kahn's algorithm (topological sort)
    in_degree: dict[str, int] = {slug: 0 for slug in nodes}
    for slug, node in nodes.items():
        for prereq in node.get("prerequisites", []):
            if prereq in in_degree:
                in_degree[slug] += 1

    queue: deque[str] = deque(slug for slug, deg in in_degree.items() if deg == 0)
    visited = 0
    while queue:
        current = queue.popleft()
        visited += 1
        # Find nodes that depend on current (current is in their prerequisites)
        for slug, node in nodes.items():
            if current in node.get("prerequisites", []):
                in_degree[slug] -= 1
                if in_degree[slug] == 0:
                    queue.append(slug)

    if visited < len(nodes):
        cycle_nodes = [slug for slug, deg in in_degree.items() if deg > 0]
        violations.append(f"cycle detected involving nodes: {cycle_nodes!r}")

    return violations


def validate_goal(goal: dict[str, Any]) -> tuple[str, list[str]]:
    """Validate a parsed goal dict.

    Returns a tuple (status, errors) where status is one of:
        "ok"           — goal is valid
        "schema"       — schema violations
        "cross_field"  — schema passes but cross-field invariants fail

    `errors` lists human-readable error messages.
    """
    schema = _load_schema()
    validator = Draft202012Validator(schema)
    schema_errors = sorted(validator.iter_errors(goal), key=lambda e: list(e.absolute_path))
    if schema_errors:
        return "schema", [f"{list(e.absolute_path) or '<root>'}: {e.message}" for e in schema_errors]
    cross = _check_cross_field(goal)
    if cross:
        return "cross_field", cross
    return "ok", []


def _emit(status: str, errors: list[str], path: str) -> None:
    print(json.dumps({"path": path, "status": status, "errors": errors}))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--goal", required=True, help="Path to goal YAML file")
    args = parser.parse_args(argv)

    path = Path(args.goal)
    if not path.is_file():
        _emit("schema", [f"goal file not found: {path}"], str(path))
        return 1

    try:
        with path.open("r", encoding="utf-8") as fh:
            goal = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        _emit("schema", [f"yaml parse error: {exc}"], str(path))
        return 1

    if not isinstance(goal, dict):
        _emit("schema", ["top-level yaml must be a mapping"], str(path))
        return 1

    status, errors = validate_goal(goal)
    _emit(status, errors, str(path))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
