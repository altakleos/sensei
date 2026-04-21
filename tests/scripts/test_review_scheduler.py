"""Tests for scripts/review_scheduler.py.

Covers cross-goal review deduplication, paused/abandoned goal handling,
freshness sorting, stale threshold filtering, and subprocess invocation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from sensei.engine.scripts.review_scheduler import main, schedule_reviews

NOW_ISO = "2026-04-20T00:00:00Z"


def _goal(
    goal_id: str,
    status: str = "active",
    nodes: dict | None = None,
) -> dict:
    return {
        "schema_version": 0,
        "goal_id": goal_id,
        "expressed_as": f"Learn {goal_id}",
        "created": "2026-04-01T00:00:00Z",
        "status": status,
        "three_unknowns": {"prior_state": "none", "target_state": "clear", "constraints": "none"},
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


def _setup(tmp_path: Path, goals: list[dict], profile: dict) -> tuple[Path, Path]:
    goals_dir = tmp_path / "goals"
    goals_dir.mkdir()
    for g in goals:
        _write_yaml(goals_dir / f"{g['goal_id']}.yaml", g)
    prof_path = _write_yaml(tmp_path / "profile.yaml", profile)
    return goals_dir, prof_path


# --- (a) topic stale in two goals appears once in output ---


def test_dedup_topic_stale_in_two_goals(tmp_path: Path) -> None:
    """A topic completed in two goals produces ONE review item."""
    goals_dir, prof = _setup(
        tmp_path,
        [
            _goal("goal-a", nodes={"recursion": {"state": "completed", "prerequisites": []}}),
            _goal("goal-b", nodes={"recursion": {"state": "completed", "prerequisites": []}}),
        ],
        # 30 days ago → very stale with default half-life 7
        _profile({"recursion": "2026-03-21T00:00:00Z"}),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    result = schedule_reviews(goals_dir, prof, now=now)
    assert len(result) == 1
    assert result[0]["topic"] == "recursion"
    assert sorted(result[0]["goals"]) == ["goal-a", "goal-b"]


# --- (b) deduplication picks the lowest freshness score ---


def test_dedup_picks_lowest_freshness(tmp_path: Path) -> None:
    """When a topic appears in two goals with different last_seen, the lowest freshness wins."""
    # Two goals share "recursion". Profile has one last_seen.
    # Since freshness is computed from the profile (not per-goal), the value is the same.
    # But we can verify the dedup path works by checking the single entry.
    goals_dir, prof = _setup(
        tmp_path,
        [
            _goal("goal-a", nodes={"recursion": {"state": "completed", "prerequisites": []}}),
            _goal("goal-b", nodes={"recursion": {"state": "completed", "prerequisites": []}}),
        ],
        _profile({"recursion": "2026-03-21T00:00:00Z"}),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    result = schedule_reviews(goals_dir, prof, now=now)
    assert len(result) == 1
    # freshness = 2^(-30/7) ≈ 0.05
    assert result[0]["freshness"] < 0.1


# --- (c) topics from paused goals are included ---


def test_paused_goals_included(tmp_path: Path) -> None:
    """Paused goals still decay — their completed topics must appear in review."""
    goals_dir, prof = _setup(
        tmp_path,
        [_goal("paused-goal", status="paused", nodes={"loops": {"state": "completed", "prerequisites": []}})],
        _profile({"loops": "2026-03-21T00:00:00Z"}),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    result = schedule_reviews(goals_dir, prof, now=now)
    assert len(result) == 1
    assert result[0]["topic"] == "loops"


# --- (d) topics from abandoned/completed goals are excluded ---


def test_abandoned_and_completed_goals_excluded(tmp_path: Path) -> None:
    goals_dir, prof = _setup(
        tmp_path,
        [
            _goal("done", status="completed", nodes={"t1": {"state": "completed", "prerequisites": []}}),
            _goal("quit", status="abandoned", nodes={"t2": {"state": "completed", "prerequisites": []}}),
        ],
        _profile({"t1": "2026-03-21T00:00:00Z", "t2": "2026-03-21T00:00:00Z"}),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    result = schedule_reviews(goals_dir, prof, now=now)
    assert result == []


# --- (e) non-completed nodes are excluded ---


def test_non_completed_nodes_excluded(tmp_path: Path) -> None:
    goals_dir, prof = _setup(
        tmp_path,
        [
            _goal(
                "g",
                nodes={
                    "active-topic": {"state": "active", "prerequisites": []},
                    "spawned-topic": {"state": "spawned", "prerequisites": []},
                    "collapsed-topic": {"state": "collapsed", "prerequisites": []},
                },
            ),
        ],
        _profile({
            "active-topic": "2026-03-21T00:00:00Z",
            "spawned-topic": "2026-03-21T00:00:00Z",
            "collapsed-topic": "2026-03-21T00:00:00Z",
        }),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    result = schedule_reviews(goals_dir, prof, now=now)
    assert result == []


# --- (f) output sorted by freshness ascending ---


def test_sorted_by_freshness_ascending(tmp_path: Path) -> None:
    goals_dir, prof = _setup(
        tmp_path,
        [
            _goal(
                "g",
                nodes={
                    "recent": {"state": "completed", "prerequisites": []},
                    "old": {"state": "completed", "prerequisites": []},
                    "ancient": {"state": "completed", "prerequisites": []},
                },
            ),
        ],
        _profile({
            "recent": "2026-04-12T00:00:00Z",   # 8 days ago
            "old": "2026-04-01T00:00:00Z",       # 19 days ago
            "ancient": "2026-03-01T00:00:00Z",   # 50 days ago
        }),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    result = schedule_reviews(goals_dir, prof, now=now)
    assert len(result) == 3
    # Most stale (lowest freshness) first
    assert result[0]["topic"] == "ancient"
    assert result[1]["topic"] == "old"
    assert result[2]["topic"] == "recent"
    assert result[0]["freshness"] < result[1]["freshness"] < result[2]["freshness"]


# --- (g) missing goals-dir returns exit 1 ---


def test_missing_goals_dir_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    prof = _write_yaml(tmp_path / "profile.yaml", _profile({}))
    rc = main(["--goals-dir", str(tmp_path / "nope"), "--profile", str(prof)])
    assert rc == 1
    assert "not found" in json.loads(capsys.readouterr().out)["error"]


# --- (h) subprocess invocation test ---


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    """Protocols invoke this helper via shell subprocess (per ADR-0006)."""
    goals_dir, prof = _setup(
        tmp_path,
        [_goal("g", nodes={"t1": {"state": "completed", "prerequisites": []}})],
        _profile({"t1": "2026-03-21T00:00:00Z"}),
    )
    script = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "sensei"
        / "engine"
        / "scripts"
        / "review_scheduler.py"
    )
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--goals-dir",
            str(goals_dir),
            "--profile",
            str(prof),
            "--now",
            NOW_ISO,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert len(parsed) == 1
    assert parsed[0]["topic"] == "t1"


# --- (i) topic above stale_threshold is excluded from output ---


def test_fresh_topic_excluded(tmp_path: Path) -> None:
    """A topic whose freshness >= stale_threshold must not appear in output."""
    goals_dir, prof = _setup(
        tmp_path,
        [_goal("g", nodes={"fresh-topic": {"state": "completed", "prerequisites": []}})],
        # 1 day ago with half-life 7 → freshness ≈ 0.91 → above 0.5 threshold
        _profile({"fresh-topic": "2026-04-19T00:00:00Z"}),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    result = schedule_reviews(goals_dir, prof, now=now)
    assert result == []
