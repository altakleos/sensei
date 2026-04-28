"""Tests for scripts/goal_priority.py.

Covers cross-goal priority ranking, the paused-goal regression guard from a6,
and priority/decay-risk/recency scoring invariants.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from sensei.engine.scripts.goal_priority import (
    _DEFAULT_DEADLINE_WEIGHT,
    _DEFAULT_HALF_LIFE_DAYS,
    _DEFAULT_STALE_THRESHOLD,
    main,
    score_goal,
)

NOW = datetime(2026, 4, 21, tzinfo=timezone.utc)


def _goal(
    *,
    goal_id: str = "learn-rust",
    status: str = "active",
    priority: str = "normal",
    nodes: dict | None = None,
) -> dict:
    return {
        "schema_version": 2,
        "goal_id": goal_id,
        "expressed_as": "Learn Rust",
        "created": "2026-04-01T00:00:00Z",
        "status": status,
        "priority": priority,
        "three_unknowns": {
            "prior_state": "none",
            "target_state": "vague",
            "constraints": "",
            "target_depth": "functional",
        },
        "nodes": nodes or {},
    }


def _profile(expertise: dict | None = None) -> dict:
    return {
        "schema_version": 0,
        "learner_id": "alice",
        "expertise_map": expertise or {},
    }


# --- score_goal filtering: paused goals included, completed/abandoned skipped ---


def test_paused_goal_included_with_status_marker() -> None:
    """Paused goals appear in output with status='paused' and score=0."""
    result = score_goal(_goal(status="paused"), _profile(), NOW)
    assert result is not None, "paused goal must not be filtered out"
    assert result["status"] == "paused"
    assert result["score"] == 0
    assert result["reason"] == "paused"


def test_completed_goal_returns_none() -> None:
    assert score_goal(_goal(status="completed"), _profile(), NOW) is None


def test_abandoned_goal_returns_none() -> None:
    assert score_goal(_goal(status="abandoned"), _profile(), NOW) is None


# --- score_goal priority ordering ---


def test_high_priority_scores_above_normal_above_low() -> None:
    high = score_goal(_goal(goal_id="h", priority="high"), _profile(), NOW)
    normal = score_goal(_goal(goal_id="n", priority="normal"), _profile(), NOW)
    low = score_goal(_goal(goal_id="l", priority="low"), _profile(), NOW)
    assert high is not None and normal is not None and low is not None, "active goals must not be filtered out"
    assert high["score"] > normal["score"] > low["score"]


# --- score_goal decay-risk term ---


def test_stale_completed_node_increases_score() -> None:
    stale_profile = _profile(
        expertise={
            "ownership": {"mastery": "solid", "last_seen": "2020-01-01T00:00:00Z"}
        }
    )
    stale_goal = _goal(nodes={"ownership": {"state": "completed", "prerequisites": []}})
    fresh_goal = _goal(nodes={})
    stale_score = score_goal(stale_goal, stale_profile, NOW)
    fresh_score = score_goal(fresh_goal, _profile(), NOW)
    assert stale_score is not None and fresh_score is not None, "active goals must not be filtered out"
    assert stale_score["score"] > fresh_score["score"]
    assert "stale" in stale_score["reason"]


def test_non_completed_nodes_do_not_affect_decay() -> None:
    """Only `completed` nodes contribute to decay risk — `active` ones don't count."""
    stale_profile = _profile(
        expertise={
            "ownership": {"mastery": "solid", "last_seen": "2020-01-01T00:00:00Z"}
        }
    )
    active_goal = _goal(nodes={"ownership": {"state": "active", "prerequisites": []}})
    no_nodes_goal = _goal(nodes={})
    active_score = score_goal(active_goal, stale_profile, NOW)
    no_nodes_score = score_goal(no_nodes_goal, _profile(), NOW)
    assert active_score is not None and no_nodes_score is not None, "active goals must not be filtered out"
    assert active_score["score"] == no_nodes_score["score"]


# --- main() CLI ---


def _write_instance(tmp_path: Path, goals: list[dict]) -> tuple[Path, Path]:
    goals_dir = tmp_path / "goals"
    goals_dir.mkdir()
    for g in goals:
        (goals_dir / f"{g['goal_id']}.yaml").write_text(yaml.safe_dump(g), encoding="utf-8")
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(_profile()), encoding="utf-8")
    return goals_dir, profile_path


def test_main_sorts_goals_by_score_desc(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    goals_dir, profile_path = _write_instance(
        tmp_path,
        [
            _goal(goal_id="low-one", priority="low"),
            _goal(goal_id="high-one", priority="high"),
            _goal(goal_id="normal-one", priority="normal"),
        ],
    )
    rc = main(
        [
            "--goals-dir",
            str(goals_dir),
            "--profile",
            str(profile_path),
            "--now",
            "2026-04-21T00:00:00Z",
        ]
    )
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    ordered = [g["slug"] for g in parsed["goals"]]
    assert ordered == ["high-one", "normal-one", "low-one"]


def test_main_includes_paused_goals_end_to_end(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Paused goals appear in ranked output with status marker — active goals rank first."""
    goals_dir, profile_path = _write_instance(
        tmp_path,
        [
            _goal(goal_id="active-one", priority="normal"),
            _goal(goal_id="paused-one", priority="high", status="paused"),
        ],
    )
    rc = main(
        [
            "--goals-dir",
            str(goals_dir),
            "--profile",
            str(profile_path),
            "--now",
            "2026-04-21T00:00:00Z",
        ]
    )
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    slugs = [g["slug"] for g in parsed["goals"]]
    assert "active-one" in slugs
    assert "paused-one" in slugs
    paused = next(g for g in parsed["goals"] if g["slug"] == "paused-one")
    assert paused["status"] == "paused"
    assert paused["score"] == 0


def test_main_missing_goals_dir_returns_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(_profile()), encoding="utf-8")
    rc = main(
        [
            "--goals-dir",
            str(tmp_path / "does-not-exist"),
            "--profile",
            str(profile_path),
        ]
    )
    assert rc == 1
    assert "not found" in json.loads(capsys.readouterr().out)["error"]


def test_main_missing_profile_returns_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    goals_dir = tmp_path / "goals"
    goals_dir.mkdir()
    rc = main(
        [
            "--goals-dir",
            str(goals_dir),
            "--profile",
            str(tmp_path / "missing.yaml"),
        ]
    )
    assert rc == 1
    assert "not found" in json.loads(capsys.readouterr().out)["error"]


def test_main_honors_half_life_override(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """a6 regression: --half-life-days must flow through to decay, not be hardcoded."""
    goals_dir = tmp_path / "goals"
    goals_dir.mkdir()
    # Completed node last seen ~8 days ago. With default half-life 7, it's stale.
    # With half-life 30, it is NOT stale.
    g = _goal(
        goal_id="rust",
        nodes={"ownership": {"state": "completed", "prerequisites": []}},
    )
    (goals_dir / "rust.yaml").write_text(yaml.safe_dump(g), encoding="utf-8")
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(
        yaml.safe_dump(
            _profile(
                expertise={
                    "ownership": {"mastery": "solid", "last_seen": "2026-04-13T00:00:00Z"}
                }
            )
        ),
        encoding="utf-8",
    )

    # Default half-life (7 days): 8 days is past half-life → freshness < 0.5 → stale.
    rc = main(
        [
            "--goals-dir",
            str(goals_dir),
            "--profile",
            str(profile_path),
            "--now",
            "2026-04-21T00:00:00Z",
        ]
    )
    assert rc == 0
    default_out = json.loads(capsys.readouterr().out)
    assert "stale" in default_out["goals"][0]["reason"]

    # Longer half-life: 8 days is still fresh → no "stale" in reason.
    rc = main(
        [
            "--goals-dir",
            str(goals_dir),
            "--profile",
            str(profile_path),
            "--half-life-days",
            "30",
            "--now",
            "2026-04-21T00:00:00Z",
        ]
    )
    assert rc == 0
    long_out = json.loads(capsys.readouterr().out)
    assert "stale" not in long_out["goals"][0]["reason"]


def test_defaults_match_engine_shipped_values() -> None:
    """If defaults.yaml ships different values, update accordingly."""
    assert _DEFAULT_HALF_LIFE_DAYS == 7.0
    assert _DEFAULT_STALE_THRESHOLD == 0.5
    assert _DEFAULT_DEADLINE_WEIGHT == 5.0


# --- deadline urgency ---


def test_imminent_deadline_scores_higher() -> None:
    """A goal with an imminent deadline scores higher than the same goal without."""
    base = _goal(goal_id="no-dl")
    with_dl = _goal(goal_id="dl")
    with_dl["deadline"] = "2026-04-23T00:00:00Z"  # 2 days away from NOW
    no_dl = score_goal(base, _profile(), NOW)
    dl = score_goal(with_dl, _profile(), NOW)
    assert no_dl is not None and dl is not None, "active goals must not be filtered out"
    assert dl["score"] > no_dl["score"]
    assert "deadline urgency" in dl["reason"]


def test_distant_deadline_minimal_boost() -> None:
    """A goal with a deadline 100 days away gets a tiny urgency boost."""
    g = _goal(goal_id="far")
    g["deadline"] = "2026-07-30T00:00:00Z"  # ~100 days from NOW
    result = score_goal(g, _profile(), NOW)
    assert result is not None, "active goal with deadline must not be filtered out"
    # Urgency = 5.0 * (1/100) = 0.05 — negligible vs base score of 20.
    assert "deadline urgency" in result["reason"]
    base = score_goal(_goal(), _profile(), NOW)
    assert base is not None, "active goal must not be filtered out"
    assert result["score"] - base["score"] < 1.0


def test_no_deadline_no_urgency() -> None:
    """A goal without a deadline field gets no urgency term."""
    result = score_goal(_goal(), _profile(), NOW)
    assert result is not None, "active goal must not be filtered out"
    assert "deadline" not in result["reason"]


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    goals_dir, profile_path = _write_instance(
        tmp_path, [_goal(goal_id="solo", priority="normal")]
    )
    script = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "sensei"
        / "engine"
        / "scripts"
        / "goal_priority.py"
    )
    assert script.is_file(), f"script path wrong: {script}"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--goals-dir",
            str(goals_dir),
            "--profile",
            str(profile_path),
            "--now",
            "2026-04-21T00:00:00Z",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert [g["slug"] for g in parsed["goals"]] == ["solo"]
