"""Hint freshness decay and expiration (per hints ingestion protocol).

Recomputes freshness for active/triaged hints using exponential decay:

    freshness = 2 ** (-elapsed_days / half_life_days)

Hints whose freshness drops below expire_threshold or whose age exceeds
expire_after_days are marked expired.

Invoked by protocols as:
    python hint_decay.py --hints-file instance/hints/hints.yaml \\
                         --half-life-days 14 --expire-threshold 0.2 \\
                         --expire-after-days 28 --now 2026-04-20T00:00:00Z

Exits 0 and prints updated hints list as JSON to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def _parse_iso(raw: str) -> datetime:
    """Parse an ISO-8601 timestamp, accepting a trailing 'Z' as UTC."""
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def update_hints(
    hints: list[dict[str, Any]],
    half_life_days: float,
    expire_threshold: float,
    expire_after_days: int,
    now: datetime,
) -> list[dict[str, Any]]:
    """Recompute freshness and expire stale hints in-place."""
    if half_life_days <= 0:
        raise ValueError(f"half_life_days must be positive, got {half_life_days}")

    for entry in hints:
        if entry.get("status") not in ("active", "triaged"):
            continue
        ingested = _parse_iso(entry["ingested"])
        elapsed_days = (now - ingested).total_seconds() / 86_400.0
        fresh = 2.0 ** (-elapsed_days / half_life_days)
        entry["freshness"] = round(fresh, 6)

        if fresh < expire_threshold or elapsed_days > expire_after_days:
            entry["status"] = "expired"

    return hints


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--hints-file", required=True, help="Path to hints.yaml")
    parser.add_argument("--half-life-days", type=float, required=True, help="Decay half-life in days")
    parser.add_argument("--expire-threshold", type=float, required=True, help="Freshness below this expires the hint")
    parser.add_argument("--expire-after-days", type=int, required=True, help="Hard cap age in days")
    parser.add_argument("--now", default=None, help="ISO-8601 current time (default: wall clock)")
    args = parser.parse_args(argv)

    if yaml is None:
        print("error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
        return 1

    with open(args.hints_file) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "hints" not in data:
        print("error: hints file must contain a top-level 'hints' key", file=sys.stderr)
        return 1

    now = _parse_iso(args.now) if args.now else datetime.now(tz=timezone.utc)

    updated = update_hints(
        data["hints"],
        half_life_days=args.half_life_days,
        expire_threshold=args.expire_threshold,
        expire_after_days=args.expire_after_days,
        now=now,
    )
    print(json.dumps(updated, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
