"""Tests for _iso.py — shared ISO-8601 timestamp parsing."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sensei.engine.scripts._iso import parse_iso


def test_parse_iso_trailing_z() -> None:
    """Trailing 'Z' is interpreted as UTC."""
    dt = parse_iso("2024-01-15T10:30:00Z")
    assert dt.tzinfo == timezone.utc
    assert dt == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)


def test_parse_iso_explicit_offset() -> None:
    """Explicit offset is preserved as-is."""
    dt = parse_iso("2024-01-15T10:30:00+05:30")
    assert dt.utcoffset() == timedelta(hours=5, minutes=30)
    assert dt.hour == 10
    assert dt.minute == 30


def test_parse_iso_naive_becomes_utc() -> None:
    """Naive datetime (no offset) gets UTC tzinfo."""
    dt = parse_iso("2024-01-15T10:30:00")
    assert dt.tzinfo == timezone.utc
    assert dt == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)


def test_parse_iso_roundtrip() -> None:
    """Parsing a formatted UTC datetime returns an equivalent datetime."""
    original = datetime(2024, 6, 15, 8, 0, 0, tzinfo=timezone.utc)
    formatted = original.isoformat()
    parsed = parse_iso(formatted)
    assert parsed == original
