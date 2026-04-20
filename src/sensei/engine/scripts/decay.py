"""Forgetting-curve freshness arithmetic (per PRODUCT-IDEATION.md §8.1).

Computes a retention score in [0, 1] from an exponential decay model:

    freshness = 2 ** (-elapsed_days / half_life_days)

where `elapsed_days` is the age of the last review and `half_life_days` is
the per-item stability parameter. A freshness of 0.5 means the item is at
the half-life; below the configured threshold the item is "stale" and due
for review.

Invoked by protocols as:
    python decay.py --last-seen 2026-04-01T00:00:00Z \\
                    --half-life-days 7 --now 2026-04-20T00:00:00Z

Exits 0 and prints a single JSON object to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone


def _parse_iso(raw: str) -> datetime:
    """Parse an ISO-8601 timestamp, accepting a trailing 'Z' as UTC."""
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def freshness(
    last_seen: datetime,
    half_life_days: float,
    now: datetime,
    stale_threshold: float = 0.5,
) -> dict[str, float | bool | str]:
    """Compute freshness score and stale flag.

    Returns a dict with:
        freshness       — retention score in [0, 1]
        elapsed_days    — days since last review
        stale           — True when freshness < stale_threshold
        days_until_stale — days remaining until freshness drops to threshold
                           (0.0 if already stale)
    """
    if half_life_days <= 0:
        raise ValueError(f"half_life_days must be positive, got {half_life_days}")
    if not 0.0 < stale_threshold <= 1.0:
        raise ValueError(
            f"stale_threshold must be in (0, 1], got {stale_threshold}"
        )
    if now < last_seen:
        raise ValueError(f"now ({now}) is before last_seen ({last_seen})")

    elapsed_seconds = (now - last_seen).total_seconds()
    elapsed_days = elapsed_seconds / 86_400.0
    fresh_score = 2.0 ** (-elapsed_days / half_life_days)

    import math
    # freshness hits threshold when elapsed_days / half_life_days = -log2(threshold)
    stale_at_days = -math.log2(stale_threshold) * half_life_days
    days_until_stale = max(0.0, stale_at_days - elapsed_days)

    return {
        "freshness": fresh_score,
        "elapsed_days": elapsed_days,
        "stale": fresh_score < stale_threshold,
        "days_until_stale": days_until_stale,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--last-seen", required=True, help="ISO-8601 timestamp of last review")
    parser.add_argument("--half-life-days", type=float, required=True, help="Per-item stability, must be > 0")
    parser.add_argument(
        "--now",
        default=None,
        help="ISO-8601 timestamp to treat as current time (default: wall clock)",
    )
    parser.add_argument(
        "--stale-threshold",
        type=float,
        default=0.5,
        help="Freshness below this is considered stale (default: 0.5)",
    )
    args = parser.parse_args(argv)

    last_seen = _parse_iso(args.last_seen)
    now = _parse_iso(args.now) if args.now else datetime.now(tz=timezone.utc)

    result = freshness(last_seen, args.half_life_days, now, args.stale_threshold)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
