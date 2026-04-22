"""Tests for scripts/global_knowledge.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from sensei.engine.scripts.global_knowledge import check, main


def _profile(topic: str = "hash-maps", mastery: str = "solid") -> dict:
    return {
        "schema_version": 0,
        "learner_id": "alice",
        "expertise_map": {
            topic: {
                "mastery": mastery,
                "confidence": 0.8,
                "last_seen": "2026-04-18T14:20:00Z",
                "attempts": 5,
                "correct": 4,
            }
        },
    }


def _write(tmp_path: Path, profile: dict) -> Path:
    path = tmp_path / "profile.yaml"
    path.write_text(yaml.safe_dump(profile), encoding="utf-8")
    return path


def test_empty_profile_returns_unknown() -> None:
    result = check({}, "hash-maps")
    assert result == {"topic": "hash-maps", "known": False, "mastery": 0.0}


def test_missing_topic_returns_unknown() -> None:
    result = check(_profile(topic="recursion", mastery="mastered"), "hash-maps")
    assert result == {"topic": "hash-maps", "known": False, "mastery": 0.0}


@pytest.mark.parametrize(
    ("mastery", "known", "score"),
    [
        ("none", False, 0.0),
        ("shaky", False, 0.25),
        ("developing", False, 0.5),
        ("solid", True, 0.75),
        ("mastered", True, 1.0),
    ],
)
def test_known_threshold_at_solid(mastery: str, known: bool, score: float) -> None:
    """Per the cross-goal spec: known := mastery rank >= solid."""
    result = check(_profile(mastery=mastery), "hash-maps")
    assert result["known"] is known
    assert result["mastery"] == score


def test_main_pass(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _write(tmp_path, _profile(mastery="mastered"))
    rc = main(["--profile", str(path), "--topic", "hash-maps"])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed == {"topic": "hash-maps", "known": True, "mastery": 1.0}


def test_main_missing_file_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--profile", str(tmp_path / "nope.yaml"), "--topic", "x"])
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert "not found" in parsed["error"]


def test_main_corrupt_yaml_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("{{{", encoding="utf-8")
    rc = main(["--profile", str(path), "--topic", "x"])
    assert rc == 1
    out = capsys.readouterr().out.lower()
    assert "yaml" in out or "parse" in out


def test_main_non_mapping_yaml_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "list.yaml"
    path.write_text("- just\n- a\n- list\n", encoding="utf-8")
    rc = main(["--profile", str(path), "--topic", "x"])
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert "mapping" in parsed["error"]


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    """Protocols invoke this helper via shell subprocess."""
    path = _write(tmp_path, _profile(mastery="solid"))
    script = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "sensei"
        / "engine"
        / "scripts"
        / "global_knowledge.py"
    )
    assert script.is_file(), f"script path wrong: {script}"
    result = subprocess.run(
        [sys.executable, str(script), "--profile", str(path), "--topic", "hash-maps"],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed == {"topic": "hash-maps", "known": True, "mastery": 0.75}


# --- Re-demonstration override tests (T6) ---


def _goal(nodes: dict | None = None) -> dict:
    return {
        "schema_version": 0,
        "goal_id": "test-goal",
        "expressed_as": "Test goal",
        "created": "2026-04-01T00:00:00Z",
        "status": "active",
        "three_unknowns": {"prior_state": "none", "target_state": "clear", "constraints": "none"},
        "nodes": nodes or {},
    }


def _write_goal(tmp_path: Path, goal: dict) -> Path:
    path = tmp_path / "goal.yaml"
    path.write_text(yaml.safe_dump(goal), encoding="utf-8")
    return path


def test_redemonstration_overrides_known(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Topic globally known + goal requires re-demonstration → known: false."""
    prof_path = _write(tmp_path, _profile(mastery="mastered"))
    goal_path = _write_goal(tmp_path, _goal(nodes={
        "hash-maps": {"state": "completed", "prerequisites": [], "require_redemonstration": True},
    }))
    rc = main(["--profile", str(prof_path), "--topic", "hash-maps", "--goal", str(goal_path)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["known"] is False
    assert out["redemonstration_required"] is True
    assert out["mastery"] == 1.0


def test_no_redemonstration_keeps_known(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Topic globally known + goal does NOT require re-demonstration → known: true."""
    prof_path = _write(tmp_path, _profile(mastery="solid"))
    goal_path = _write_goal(tmp_path, _goal(nodes={
        "hash-maps": {"state": "completed", "prerequisites": [], "require_redemonstration": False},
    }))
    rc = main(["--profile", str(prof_path), "--topic", "hash-maps", "--goal", str(goal_path)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["known"] is True
    assert "redemonstration_required" not in out


def test_no_goal_flag_unchanged(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Without --goal, behavior is unchanged (backward compatible)."""
    prof_path = _write(tmp_path, _profile(mastery="mastered"))
    rc = main(["--profile", str(prof_path), "--topic", "hash-maps"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["known"] is True
    assert "redemonstration_required" not in out


def test_goal_topic_not_in_goal_unchanged(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """--goal provided but topic not in goal's nodes → existing behavior unchanged."""
    prof_path = _write(tmp_path, _profile(mastery="mastered"))
    goal_path = _write_goal(tmp_path, _goal(nodes={
        "other-topic": {"state": "active", "prerequisites": []},
    }))
    rc = main(["--profile", str(prof_path), "--topic", "hash-maps", "--goal", str(goal_path)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["known"] is True
    assert "redemonstration_required" not in out


# --- Concept-aware evidence tests ---


def test_concept_evidence_from_peer() -> None:
    """Topic not in profile but a concept peer is known → concept_evidence: true."""
    profile = _profile(topic="hash-maps", mastery="mastered")
    result = check(profile, "hash-table-perf", concept_peers=["hash-maps"])
    assert result["known"] is False
    assert result["concept_evidence"] is True
    assert result["evidence_from"] == "hash-maps"


def test_concept_evidence_peer_not_known() -> None:
    """Topic not in profile, peer exists but not known → no concept_evidence."""
    profile = _profile(topic="hash-maps", mastery="shaky")
    result = check(profile, "hash-table-perf", concept_peers=["hash-maps"])
    assert result["known"] is False
    assert "concept_evidence" not in result


def test_concept_evidence_no_peers() -> None:
    """Without concept_peers, no concept evidence reported."""
    result = check(_profile(topic="hash-maps", mastery="mastered"), "unknown-topic")
    assert result["known"] is False
    assert "concept_evidence" not in result


def test_concept_peers_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """--concept-peers CLI flag passes through to check()."""
    prof_path = _write(tmp_path, _profile(topic="hash-maps", mastery="solid"))
    rc = main([
        "--profile", str(prof_path),
        "--topic", "hash-table-perf",
        "--concept-peers", '["hash-maps"]',
    ])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["concept_evidence"] is True
    assert out["evidence_from"] == "hash-maps"
