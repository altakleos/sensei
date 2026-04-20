"""Tests for scripts/decay.py."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from sensei.engine.scripts.decay import freshness, main


def _utc(y: int, mo: int, d: int) -> datetime:
    return datetime(y, mo, d, tzinfo=timezone.utc)


def test_fresh_when_just_seen() -> None:
    t = _utc(2026, 4, 20)
    result = freshness(last_seen=t, half_life_days=7, now=t)
    assert result["freshness"] == pytest.approx(1.0)
    assert result["elapsed_days"] == pytest.approx(0.0)
    assert result["stale"] is False


def test_half_life_reached() -> None:
    """At exactly half_life_days elapsed, freshness should be 0.5."""
    last = _utc(2026, 4, 1)
    now = last + timedelta(days=7)
    result = freshness(last_seen=last, half_life_days=7, now=now)
    assert result["freshness"] == pytest.approx(0.5)


def test_stale_flag_flips_below_threshold() -> None:
    last = _utc(2026, 4, 1)
    now = last + timedelta(days=14)  # two half-lives → 0.25
    result = freshness(last_seen=last, half_life_days=7, now=now, stale_threshold=0.5)
    assert result["freshness"] == pytest.approx(0.25)
    assert result["stale"] is True
    assert result["days_until_stale"] == 0.0


def test_days_until_stale_linearity() -> None:
    last = _utc(2026, 4, 1)
    # At half-life the score is 0.5 == threshold, days_until_stale should be 0.
    now = last + timedelta(days=7)
    result = freshness(last_seen=last, half_life_days=7, now=now, stale_threshold=0.5)
    assert result["days_until_stale"] == pytest.approx(0.0)


def test_days_until_stale_with_custom_threshold() -> None:
    last = _utc(2026, 4, 1)
    # freshness drops to 0.25 at 2*half_life — solve for when it hits 0.8
    # 2 ** (-t/7) = 0.8  →  t = -7 * log2(0.8)
    expected = -7 * math.log2(0.8)
    result = freshness(last_seen=last, half_life_days=7, now=last, stale_threshold=0.8)
    assert result["days_until_stale"] == pytest.approx(expected)


def test_invalid_half_life() -> None:
    with pytest.raises(ValueError, match="half_life_days"):
        freshness(last_seen=_utc(2026, 4, 1), half_life_days=0, now=_utc(2026, 4, 2))


def test_invalid_threshold() -> None:
    with pytest.raises(ValueError, match="stale_threshold"):
        freshness(
            last_seen=_utc(2026, 4, 1),
            half_life_days=7,
            now=_utc(2026, 4, 2),
            stale_threshold=1.5,
        )


def test_now_before_last_seen_raises() -> None:
    with pytest.raises(ValueError, match="before last_seen"):
        freshness(last_seen=_utc(2026, 4, 10), half_life_days=7, now=_utc(2026, 4, 1))


def test_main_emits_json(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(
        [
            "--last-seen",
            "2026-04-01T00:00:00Z",
            "--half-life-days",
            "7",
            "--now",
            "2026-04-08T00:00:00Z",
        ]
    )
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["freshness"] == pytest.approx(0.5)
    assert parsed["stale"] is False


def test_script_runs_as_subprocess() -> None:
    """Protocols invoke helpers via shell subprocess (per ADR-0006). Verify that path works."""
    script = Path(__file__).resolve().parents[2] / "src" / "sensei" / "engine" / "scripts" / "decay.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--last-seen",
            "2026-04-01T00:00:00Z",
            "--half-life-days",
            "7",
            "--now",
            "2026-04-15T00:00:00Z",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["freshness"] == pytest.approx(0.25)
    assert parsed["stale"] is True
