"""Allocate session minutes across ranked goals proportional to score.

Takes the ranked goal list from ``goal_priority.py`` (via ``--goals-json``
file or stdin) and a ``--session-minutes`` budget, then distributes minutes
per goal proportional to score.  Goals that would receive fewer than the
minimum allocation (default 5 minutes) are dropped with a note.

Invoked by the engine as:
    python session_allocator.py --goals-json <path> --session-minutes 60

Exits 0 and prints a JSON object to stdout.
Exits 1 on invalid input.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

_DEFAULT_MIN_MINUTES = 5


def allocate_session(
    goals: list[dict[str, Any]],
    session_minutes: int,
    min_minutes: int = _DEFAULT_MIN_MINUTES,
) -> dict[str, Any]:
    """Allocate *session_minutes* across *goals* proportional to score.

    Uses the largest-remainder method (Hamilton's apportionment) so the sum
    of per-goal integer allocations equals *session_minutes* exactly, up to
    the amount lost to goals dropped below *min_minutes*. Without this,
    flooring each share individually can lose up to ``len(candidates) − 1``
    minutes per session.

    Returns ``{"allocations": [...], "dropped": [...]}``.
    """
    # Filter to scoreable goals (skip paused, zero-score, etc.).
    candidates = [g for g in goals if g.get("score", 0) > 0]
    total_score = sum(g["score"] for g in candidates)

    if not candidates or total_score == 0:
        return {"allocations": [], "dropped": []}

    # Step 1 — floor each share and record the fractional residue.
    raw_shares: list[tuple[dict[str, Any], int, float]] = []
    total_floor = 0
    for g in candidates:
        raw = session_minutes * (g["score"] / total_score)
        floor_min = int(math.floor(raw))
        residue = raw - floor_min
        raw_shares.append((g, floor_min, residue))
        total_floor += floor_min

    # Step 2 — distribute remaining minutes to the largest-residue candidates.
    # Python's sort is stable, so ties break by input order.
    residue_minutes = session_minutes - total_floor
    order = sorted(range(len(raw_shares)), key=lambda i: raw_shares[i][2], reverse=True)
    minutes_per: list[int] = [floor_min for (_, floor_min, _) in raw_shares]
    for i in order[:residue_minutes]:
        minutes_per[i] += 1

    # Step 3 — partition into allocations vs dropped (below min).
    allocations: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    for (g, _, _), minutes in zip(raw_shares, minutes_per, strict=True):
        if minutes < min_minutes:
            dropped.append({"slug": g["slug"], "reason": "below minimum"})
        else:
            allocations.append({
                "slug": g["slug"],
                "minutes": minutes,
                "reason": f"score {g['score']} → {minutes} min",
            })

    return {"allocations": allocations, "dropped": dropped}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--goals-json", default=None, help="Path to JSON file with ranked goals (default: stdin)")
    parser.add_argument("--session-minutes", type=int, required=True, help="Total session budget in minutes")
    parser.add_argument(
        "--min-minutes",
        type=int,
        default=_DEFAULT_MIN_MINUTES,
        help=f"Minimum per-goal allocation (default: {_DEFAULT_MIN_MINUTES})",
    )
    args = parser.parse_args(argv)

    try:
        if args.goals_json:
            data = json.loads(Path(args.goals_json).read_text(encoding="utf-8"))
        else:
            data = json.load(sys.stdin)
    except (json.JSONDecodeError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1

    goals = data.get("goals", [])
    result = allocate_session(goals, args.session_minutes, args.min_minutes)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
