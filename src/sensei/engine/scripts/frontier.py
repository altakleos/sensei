"""Compute the activation frontier of a curriculum DAG.

A node is on the frontier when all its prerequisites have state 'skipped'
or 'completed', and the node itself is not 'skipped', 'active', or
'completed'.

Invoked by protocols as:
    python frontier.py --curriculum learner/goals/goal/curriculum.yaml \\
                       [--hints learner/hints/hints.yaml] \\
                       [--boost-weight 1.5] [--max-boost 2.0]

Exits 0 and prints a single JSON object to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: Missing 'pyyaml'. Install with: pip install sensei-tutor", file=sys.stderr)
    sys.exit(1)

from sensei.engine.scripts._states import DONE_STATES, EXCLUDED_STATES


def compute_frontier(
    nodes: dict[str, dict[str, Any]],
    hints: list[dict[str, Any]] | None = None,
    boost_weight: float = 1.5,
    max_boost: float = 2.0,
) -> list[str]:
    """Return frontier slugs sorted by priority (lower priority = higher rank).

    Base priority is the alphabetical index of the node slug. This keeps the
    frontier deterministic regardless of `curriculum.yaml` key order —
    editing the file layout does not silently re-sequence teaching. Hint
    boosting still lowers priority (promotes) exactly as before.
    """
    frontier: list[tuple[float, str]] = []

    for idx, slug in enumerate(sorted(nodes)):
        node = nodes[slug]
        if node.get("state") in EXCLUDED_STATES:
            continue
        prereqs = node.get("prerequisites", [])
        if all(nodes.get(p, {}).get("state") in DONE_STATES for p in prereqs):
            priority = float(idx)
            frontier.append((priority, slug))

    if hints:
        # Build topic → best (relevance * freshness) from active/triaged hints
        topic_boost: dict[str, float] = {}
        for h in hints:
            if h.get("status") not in ("active", "triaged"):
                continue
            relevance = h.get("relevance", 0.0)
            freshness = h.get("freshness", 1.0)
            for topic in h.get("topics", []):
                score = relevance * freshness * boost_weight
                score = min(score, max_boost)
                topic_boost[topic] = max(topic_boost.get(topic, 0.0), score)

        frontier = [
            (pri - topic_boost.get(slug, 0.0), slug) for pri, slug in frontier
        ]

    frontier.sort(key=lambda t: t[0])
    return [slug for _, slug in frontier]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--curriculum", required=True, help="Path to curriculum.yaml")
    parser.add_argument("--hints", default=None, help="Path to hints.yaml for priority boosting")
    parser.add_argument("--boost-weight", type=float, default=1.5, help="Multiplier for hint boost")
    parser.add_argument("--max-boost", type=float, default=2.0, help="Ceiling on hint boost")
    args = parser.parse_args(argv)

    path = Path(args.curriculum)
    if not path.is_file():
        print(json.dumps({"error": f"curriculum file not found: {path}"}), file=sys.stdout)
        return 1

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        print(json.dumps({"error": f"yaml parse error: {exc}"}))
        return 1

    if not isinstance(data, dict) or "nodes" not in data:
        print(json.dumps({"error": "curriculum file must contain a top-level 'nodes' key"}))
        return 1

    nodes = data["nodes"] or {}

    hints_list = None
    if args.hints:
        hints_path = Path(args.hints)
        if not hints_path.is_file():
            print(json.dumps({"error": f"hints file not found: {hints_path}"}))
            return 1
        try:
            with hints_path.open("r", encoding="utf-8") as fh:
                hints_data = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            print(json.dumps({"error": f"hints yaml parse error: {exc}"}))
            return 1
        if isinstance(hints_data, dict):
            hints_list = hints_data.get("hints", [])

    frontier = compute_frontier(nodes, hints_list, args.boost_weight, args.max_boost)

    # Find active node
    active = next((s for s, n in nodes.items() if n.get("state") == "active"), None)
    completed = [s for s, n in nodes.items() if n.get("state") == "completed"]

    print(json.dumps({
        "frontier": frontier,
        "active": active,
        "completed": completed,
        "total_nodes": len(nodes),
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
