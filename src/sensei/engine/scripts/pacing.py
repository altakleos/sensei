"""Velocity and pacing arithmetic (per pacing-velocity plan).

Computes a weighted-average completion velocity from a goal's curriculum
graph, projects a completion date, and compares against the deadline to
produce a pace status (ahead / on_track / behind).

Invoked by protocols as:
    python pacing.py --curriculum goals/rust/curriculum.yaml \\
                     --profile learner/profile.yaml \\
                     --now 2026-06-01T00:00:00Z

Exits 0 and prints a single JSON object to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _iso import parse_iso  # type: ignore[import-not-found]
from decay import freshness_score  # type: ignore[import-not-found]

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


def compute_pacing(
    nodes: dict[str, dict[str, Any]],
    deadline: str | None,
    created: str,
    profile_map: dict[str, dict[str, Any]] | None,
    now: datetime,
    recency_decay: float = 0.7,
    review_overhead_cap: float = 0.3,
    half_life_days: float = 7.0,
    stale_threshold: float = 0.5,
) -> dict[str, Any]:
    """Pure function: compute velocity, projection, and pace status.

    *nodes* is the ``nodes`` dict from a goal curriculum YAML — each value
    has at least ``state`` and optionally ``completed_at`` (ISO-8601).
    *profile_map* is the ``expertise_map`` dict from the learner profile
    (may be ``None``).
    """
    total = len(nodes)

    # 1. Collect completed timestamps, sorted ascending.
    completed: list[datetime] = []
    for v in nodes.values():
        ts = v.get("completed_at") if isinstance(v, dict) else None
        if ts:
            completed.append(parse_iso(ts))
    completed.sort()

    completed_count = len(completed)
    remaining = total - completed_count

    # 2. Early exit: nothing completed yet.
    if completed_count == 0:
        return _result(completed_count, remaining, None, None, deadline, None, None)

    # 3. Compute velocity.
    created_dt = parse_iso(created)
    if completed_count == 1:
        interval_days = max((completed[0] - created_dt).total_seconds() / 86_400, 0.001)
        velocity = 1.0 / interval_days
    else:
        # Inter-completion intervals, weighted by recency.
        intervals: list[float] = []
        for i in range(1, len(completed)):
            intervals.append(max((completed[i] - completed[i - 1]).total_seconds() / 86_400, 0.001))
        # Newest interval is last in list → weight 1.0; older → decay^distance.
        total_weight = 0.0
        weighted_sum = 0.0
        for idx, iv in enumerate(intervals):
            distance_from_newest = len(intervals) - 1 - idx
            w = recency_decay ** distance_from_newest
            weighted_sum += iv * w
            total_weight += w
        avg_interval = weighted_sum / total_weight
        velocity = 1.0 / avg_interval

    # 4. Review overhead adjustment.
    review_fraction = 0.0
    if profile_map and completed_count > 0:
        stale_count = 0
        for _key, entry in profile_map.items():
            stability = entry.get("stability") if isinstance(entry, dict) else None
            if stability is None:
                continue
            # Use last completed timestamp as proxy for last_seen.
            elapsed = max((now - completed[-1]).total_seconds() / 86_400, 0.0)
            score = freshness_score(elapsed, stability if stability > 0 else half_life_days)
            if score < stale_threshold:
                stale_count += 1
        review_fraction = min(stale_count / max(completed_count, 1), review_overhead_cap)

    effective_velocity = velocity * (1.0 - review_fraction)

    # 5. Projection.
    if remaining == 0:
        projected = now
    else:
        projected_days = remaining / effective_velocity
        projected = now + timedelta(days=projected_days)

    # 6. Pace status vs deadline.
    pace_status = None
    days_delta = None
    if deadline:
        deadline_dt = parse_iso(deadline)
        days_delta = int((deadline_dt - projected).total_seconds() / 86_400)
        if days_delta > 1:
            pace_status = "ahead"
        elif days_delta < -1:
            pace_status = "behind"
        else:
            pace_status = "on_track"

    return _result(
        completed_count, remaining,
        round(effective_velocity, 2),
        projected.strftime("%Y-%m-%dT%H:%M:%SZ"),
        deadline, pace_status, days_delta,
    )


def _result(
    completed_count: int,
    remaining_count: int,
    velocity: float | None,
    projected: str | None,
    deadline: str | None,
    pace_status: str | None,
    days_delta: int | None,
) -> dict[str, Any]:
    return {
        "completed_count": completed_count,
        "remaining_count": remaining_count,
        "velocity_topics_per_day": velocity,
        "projected_completion": projected,
        "deadline": deadline,
        "pace_status": pace_status,
        "days_delta": days_delta,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--curriculum", required=True, help="Path to goal curriculum YAML")
    parser.add_argument("--profile", default=None, help="Path to learner profile YAML")
    parser.add_argument("--now", default=None, help="ISO-8601 timestamp (default: wall clock)")
    parser.add_argument("--half-life-days", type=float, default=7.0, help="Half-life for stale computation")
    parser.add_argument("--stale-threshold", type=float, default=0.5, help="Freshness below this is stale")
    parser.add_argument("--recency-decay", type=float, default=0.7, help="Weight decay for velocity")
    parser.add_argument("--review-overhead-cap", type=float, default=0.3, help="Max review fraction")
    args = parser.parse_args(argv)

    if yaml is None:
        print("pacing.py requires PyYAML (`pip install pyyaml`)", file=sys.stderr)
        return 1

    with open(args.curriculum) as f:
        cur = yaml.safe_load(f) or {}

    nodes = cur.get("nodes", {})
    deadline = cur.get("deadline")
    created = cur.get("created")
    if not created:
        print("curriculum YAML must contain a 'created' field", file=sys.stderr)
        return 1

    profile_map = None
    if args.profile:
        with open(args.profile) as f:
            prof = yaml.safe_load(f) or {}
        profile_map = prof.get("expertise_map", {})

    now = parse_iso(args.now) if args.now else datetime.now(tz=timezone.utc)

    result = compute_pacing(
        nodes, deadline, created, profile_map, now,
        recency_decay=args.recency_decay,
        review_overhead_cap=args.review_overhead_cap,
        half_life_days=args.half_life_days,
        stale_threshold=args.stale_threshold,
    )
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
