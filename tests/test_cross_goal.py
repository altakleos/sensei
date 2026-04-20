"""Tests for cross-goal intelligence scripts (global_knowledge.py, goal_priority.py)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from sensei.engine.scripts.global_knowledge import main as gk_main
from sensei.engine.scripts.goal_priority import main as gp_main

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _profile(topics: dict[str, str] | None = None) -> dict:
    """Build a minimal valid profile with given topic→mastery pairs."""
    expertise: dict = {}
    for slug, mastery in (topics or {}).items():
        expertise[slug] = {
            "mastery": mastery,
            "confidence": 0.6,
            "last_seen": "2026-04-18T14:00:00Z",
            "attempts": 3,
            "correct": 2,
        }
    return {"schema_version": 0, "learner_id": "tester", "expertise_map": expertise}


def _goal(slug: str, status: str = "active", priority: str = "normal", nodes: dict | None = None) -> dict:
    return {
        "schema_version": 0,
        "goal_id": slug,
        "expressed_as": f"Learn {slug}",
        "created": "2026-04-01T00:00:00Z",
        "status": status,
        "priority": priority,
        "three_unknowns": {"prior_state": "none", "target_state": "clear", "constraints": "none"},
        "nodes": nodes or {},
    }


def _write_yaml(tmp_path: Path, name: str, data: dict) -> Path:
    p = tmp_path / name
    p.write_text(yaml.safe_dump(data), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# global_knowledge tests
# ---------------------------------------------------------------------------

class TestGlobalKnowledge:
    def test_topic_known_mastered(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Mastery 'mastered' (score 1.0) → known=true."""
        path = _write_yaml(tmp_path, "profile.yaml", _profile({"hash-maps": "mastered"}))
        rc = gk_main(["--profile", str(path), "--topic", "hash-maps"])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["known"] is True
        assert out["mastery"] == 1.0

    def test_topic_known_solid(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Mastery 'solid' (score 0.75) → known=true."""
        path = _write_yaml(tmp_path, "profile.yaml", _profile({"hash-maps": "solid"}))
        rc = gk_main(["--profile", str(path), "--topic", "hash-maps"])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["known"] is True
        assert out["mastery"] == 0.75

    def test_topic_unknown_developing(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Mastery 'developing' (score 0.5) → known=false."""
        path = _write_yaml(tmp_path, "profile.yaml", _profile({"hash-maps": "developing"}))
        rc = gk_main(["--profile", str(path), "--topic", "hash-maps"])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["known"] is False
        assert out["mastery"] == 0.5

    def test_topic_not_in_profile(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Topic absent from expertise_map → known=false, mastery=0.0."""
        path = _write_yaml(tmp_path, "profile.yaml", _profile({}))
        rc = gk_main(["--profile", str(path), "--topic", "recursion"])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["known"] is False
        assert out["mastery"] == 0.0

    def test_missing_file_returns_1(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        rc = gk_main(["--profile", str(tmp_path / "nope.yaml"), "--topic", "x"])
        assert rc == 1


# ---------------------------------------------------------------------------
# goal_priority tests
# ---------------------------------------------------------------------------

class TestGoalPriority:
    def test_ranks_by_priority(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """High > normal > low when no decay risk or recency."""
        goals_dir = tmp_path / "goals"
        goals_dir.mkdir()
        _write_yaml(goals_dir, "low.yaml", _goal("low-goal", priority="low"))
        _write_yaml(goals_dir, "high.yaml", _goal("high-goal", priority="high"))
        _write_yaml(goals_dir, "normal.yaml", _goal("normal-goal", priority="normal"))
        prof = _write_yaml(tmp_path, "profile.yaml", _profile({}))

        rc = gp_main(["--goals-dir", str(goals_dir), "--profile", str(prof), "--now", "2026-04-20T00:00:00Z"])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        slugs = [g["slug"] for g in out["goals"]]
        assert slugs == ["high-goal", "normal-goal", "low-goal"]

    def test_skips_completed_and_abandoned(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Completed and abandoned goals are excluded from ranking."""
        goals_dir = tmp_path / "goals"
        goals_dir.mkdir()
        _write_yaml(goals_dir, "done.yaml", _goal("done", status="completed"))
        _write_yaml(goals_dir, "quit.yaml", _goal("quit", status="abandoned"))
        _write_yaml(goals_dir, "live.yaml", _goal("live", status="active"))
        prof = _write_yaml(tmp_path, "profile.yaml", _profile({}))

        rc = gp_main(["--goals-dir", str(goals_dir), "--profile", str(prof), "--now", "2026-04-20T00:00:00Z"])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        slugs = [g["slug"] for g in out["goals"]]
        assert slugs == ["live"]

    def test_decay_risk_boosts_score(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """A goal with stale completed topics scores higher than one without."""
        goals_dir = tmp_path / "goals"
        goals_dir.mkdir()
        # Goal A: normal priority, 2 stale completed topics.
        _write_yaml(goals_dir, "a.yaml", _goal("goal-a", priority="normal", nodes={
            "topic-one": {"state": "completed", "prerequisites": []},
            "topic-two": {"state": "completed", "prerequisites": []},
        }))
        # Goal B: normal priority, no completed topics.
        _write_yaml(goals_dir, "b.yaml", _goal("goal-b", priority="normal"))
        # Profile: topics last seen 30 days ago (very stale).
        prof_data = _profile({"topic-one": "solid", "topic-two": "solid"})
        prof_data["expertise_map"]["topic-one"]["last_seen"] = "2026-03-20T00:00:00Z"
        prof_data["expertise_map"]["topic-two"]["last_seen"] = "2026-03-20T00:00:00Z"
        prof = _write_yaml(tmp_path, "profile.yaml", prof_data)

        rc = gp_main(["--goals-dir", str(goals_dir), "--profile", str(prof), "--now", "2026-04-20T00:00:00Z"])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["goals"][0]["slug"] == "goal-a"
        assert out["goals"][0]["score"] > out["goals"][1]["score"]
        assert "2 stale topics" in out["goals"][0]["reason"]

    def test_missing_goals_dir_returns_1(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        prof = _write_yaml(tmp_path, "profile.yaml", _profile({}))
        rc = gp_main(["--goals-dir", str(tmp_path / "nope"), "--profile", str(prof)])
        assert rc == 1
