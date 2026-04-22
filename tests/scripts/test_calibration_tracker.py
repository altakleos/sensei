"""Tests for calibration_tracker.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from sensei.engine.scripts.calibration_tracker import compute_calibration, main


def test_compute_calibration_no_topics():
    """No topics → None (insufficient data)."""
    assert compute_calibration({"expertise_map": {}}) is None


def test_compute_calibration_no_attempts():
    """Topics with zero attempts → None."""
    profile = {
        "expertise_map": {
            "recursion": {"mastery": "none", "confidence": 0.0, "last_seen": "2026-04-20T00:00:00Z", "attempts": 0, "correct": 0},
        }
    }
    assert compute_calibration(profile) is None


def test_compute_calibration_perfect():
    """All correct → 1.0."""
    profile = {
        "expertise_map": {
            "recursion": {"mastery": "solid", "confidence": 0.9, "last_seen": "2026-04-20T00:00:00Z", "attempts": 5, "correct": 5},
        }
    }
    assert compute_calibration(profile) == 1.0


def test_compute_calibration_partial():
    """4 correct out of 5 → 0.8."""
    profile = {
        "expertise_map": {
            "recursion": {"mastery": "solid", "confidence": 0.8, "last_seen": "2026-04-20T00:00:00Z", "attempts": 5, "correct": 4},
        }
    }
    assert compute_calibration(profile) == pytest.approx(0.8)


def test_compute_calibration_multiple_topics():
    """Aggregates across topics: 7 correct out of 10 → 0.7."""
    profile = {
        "expertise_map": {
            "recursion": {"mastery": "solid", "confidence": 0.8, "last_seen": "2026-04-20T00:00:00Z", "attempts": 5, "correct": 4},
            "sorting": {"mastery": "developing", "confidence": 0.6, "last_seen": "2026-04-20T00:00:00Z", "attempts": 5, "correct": 3},
        }
    }
    assert compute_calibration(profile) == pytest.approx(0.7)


def test_main_outputs_json(tmp_path: Path) -> None:
    profile = tmp_path / "profile.yaml"
    profile.write_text(yaml.safe_dump({
        "schema_version": 2,
        "learner_id": "alice",
        "expertise_map": {
            "recursion": {"mastery": "solid", "confidence": 0.8, "last_seen": "2026-04-20T00:00:00Z", "attempts": 10, "correct": 8},
        },
    }))
    rc = main(["--profile", str(profile)])
    assert rc == 0


def test_main_empty_profile(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    profile = tmp_path / "profile.yaml"
    profile.write_text("", encoding="utf-8")
    rc = main(["--profile", str(profile)])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["calibration_accuracy"] is None


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    """Smoke test: the python -m entry-point works."""
    profile = tmp_path / "profile.yaml"
    profile.write_text(yaml.safe_dump({
        "schema_version": 2,
        "learner_id": "alice",
        "expertise_map": {
            "recursion": {"mastery": "solid", "confidence": 0.8, "last_seen": "2026-04-20T00:00:00Z", "attempts": 5, "correct": 4},
        },
    }))
    result = subprocess.run(
        [sys.executable, "-m", "sensei.engine.scripts.calibration_tracker", "--profile", str(profile)],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["calibration_accuracy"] == pytest.approx(0.8)
