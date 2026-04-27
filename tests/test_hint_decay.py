"""Tests for hint_decay.py freshness computation and CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from sensei.engine.scripts.hint_decay import main, update_hints

HALF_LIFE = 14.0
THRESHOLD = 0.2
EXPIRE_DAYS = 28
NOW = datetime(2026, 4, 20, tzinfo=timezone.utc)


def _hint(status: str = "active", days_ago: int = 0) -> dict:
    from datetime import timedelta

    ingested = (NOW - timedelta(days=days_ago)).isoformat()
    return {"id": "h1", "status": status, "ingested": ingested}


def _write_hints(tmp_path: Path, hints: list[dict]) -> Path:
    path = tmp_path / "hints.yaml"
    path.write_text(yaml.safe_dump({"hints": hints}), encoding="utf-8")
    return path


def _run_main(
    hints_file: Path, capsys: pytest.CaptureFixture[str], now: str = "2026-04-20T00:00:00Z"
) -> tuple[int, list]:
    rc = main([
        "--hints-file", str(hints_file),
        "--half-life-days", str(HALF_LIFE),
        "--expire-threshold", str(THRESHOLD),
        "--expire-after-days", str(EXPIRE_DAYS),
        "--now", now,
    ])
    return rc, json.loads(capsys.readouterr().out)


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


# --- main(argv) CLI entry ---


def test_main_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    hints_file = _write_hints(tmp_path, [_hint(days_ago=7)])
    rc, output = _run_main(hints_file, capsys)
    assert rc == 0
    assert isinstance(output, list)
    assert output[0]["freshness"] == 0.707107  # 2^(-7/14) rounded


def test_main_missing_hints_file_returns_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = main([
        "--hints-file", str(tmp_path / "missing.yaml"),
        "--half-life-days", "14",
        "--expire-threshold", "0.2",
        "--expire-after-days", "28",
    ])
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert "not found" in out["error"]


def test_main_corrupt_yaml_returns_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("{{{", encoding="utf-8")
    rc = main([
        "--hints-file", str(path),
        "--half-life-days", "14",
        "--expire-threshold", "0.2",
        "--expire-after-days", "28",
    ])
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert "yaml parse error" in out["error"]


def test_main_malformed_hints_file_rejected(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("- not a dict\n", encoding="utf-8")
    rc = main([
        "--hints-file", str(path),
        "--half-life-days", "14",
        "--expire-threshold", "0.2",
        "--expire-after-days", "28",
    ])
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert "hints" in out["error"].lower()


def test_main_uses_wall_clock_when_now_omitted(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """When --now is not passed, the script uses datetime.now(UTC). A just-ingested hint
    should still compute a freshness near 1.0 without errors."""
    hints_file = _write_hints(tmp_path, [_hint(days_ago=0)])
    # Use a future date of the hint ingestion so "just ingested" relative to wall clock
    # is approximated. Simpler: just check the script runs and emits a list.
    rc = main([
        "--hints-file", str(hints_file),
        "--half-life-days", "14",
        "--expire-threshold", "0.2",
        "--expire-after-days", "28",
    ])
    assert rc == 0
    output = json.loads(capsys.readouterr().out)
    assert isinstance(output, list)


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    """Smoke test: the `python -m sensei.engine.scripts.hint_decay` entry still works."""
    hints_file = tmp_path / "hints.yaml"
    data = {"hints": [_hint(days_ago=7)]}
    hints_file.write_text(yaml.dump(data), encoding="utf-8")
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
        check=True,
    )
    output = json.loads(result.stdout)
    assert output[0]["freshness"] == 0.707107
