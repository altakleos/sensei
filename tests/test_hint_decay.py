"""Tests for hint_decay.py freshness computation and CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from sensei.engine.scripts.hint_decay import update_hints

HALF_LIFE = 14.0
THRESHOLD = 0.2
EXPIRE_DAYS = 28
NOW = datetime(2026, 4, 20, tzinfo=timezone.utc)


def _hint(status: str = "active", days_ago: int = 0) -> dict:
    from datetime import timedelta

    ingested = (NOW - timedelta(days=days_ago)).isoformat()
    return {"id": "h1", "status": status, "ingested": ingested}


def test_freshness_day_zero() -> None:
    hints = update_hints([_hint(days_ago=0)], HALF_LIFE, THRESHOLD, EXPIRE_DAYS, NOW)
    assert hints[0]["freshness"] == 1.0


def test_freshness_at_half_life() -> None:
    hints = update_hints([_hint(days_ago=14)], HALF_LIFE, THRESHOLD, EXPIRE_DAYS, NOW)
    assert hints[0]["freshness"] == 0.5


def test_freshness_at_two_half_lives() -> None:
    hints = update_hints([_hint(days_ago=28)], HALF_LIFE, THRESHOLD, EXPIRE_DAYS, NOW)
    assert hints[0]["freshness"] == 0.25


def test_expiration_by_threshold() -> None:
    # 50 days -> freshness = 2^(-50/14) ≈ 0.084 < 0.2
    hints = update_hints([_hint(days_ago=50)], HALF_LIFE, THRESHOLD, EXPIRE_DAYS, NOW)
    assert hints[0]["status"] == "expired"
    assert hints[0]["freshness"] < THRESHOLD


def test_expiration_by_age() -> None:
    # 29 days > expire_after_days=28, even though freshness ~0.24 > threshold
    hints = update_hints([_hint(days_ago=29)], HALF_LIFE, THRESHOLD, expire_after_days=28, now=NOW)
    assert hints[0]["status"] == "expired"


def test_non_active_hints_untouched() -> None:
    for status in ("absorbed", "irrelevant", "expired"):
        hint = _hint(status=status, days_ago=100)
        hints = update_hints([hint], HALF_LIFE, THRESHOLD, EXPIRE_DAYS, NOW)
        assert "freshness" not in hints[0]
        assert hints[0]["status"] == status


def test_cli_invocation(tmp_path: Path) -> None:
    hints_file = tmp_path / "hints.yaml"
    data = {"hints": [_hint(days_ago=7)]}
    hints_file.write_text(yaml.dump(data))

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sensei.engine.scripts.hint_decay",
            "--hints-file", str(hints_file),
            "--half-life-days", "14",
            "--expire-threshold", "0.2",
            "--expire-after-days", "28",
            "--now", "2026-04-20T00:00:00Z",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert isinstance(output, list)
    assert output[0]["freshness"] == 0.707107
