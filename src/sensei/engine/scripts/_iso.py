"""Shared ISO-8601 timestamp parsing for engine scripts.

Single source of truth for the "parse an ISO-8601 timestamp, treat a
trailing 'Z' as UTC, default naive datetimes to UTC" idiom that otherwise
gets copy-pasted into every script that reads timestamps from learner state.
"""

from __future__ import annotations

from datetime import datetime, timezone


def parse_iso(raw: str) -> datetime:
    """Parse an ISO-8601 timestamp. Accepts a trailing 'Z' as UTC."""
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
