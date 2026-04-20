"""Tests for scripts/check_profile.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from sensei.engine.scripts.check_profile import main, validate_profile


def _valid_profile() -> dict:
    return {
        "schema_version": 0,
        "learner_id": "alice",
        "expertise_map": {
            "recursion": {
                "mastery": "developing",
                "confidence": 0.6,
                "last_seen": "2026-04-18T14:20:00Z",
                "attempts": 4,
                "correct": 3,
            }
        },
    }


def _write(tmp_path: Path, profile: dict) -> Path:
    path = tmp_path / "profile.yaml"
    path.write_text(yaml.safe_dump(profile), encoding="utf-8")
    return path


def test_minimal_valid_profile() -> None:
    status, errors = validate_profile(_valid_profile())
    assert status == "ok"
    assert errors == []


def test_empty_expertise_map_is_valid() -> None:
    profile = _valid_profile()
    profile["expertise_map"] = {}
    status, errors = validate_profile(profile)
    assert status == "ok"
    assert errors == []


def test_missing_required_field_fails() -> None:
    profile = _valid_profile()
    del profile["learner_id"]
    status, errors = validate_profile(profile)
    assert status == "schema"
    assert any("learner_id" in err for err in errors)


def test_invalid_mastery_level_fails() -> None:
    profile = _valid_profile()
    profile["expertise_map"]["recursion"]["mastery"] = "expert"  # not in enum
    status, errors = validate_profile(profile)
    assert status == "schema"


def test_confidence_out_of_range_fails() -> None:
    profile = _valid_profile()
    profile["expertise_map"]["recursion"]["confidence"] = 1.5
    status, errors = validate_profile(profile)
    assert status == "schema"


def test_invalid_topic_slug_fails() -> None:
    profile = _valid_profile()
    # Dot not allowed per the slug pattern.
    profile["expertise_map"]["Recursion.Intro"] = profile["expertise_map"].pop("recursion")
    status, errors = validate_profile(profile)
    assert status == "schema"


def test_schema_version_must_be_zero() -> None:
    profile = _valid_profile()
    profile["schema_version"] = 1
    status, errors = validate_profile(profile)
    assert status == "schema"


def test_cross_field_correct_exceeds_attempts() -> None:
    profile = _valid_profile()
    profile["expertise_map"]["recursion"]["correct"] = 5
    profile["expertise_map"]["recursion"]["attempts"] = 3
    status, errors = validate_profile(profile)
    assert status == "cross_field"
    assert any("exceeds attempts" in err for err in errors)


def test_main_ok(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _write(tmp_path, _valid_profile())
    rc = main(["--profile", str(path)])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["status"] == "ok"


def test_main_schema_failure(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    profile = _valid_profile()
    del profile["learner_id"]
    path = _write(tmp_path, profile)
    rc = main(["--profile", str(path)])
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["status"] == "schema"


def test_main_cross_field_failure(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    profile = _valid_profile()
    profile["expertise_map"]["recursion"]["correct"] = 99
    profile["expertise_map"]["recursion"]["attempts"] = 1
    path = _write(tmp_path, profile)
    rc = main(["--profile", str(path)])
    assert rc == 2
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["status"] == "cross_field"


def test_main_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--profile", str(tmp_path / "nope.yaml")])
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["status"] == "schema"
    assert any("not found" in err for err in parsed["errors"])


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    path = _write(tmp_path, _valid_profile())
    script = Path(__file__).resolve().parents[2] / "src" / "sensei" / "engine" / "scripts" / "check_profile.py"
    result = subprocess.run(
        [sys.executable, str(script), "--profile", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["status"] == "ok"
