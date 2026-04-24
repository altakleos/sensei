"""Tests for scripts/mastery_check.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from sensei.engine.scripts.mastery_check import main, meets, rank


def _profile(topic: str = "recursion", mastery: str = "developing") -> dict:
    return {
        "schema_version": 0,
        "learner_id": "alice",
        "expertise_map": {
            topic: {
                "mastery": mastery,
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


def test_rank_order() -> None:
    assert rank("none") < rank("shaky") < rank("developing") < rank("solid") < rank("mastered")


def test_rank_unknown_raises() -> None:
    with pytest.raises(ValueError, match="unknown mastery"):
        rank("expert")


def test_meets_simple() -> None:
    assert meets("mastered", "solid") is True
    assert meets("solid", "solid") is True
    assert meets("developing", "solid") is False
    assert meets("none", "none") is True


def test_pass_gate(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _write(tmp_path, _profile(mastery="solid"))
    rc = main(["--profile", str(path), "--topic", "recursion", "--required", "developing"])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["gate"] == "pass"
    assert parsed["current_mastery"] == "solid"
    assert parsed["required"] == "developing"


def test_fail_gate(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _write(tmp_path, _profile(mastery="shaky"))
    rc = main(["--profile", str(path), "--topic", "recursion", "--required", "solid"])
    assert rc == 3
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["gate"] == "fail"
    assert parsed["current_mastery"] == "shaky"


def test_absent_topic_treated_as_none(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _write(tmp_path, _profile(mastery="solid"))  # has recursion but not bfs
    rc = main(["--profile", str(path), "--topic", "bfs", "--required", "shaky"])
    assert rc == 3
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["current_mastery"] == "none"
    assert parsed["gate"] == "fail"
    assert "absent" in (parsed.get("reason") or "")


def test_absent_topic_passes_required_none(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _write(tmp_path, _profile(mastery="solid"))
    rc = main(["--profile", str(path), "--topic", "unknown", "--required", "none"])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["gate"] == "pass"


def test_invalid_profile_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad = _profile(mastery="solid")
    del bad["learner_id"]
    path = _write(tmp_path, bad)
    rc = main(["--profile", str(path), "--topic", "recursion", "--required", "solid"])
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["error"] == "invalid profile"


def test_missing_file_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--profile", str(tmp_path / "nope.yaml"), "--topic", "recursion", "--required", "solid"])
    assert rc == 1


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    path = _write(tmp_path, _profile(mastery="mastered"))
    script = Path(__file__).resolve().parents[2] / "src" / "sensei" / "engine" / "scripts" / "mastery_check.py"
    assert script.is_file(), f"script path wrong: {script}"
    result = subprocess.run(
        [sys.executable, str(script), "--profile", str(path), "--topic", "recursion", "--required", "solid"],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["gate"] == "pass"


def test_yaml_parse_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("{{{", encoding="utf-8")
    rc = main(["--profile", str(path), "--topic", "recursion", "--required", "solid"])
    assert rc == 1
    out = capsys.readouterr().out.lower()
    assert "yaml" in out or "parse" in out


def test_min_attempts_blocks_premature_pass(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Gate fails when attempts < min_attempts even if mastery level is met."""
    profile = {"schema_version": 2, "learner_id": "a", "expertise_map": {
        "caching": {"mastery": "solid", "confidence": 0.8, "last_seen": "2026-01-01T00:00:00Z", "attempts": 1, "correct": 1}
    }}
    (tmp_path / "p.yaml").write_text(yaml.safe_dump(profile))
    rc = main(["--profile", str(tmp_path / "p.yaml"), "--topic", "caching", "--required", "solid", "--min-attempts", "3"])
    assert rc == 3
    out = json.loads(capsys.readouterr().out)
    assert out["gate"] == "fail"
    assert "insufficient evidence" in out["reason"]


def test_min_attempts_passes_with_enough(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Gate passes when attempts >= min_attempts and mastery level is met."""
    profile = {"schema_version": 2, "learner_id": "a", "expertise_map": {
        "caching": {"mastery": "solid", "confidence": 0.8, "last_seen": "2026-01-01T00:00:00Z", "attempts": 5, "correct": 5}
    }}
    (tmp_path / "p.yaml").write_text(yaml.safe_dump(profile))
    rc = main(["--profile", str(tmp_path / "p.yaml"), "--topic", "caching", "--required", "solid", "--min-attempts", "3"])
    assert rc == 0


def test_min_ratio_blocks_low_accuracy(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Gate fails when correct/attempts ratio < min_ratio."""
    profile = {"schema_version": 2, "learner_id": "a", "expertise_map": {
        "caching": {"mastery": "solid", "confidence": 0.8, "last_seen": "2026-01-01T00:00:00Z", "attempts": 5, "correct": 3}
    }}
    (tmp_path / "p.yaml").write_text(yaml.safe_dump(profile))
    rc = main(["--profile", str(tmp_path / "p.yaml"), "--topic", "caching", "--required", "solid", "--min-ratio", "0.9"])
    assert rc == 3
    out = json.loads(capsys.readouterr().out)
    assert "accuracy too low" in out["reason"]


def test_min_ratio_passes_high_accuracy(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Gate passes when correct/attempts ratio >= min_ratio."""
    profile = {"schema_version": 2, "learner_id": "a", "expertise_map": {
        "caching": {"mastery": "solid", "confidence": 0.8, "last_seen": "2026-01-01T00:00:00Z", "attempts": 10, "correct": 9}
    }}
    (tmp_path / "p.yaml").write_text(yaml.safe_dump(profile))
    rc = main(["--profile", str(tmp_path / "p.yaml"), "--topic", "caching", "--required", "solid", "--min-ratio", "0.9"])
    assert rc == 0


def test_defaults_no_evidence_check(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Without --min-attempts or --min-ratio, gate behaves as before (backward compat)."""
    profile = {"schema_version": 2, "learner_id": "a", "expertise_map": {
        "caching": {"mastery": "solid", "confidence": 0.8, "last_seen": "2026-01-01T00:00:00Z", "attempts": 1, "correct": 1}
    }}
    (tmp_path / "p.yaml").write_text(yaml.safe_dump(profile))
    rc = main(["--profile", str(tmp_path / "p.yaml"), "--topic", "caching", "--required", "solid"])
    assert rc == 0
