"""Validated state transitions on the curriculum DAG.

Performs activate, complete, collapse, spawn, and expand operations with
cycle detection (Kahn's algorithm) after every mutation.

Invoked by protocols as:
    python mutate_graph.py --curriculum <path> --operation <op> --node <slug> \\
                           [--prerequisites <comma-separated>] [--subgraph <json>]

Exits:
    0 — mutation applied successfully
    1 — input error (missing file, invalid args, precondition failure)
    2 — invariant violation (cycle detected after mutation)
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any

import yaml

from sensei.engine.scripts._atomic import atomic_write_text

_DONE_STATES = frozenset({"collapsed", "completed"})
_EXCLUDED_STATES = frozenset({"collapsed", "active", "completed", "expanded"})


def _is_on_frontier(slug: str, nodes: dict[str, dict[str, Any]]) -> bool:
    """Check if a node is on the activation frontier."""
    node = nodes.get(slug)
    if not node or node.get("state") in _EXCLUDED_STATES:
        return False
    prereqs = node.get("prerequisites", [])
    return all(nodes.get(p, {}).get("state") in _DONE_STATES for p in prereqs)


def _has_cycle(nodes: dict[str, dict[str, Any]]) -> bool:
    """Kahn's algorithm — returns True if a cycle exists. O(N + E)."""
    in_degree: dict[str, int] = {s: 0 for s in nodes}
    # Reverse adjacency: prereq → nodes that depend on it. Built once so the
    # BFS inner loop walks only actual dependents instead of re-scanning every
    # node's prerequisites on each dequeue.
    dependents: dict[str, list[str]] = {s: [] for s in nodes}
    for slug, node in nodes.items():
        for prereq in node.get("prerequisites", []):
            if prereq in in_degree:
                in_degree[slug] += 1
                dependents[prereq].append(slug)

    queue: deque[str] = deque(s for s, d in in_degree.items() if d == 0)
    visited = 0
    while queue:
        current = queue.popleft()
        visited += 1
        for dep in dependents[current]:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    return visited < len(nodes)


def _frontier_list(nodes: dict[str, dict[str, Any]]) -> list[str]:
    """Compute current frontier slugs."""
    return [s for s in nodes if _is_on_frontier(s, nodes)]


def _fail(op: str, slug: str, msg: str, code: int = 1) -> int:
    print(json.dumps({"operation": op, "node": slug, "valid": False, "error": msg}))
    return code


def _success(op: str, slug: str, state: str, nodes: dict[str, dict[str, Any]]) -> int:
    print(json.dumps({
        "operation": op,
        "node": slug,
        "new_state": state,
        "valid": True,
        "frontier": _frontier_list(nodes),
    }))
    return 0


def mutate(
    nodes: dict[str, dict[str, Any]], op: str, slug: str,
    prerequisites: list[str] | None, subgraph: dict[str, Any] | None,
) -> tuple[int, str]:
    """Apply mutation. Returns (exit_code, new_state_or_empty)."""
    if op == "activate":
        if slug not in nodes:
            return 1, ""
        active = [s for s, n in nodes.items() if n.get("state") == "active"]
        if active:
            return 1, ""
        if not _is_on_frontier(slug, nodes):
            return 1, ""
        nodes[slug]["state"] = "active"
        return 0, "active"

    elif op == "complete":
        if slug not in nodes or nodes[slug].get("state") != "active":
            return 1, ""
        nodes[slug]["state"] = "completed"
        return 0, "completed"

    elif op == "collapse":
        if slug not in nodes:
            return 1, ""
        nodes[slug]["state"] = "collapsed"
        return 0, "collapsed"

    elif op == "spawn":
        if slug in nodes:
            return 1, ""
        if not prerequisites:
            return 1, ""
        for p in prerequisites:
            if p not in nodes:
                return 1, ""
        nodes[slug] = {"state": "spawned", "prerequisites": prerequisites}
        return 0, "spawned"

    elif op == "expand":
        if slug not in nodes:
            return 1, ""
        if not subgraph or "nodes" not in subgraph:
            return 1, ""
        # Find dependents of original node (nodes that list slug as prerequisite)
        dependents = [s for s, n in nodes.items() if slug in n.get("prerequisites", [])]
        # Find leaf nodes in subgraph (not a prerequisite of any other subgraph node)
        sub_nodes = subgraph["nodes"]
        all_prereqs_in_sub = set()
        for sn in sub_nodes.values():
            all_prereqs_in_sub.update(sn.get("prerequisites", []))
        leaves = [s for s in sub_nodes if s not in all_prereqs_in_sub]

        # Mark original as expanded
        nodes[slug]["state"] = "expanded"
        # Add subgraph nodes
        for sub_slug, sub_data in sub_nodes.items():
            nodes[sub_slug] = {"state": "spawned", "prerequisites": sub_data.get("prerequisites", [])}
        # Dependents now depend on leaves instead of original
        for dep in dependents:
            prereqs = nodes[dep].get("prerequisites", [])
            prereqs = [p for p in prereqs if p != slug] + leaves
            nodes[dep]["prerequisites"] = prereqs

        return 0, "expanded"

    return 1, ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--curriculum", required=True, help="Path to curriculum.yaml")
    parser.add_argument("--operation", required=True, choices=["activate", "complete", "collapse", "spawn", "expand"])
    parser.add_argument("--node", required=True, help="Target node slug")
    parser.add_argument("--prerequisites", default=None, help="Comma-separated prerequisite slugs (for spawn)")
    parser.add_argument("--subgraph", default=None, help="JSON subgraph string (for expand)")
    args = parser.parse_args(argv)

    path = Path(args.curriculum)
    if not path.is_file():
        return _fail(args.operation, args.node, f"curriculum file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        return _fail(args.operation, args.node, f"yaml parse error: {exc}")

    if not isinstance(data, dict) or "nodes" not in data:
        return _fail(args.operation, args.node, "curriculum file must contain a top-level 'nodes' key")

    nodes = data["nodes"] or {}
    original = copy.deepcopy(nodes)

    prerequisites = args.prerequisites.split(",") if args.prerequisites else None
    subgraph = None
    if args.subgraph:
        try:
            subgraph = json.loads(args.subgraph)
        except json.JSONDecodeError as exc:
            return _fail(args.operation, args.node, f"invalid subgraph JSON: {exc}")

    code, new_state = mutate(nodes, args.operation, args.node, prerequisites, subgraph)
    if code != 0:
        # Determine error message
        if args.operation == "activate":
            active = [s for s, n in original.items() if n.get("state") == "active"]
            if active:
                msg = f"another node is already active: {active[0]}"
            elif args.node not in original:
                msg = f"node '{args.node}' does not exist"
            else:
                msg = f"node '{args.node}' is not on the frontier"
        elif args.operation == "complete":
            msg = f"node '{args.node}' is not active"
        elif args.operation == "collapse":
            msg = f"node '{args.node}' does not exist"
        elif args.operation == "spawn":
            if args.node in original:
                msg = f"node '{args.node}' already exists"
            elif not prerequisites:
                msg = "prerequisites required for spawn"
            else:
                missing = [p for p in prerequisites if p not in original]
                msg = f"prerequisite(s) not found: {missing}"
        elif args.operation == "expand":
            msg = f"node '{args.node}' does not exist" if args.node not in original else "subgraph required for expand"
        else:
            msg = "unknown error"
        return _fail(args.operation, args.node, msg)

    # Cycle detection after mutation
    if _has_cycle(nodes):
        return _fail(args.operation, args.node, "cycle detected after mutation", code=2)

    # Write back
    data["nodes"] = nodes
    atomic_write_text(path, yaml.safe_dump(data, default_flow_style=False, sort_keys=False))

    return _success(args.operation, args.node, new_state, nodes)


if __name__ == "__main__":
    sys.exit(main())
