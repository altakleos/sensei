"""Tests for scripts/resume_planner.py.

Covers decay-aware resume planning: stale topic detection, freshness sorting,
completed-only filtering, frontier recomputation, and subprocess invocation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from sensei.engine.scripts.resume_planner import main, plan_resume

NOW_ISO = "2026-04-20T00:00:00Z"
NOW = datetime(2026, 4, 20, tzinfo=timezone.utc)


def _goal(
    goal_id: str = "learn-rust",
    status: str = "active",
    nodes: dict | None = None,
) -> dict:
    return {
        "schema_version": 0,
        "goal_id": goal_id,
        "expressed_as": f"Learn {goal_id}",
        "created": "2026-04-01T00:00:00Z",
        "status": status,
        "three_unknowns": {"prior_state": "none", "target_state": "clear", "constraints": "none", "target_depth": "functional"},
        "nodes": nodes or {},
    }


def _profile(topics: dict[str, str] | None = None) -> dict:
    """Build a profile. topics maps slug → last_seen ISO string."""
    expertise: dict = {}
    for slug, last_seen in (topics or {}).items():
        expertise[slug] = {
            "mastery": "solid",
            "confidence": 0.8,
            "last_seen": last_seen,
            "attempts": 5,
            "correct": 4,
        }
    return {"schema_version": 0, "learner_id": "alice", "expertise_map": expertise}


def _write_yaml(path: Path, data: dict) -> Path:
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def _setup(tmp_path: Path, goal: dict, profile: dict) -> tuple[Path, Path]:
    goal_path = _write_yaml(tmp_path / "goal.yaml", goal)
    prof_path = _write_yaml(tmp_path / "profile.yaml", profile)
    return goal_path, prof_path


# --- (a) goal paused 30 days → stale topics, action=review_first ---


def test_paused_30_days_review_first(tmp_path: Path) -> None:
    """Goal with completed topics last seen 30 days ago → stale, review_first."""
    goal_path, prof_path = _setup(
        tmp_path,
        _goal(nodes={
            "ownership": {"state": "completed", "prerequisites": []},
            "borrowing": {"state": "completed", "prerequisites": ["ownership"]},
            "lifetimes": {"state": "pending", "prerequisites": ["borrowing"]},
        }),
        _profile({
            "ownership": "2026-03-21T00:00:00Z",
            "borrowing": "2026-03-21T00:00:00Z",
        }),
    )
    result = plan_resume(goal_path, prof_path, now=NOW)
    assert result["recommended_action"] == "review_first"
    assert len(result["stale_topics"]) == 2
    slugs = [t["slug"] for t in result["stale_topics"]]
    assert "ownership" in slugs
    assert "borrowing" in slugs


# --- (b) goal paused 1 day → no stale topics, action=continue ---


def test_paused_1_day_continue(tmp_path: Path) -> None:
    """Goal with completed topics last seen 1 day ago → fresh, continue."""
    goal_path, prof_path = _setup(
        tmp_path,
        _goal(nodes={
            "ownership": {"state": "completed", "prerequisites": []},
            "borrowing": {"state": "pending", "prerequisites": ["ownership"]},
        }),
        _profile({"ownership": "2026-04-19T00:00:00Z"}),
    )
    result = plan_resume(goal_path, prof_path, now=NOW)
    assert result["recommended_action"] == "continue"
    assert result["stale_topics"] == []


# --- (c) stale topics sorted by freshness ascending ---


def test_stale_topics_sorted_by_freshness(tmp_path: Path) -> None:
    """Most decayed topic (lowest freshness) appears first."""
    goal_path, prof_path = _setup(
        tmp_path,
        _goal(nodes={
            "recent": {"state": "completed", "prerequisites": []},
            "old": {"state": "completed", "prerequisites": []},
            "ancient": {"state": "completed", "prerequisites": []},
        }),
        _profile({
            "recent": "2026-04-12T00:00:00Z",   # 8 days ago
            "old": "2026-04-01T00:00:00Z",       # 19 days ago
            "ancient": "2026-03-01T00:00:00Z",   # 50 days ago
        }),
    )
    result = plan_resume(goal_path, prof_path, now=NOW)
    assert len(result["stale_topics"]) == 3
    assert result["stale_topics"][0]["slug"] == "ancient"
    assert result["stale_topics"][1]["slug"] == "old"
    assert result["stale_topics"][2]["slug"] == "recent"
    assert (
        result["stale_topics"][0]["freshness"]
        < result["stale_topics"][1]["freshness"]
        < result["stale_topics"][2]["freshness"]
    )


# --- (d) only completed nodes checked for decay ---


def test_only_completed_nodes_checked(tmp_path: Path) -> None:
    """Active, pending, and skipped nodes are not checked for decay."""
    goal_path, prof_path = _setup(
        tmp_path,
        _goal(nodes={
            "active-topic": {"state": "active", "prerequisites": []},
            "pending-topic": {"state": "pending", "prerequisites": []},
            "skipped-topic": {"state": "skipped", "prerequisites": []},
        }),
        _profile({
            "active-topic": "2026-03-01T00:00:00Z",
            "pending-topic": "2026-03-01T00:00:00Z",
            "skipped-topic": "2026-03-01T00:00:00Z",
        }),
    )
    result = plan_resume(goal_path, prof_path, now=NOW)
    assert result["stale_topics"] == []
    assert result["recommended_action"] == "continue"


# --- (e) missing profile → exit 1 ---


def test_missing_profile_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    goal_path = _write_yaml(tmp_path / "goal.yaml", _goal())
    rc = main(["--goal", str(goal_path), "--profile", str(tmp_path / "nope.yaml")])
    assert rc == 1
    assert "not found" in json.loads(capsys.readouterr().out)["error"]


# --- (f) subprocess invocation test ---


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    """Protocols invoke this helper via shell subprocess (per ADR-0006)."""
    goal_path, prof_path = _setup(
        tmp_path,
        _goal(nodes={"t1": {"state": "completed", "prerequisites": []}}),
        _profile({"t1": "2026-03-21T00:00:00Z"}),
    )
    script = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "sensei"
        / "engine"
        / "scripts"
        / "resume_planner.py"
    )
    assert script.is_file(), f"script path wrong: {script}"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--goal",
            str(goal_path),
            "--profile",
            str(prof_path),
            "--now",
            NOW_ISO,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["recommended_action"] == "review_first"
    assert len(parsed["stale_topics"]) == 1
    assert parsed["stale_topics"][0]["slug"] == "t1"


# --- (g) frontier is recomputed (verify frontier field is populated) ---


def test_frontier_recomputed(tmp_path: Path) -> None:
    """The frontier field should contain pending nodes whose prereqs are done."""
    goal_path, prof_path = _setup(
        tmp_path,
        _goal(nodes={
            "basics": {"state": "completed", "prerequisites": []},
            "intermediate": {"state": "pending", "prerequisites": ["basics"]},
            "advanced": {"state": "pending", "prerequisites": ["intermediate"]},
        }),
        _profile({"basics": "2026-03-21T00:00:00Z"}),
    )
    result = plan_resume(goal_path, prof_path, now=NOW)
    # "intermediate" has all prereqs completed → on the frontier
    assert "intermediate" in result["frontier"]
    # "advanced" depends on "intermediate" (pending) → NOT on the frontier
    assert "advanced" not in result["frontier"]
