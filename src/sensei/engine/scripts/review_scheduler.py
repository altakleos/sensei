"""Schedule cross-goal review by ranking stale topics across all active goals.

Reads all active/paused goal files in a directory plus the learner profile,
computes freshness for every completed topic using decay.freshness_score,
deduplicates topics that appear in multiple goals (picks lowest freshness),
and outputs a ranked JSON list sorted by freshness ascending (most stale first).

Invoked by the engine as:
    python review_scheduler.py --goals-dir learner/goals \
                               --profile learner/profile.yaml \
                               --half-life-days <config.memory.half_life_days> \
                               --stale-threshold <config.memory.stale_threshold> \
                               [--now 2026-04-20T00:00:00Z]

Exits 0 and prints a JSON list of review candidates to stdout.
Exits 1 on invalid input (missing directory, bad YAML).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from sensei.engine.scripts.decay import freshness_score

_DEFAULT_HALF_LIFE_DAYS = 7.0
_DEFAULT_STALE_THRESHOLD = 0.5


def _parse_iso(raw: str) -> datetime:
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def schedule_reviews(
    goals_dir: str | Path,
    profile_path: str | Path,
    half_life_days: float = _DEFAULT_HALF_LIFE_DAYS,
    stale_threshold: float = _DEFAULT_STALE_THRESHOLD,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    """Return stale review candidates across all active/paused goals.

    Each item: ``{"topic": slug, "freshness": float, "elapsed_days": float,
    "goals": [goal_id, ...]}``.  Sorted by freshness ascending (most stale first).

    Malformed goal YAML files are skipped with a warning printed to stderr —
    a single corrupt goal must not prevent review scheduling across the
    learner's remaining goals.
    """
    if now is None:
        now = datetime.now(tz=timezone.utc)

    goals_dir = Path(goals_dir)
    profile_path = Path(profile_path)

    with profile_path.open("r", encoding="utf-8") as fh:
        profile = yaml.safe_load(fh) or {}
    expertise = profile.get("expertise_map") or {}

    # topic → {freshness, elapsed_days, goals}
    candidates: dict[str, dict[str, Any]] = {}

    for gf in sorted(goals_dir.glob("*.yaml")):
        try:
            with gf.open("r", encoding="utf-8") as fh:
                goal = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            print(
                f"warning: skipping malformed goal file {gf.name}: {exc}",
                file=sys.stderr,
            )
            continue
        if not isinstance(goal, dict):
            continue

        status = goal.get("status", "")
        if status not in ("active", "paused"):
            continue

        goal_id = goal.get("goal_id", gf.stem)
        nodes = goal.get("nodes") or {}

        for topic, node in nodes.items():
            if node.get("state") != "completed":
                continue

            entry = expertise.get(topic)
            if not entry or not entry.get("last_seen"):
                continue

            elapsed = (now - _parse_iso(entry["last_seen"])).total_seconds() / 86_400.0
            fresh = freshness_score(elapsed, half_life_days)

            if fresh >= stale_threshold:
                continue

            if topic in candidates:
                # Dedup: keep lowest freshness.
                candidates[topic]["goals"].append(goal_id)
                if fresh < candidates[topic]["freshness"]:
                    candidates[topic]["freshness"] = fresh
                    candidates[topic]["elapsed_days"] = elapsed
            else:
                candidates[topic] = {
                    "topic": topic,
                    "freshness": fresh,
                    "elapsed_days": elapsed,
                    "goals": [goal_id],
                }

    result = sorted(candidates.values(), key=lambda x: x["freshness"])
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--goals-dir", required=True, help="Directory containing goal YAML files")
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

    goals_dir = Path(args.goals_dir)
    if not goals_dir.is_dir():
        print(json.dumps({"error": f"goals directory not found: {goals_dir}"}))
        return 1

    profile_path = Path(args.profile)
    if not profile_path.is_file():
        print(json.dumps({"error": f"profile file not found: {profile_path}"}))
        return 1

    try:
        now = _parse_iso(args.now) if args.now else datetime.now(tz=timezone.utc)
        result = schedule_reviews(goals_dir, profile_path, args.half_life_days, args.stale_threshold, now)
    except yaml.YAMLError as exc:
        print(json.dumps({"error": f"yaml parse error: {exc}"}))
        return 1

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
