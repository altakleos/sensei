"""Plan decay-aware resume for a paused goal (per cross-goal intelligence spec).

Reads a single goal file plus the learner profile, computes freshness for
every completed node using decay.freshness_score, identifies stale topics,
recomputes the curriculum frontier (importing compute_frontier as a library
call), and outputs a JSON resume plan.

Invoked by the engine as:
    python resume_planner.py --goal learner/goals/<slug>.yaml \
                             --profile learner/profile.yaml \
                             --half-life-days <config.memory.half_life_days> \
                             --stale-threshold <config.memory.stale_threshold> \
                             [--now 2026-04-20T00:00:00Z]

Exits 0 and prints a JSON resume plan to stdout.
Exits 1 on invalid input (missing file, bad YAML).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: Missing 'pyyaml'. Install with: pip install sensei-tutor", file=sys.stderr)
    sys.exit(1)

from _iso import parse_iso  # type: ignore[import-not-found]
from decay import freshness_score  # type: ignore[import-not-found]
from frontier import compute_frontier  # type: ignore[import-not-found]

_DEFAULT_HALF_LIFE_DAYS = 7.0
_DEFAULT_STALE_THRESHOLD = 0.5


def plan_resume(
    goal_path: str | Path,
    profile_path: str | Path,
    half_life_days: float = _DEFAULT_HALF_LIFE_DAYS,
    stale_threshold: float = _DEFAULT_STALE_THRESHOLD,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Compute a decay-aware resume plan for a single goal.

    Returns::

        {
            "stale_topics": [{"slug": str, "freshness": float, "elapsed_days": float}, ...],
            "frontier": [slug, ...],
            "recommended_action": "review_first" | "continue",
        }

    ``stale_topics`` is sorted by freshness ascending (most decayed first).
    ``recommended_action`` is ``"review_first"`` when any topic has freshness
    below *stale_threshold*, ``"continue"`` otherwise.
    """
    if now is None:
        now = datetime.now(tz=timezone.utc)

    goal_path = Path(goal_path)
    profile_path = Path(profile_path)

    with goal_path.open("r", encoding="utf-8") as fh:
        goal = yaml.safe_load(fh) or {}
    with profile_path.open("r", encoding="utf-8") as fh:
        profile = yaml.safe_load(fh) or {}

    expertise = profile.get("expertise_map") or {}
    nodes = goal.get("nodes") or {}

    # Compute freshness for completed nodes.
    stale_topics: list[dict[str, Any]] = []
    for topic, node in nodes.items():
        if node.get("state") != "completed":
            continue
        entry = expertise.get(topic)
        if not entry or not entry.get("last_seen"):
            continue
        elapsed = (now - parse_iso(entry["last_seen"])).total_seconds() / 86_400.0
        fresh = freshness_score(elapsed, half_life_days)
        if fresh < stale_threshold:
            stale_topics.append({"slug": topic, "freshness": fresh, "elapsed_days": elapsed})

    stale_topics.sort(key=lambda x: x["freshness"])

    # Recompute frontier from the goal's nodes (library call, not subprocess).
    frontier = compute_frontier(nodes)

    recommended_action = "review_first" if stale_topics else "continue"

    return {
        "stale_topics": stale_topics,
        "frontier": frontier,
        "recommended_action": recommended_action,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--goal", required=True, help="Path to goal YAML file")
    parser.add_argument("--profile", required=True, help="Path to profile.yaml")
    parser.add_argument(
        "--half-life-days",
        type=float,
        default=_DEFAULT_HALF_LIFE_DAYS,
        help=f"Decay half-life in days (default: {_DEFAULT_HALF_LIFE_DAYS})",
    )
    parser.add_argument(
        "--stale-threshold",
        type=float,
        default=_DEFAULT_STALE_THRESHOLD,
        help=f"Freshness below this is stale (default: {_DEFAULT_STALE_THRESHOLD})",
    )
    parser.add_argument("--now", default=None, help="ISO-8601 timestamp (default: wall clock)")
    args = parser.parse_args(argv)

    goal_path = Path(args.goal)
    if not goal_path.is_file():
        print(json.dumps({"error": f"goal file not found: {goal_path}"}))
        return 1

    profile_path = Path(args.profile)
    if not profile_path.is_file():
        print(json.dumps({"error": f"profile file not found: {profile_path}"}))
        return 1

    try:
        now = parse_iso(args.now) if args.now else datetime.now(tz=timezone.utc)
        result = plan_resume(goal_path, profile_path, args.half_life_days, args.stale_threshold, now)
    except yaml.YAMLError as exc:
        print(json.dumps({"error": f"yaml parse error: {exc}"}))
        return 1

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
