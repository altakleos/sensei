"""Rank goals by priority for session start (per cross-goal intelligence spec).

Reads all YAML goal files in a directory, filters to active/paused goals,
and scores each by priority weight, decay risk, and recency.

Invoked by the engine as:
    python goal_priority.py --goals-dir learner/goals \\
                            --profile learner/profile.yaml \\
                            --half-life-days <config.memory.half_life_days> \\
                            --stale-threshold <config.memory.stale_threshold> \\
                            [--now 2026-04-20T00:00:00Z]

``--half-life-days`` and ``--stale-threshold`` are optional; they default to
the engine's shipped defaults (7.0 and 0.5). Pass them explicitly to honor
instance-level overrides from ``learner/config.yaml``.

Exits 0 and prints a JSON object with a sorted ``goals`` list to stdout.
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

_PRIORITY_WEIGHT: dict[str, int] = {"high": 3, "normal": 2, "low": 1}
_DEFAULT_HALF_LIFE_DAYS = 7.0
_DEFAULT_STALE_THRESHOLD = 0.5
_DEFAULT_DEADLINE_WEIGHT = 5.0


def _parse_iso(raw: str) -> datetime:
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _is_stale(last_seen: str, now: datetime, half_life_days: float, stale_threshold: float) -> bool:
    elapsed = (now - _parse_iso(last_seen)).total_seconds() / 86_400.0
    return bool(2.0 ** (-elapsed / half_life_days) < stale_threshold)


def score_goal(
    goal: dict[str, Any],
    profile: dict[str, Any],
    now: datetime,
    half_life_days: float = _DEFAULT_HALF_LIFE_DAYS,
    stale_threshold: float = _DEFAULT_STALE_THRESHOLD,
    deadline_weight: float = _DEFAULT_DEADLINE_WEIGHT,
) -> dict[str, Any] | None:
    """Score a single goal. Returns None if goal should be skipped.

    Paused goals are included with ``"status": "paused"`` and a score of 0
    so downstream consumers (e.g. session_allocator) can see them.
    Completed and abandoned goals are still excluded.
    """
    status = goal.get("status", "")
    if status not in ("active", "paused"):
        return None

    slug = goal.get("goal_id", "unknown")
    priority = goal.get("priority", "normal")

    # Paused goals appear in output with zero score for visibility.
    if status == "paused":
        return {"slug": slug, "status": "paused", "score": 0, "reason": "paused"}

    pw = _PRIORITY_WEIGHT.get(priority, 2)

    expertise = profile.get("expertise_map") or {}
    nodes = goal.get("nodes") or {}

    # Count stale completed topics (decay risk).
    stale_count = 0
    most_recent: datetime | None = None
    for topic, node in nodes.items():
        if node.get("state") != "completed":
            continue
        entry = expertise.get(topic)
        if entry and entry.get("last_seen"):
            ls = _parse_iso(entry["last_seen"])
            if most_recent is None or ls > most_recent:
                most_recent = ls
            if _is_stale(entry["last_seen"], now, half_life_days, stale_threshold):
                stale_count += 1

    # Recency boost: 0–5 points, more recent = higher.
    recency_boost = 0.0
    if most_recent is not None:
        days_ago = (now - most_recent).total_seconds() / 86_400.0
        recency_boost = max(0.0, 5.0 - days_ago)

    # Deadline urgency: deadline_weight * (1 / max(1, days_until_deadline)).
    deadline_urgency = 0.0
    deadline_raw = goal.get("deadline")
    if deadline_raw:
        days_until = (_parse_iso(deadline_raw) - now).total_seconds() / 86_400.0
        deadline_urgency = deadline_weight * (1.0 / max(1.0, days_until))

    score = pw * 10 + stale_count * 2 + recency_boost + deadline_urgency
    reason_parts = [f"{priority} priority"]
    if stale_count:
        reason_parts.append(f"{stale_count} stale topic{'s' if stale_count != 1 else ''}")
    if deadline_urgency > 0:
        reason_parts.append(f"deadline urgency {deadline_urgency:.1f}")
    return {"slug": slug, "status": status, "score": round(score, 1), "reason": ", ".join(reason_parts)}


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
    parser.add_argument(
        "--deadline-weight",
        type=float,
        default=_DEFAULT_DEADLINE_WEIGHT,
        help=f"Deadline urgency multiplier (default: {_DEFAULT_DEADLINE_WEIGHT})",
    )
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
        with profile_path.open("r", encoding="utf-8") as fh:
            profile = yaml.safe_load(fh) or {}
        goals = []
        for gf in sorted(goals_dir.glob("*.yaml")):
            with gf.open("r", encoding="utf-8") as fh:
                goals.append(yaml.safe_load(fh))
    except yaml.YAMLError as exc:
        print(json.dumps({"error": f"yaml parse error: {exc}"}))
        return 1

    now = _parse_iso(args.now) if args.now else datetime.now(tz=timezone.utc)
    scored = [
        s
        for g in goals
        if (
            s := score_goal(g, profile, now, args.half_life_days, args.stale_threshold, args.deadline_weight)
        ) is not None
    ]
    scored.sort(key=lambda x: float(x["score"]), reverse=True)
    print(json.dumps({"goals": scored}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
