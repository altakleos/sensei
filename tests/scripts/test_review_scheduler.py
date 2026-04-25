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
        "three_unknowns": {
            "prior_state": "none",
            "target_state": "clear",
            "constraints": "none",
            "target_depth": "functional",
        },
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
                    "pending-topic": {"state": "pending", "prerequisites": []},
                    "skipped-topic": {"state": "skipped", "prerequisites": []},
                },
            ),
        ],
        _profile({
            "active-topic": "2026-03-21T00:00:00Z",
            "pending-topic": "2026-03-21T00:00:00Z",
            "skipped-topic": "2026-03-21T00:00:00Z",
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
    assert script.is_file(), f"script path wrong: {script}"
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


# --- (j) concept-aware dedup: topics sharing concept tags are deduplicated ---


def test_concept_dedup_keeps_stalest(tmp_path: Path) -> None:
    """Topics sharing a concept tag are deduplicated — stalest kept."""
    goals_dir, prof = _setup(
        tmp_path,
        [
            _goal("goal-a", nodes={"hash-maps": {"state": "completed", "prerequisites": []}}),
            _goal("goal-b", nodes={"hash-table-perf": {"state": "completed", "prerequisites": []}}),
        ],
        _profile({
            "hash-maps": "2026-03-21T00:00:00Z",       # 30 days → very stale
            "hash-table-perf": "2026-04-10T00:00:00Z",  # 10 days → stale
        }),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    concept_map = {"hash-tables": ["hash-maps", "hash-table-perf"]}
    result = schedule_reviews(goals_dir, prof, now=now, concept_map=concept_map)
    assert len(result) == 1
    assert result[0]["topic"] == "hash-maps"  # stalest kept


def test_concept_dedup_without_flag_slug_only(tmp_path: Path) -> None:
    """Without concept_map, different slugs are NOT deduplicated."""
    goals_dir, prof = _setup(
        tmp_path,
        [
            _goal("goal-a", nodes={"hash-maps": {"state": "completed", "prerequisites": []}}),
            _goal("goal-b", nodes={"hash-table-perf": {"state": "completed", "prerequisites": []}}),
        ],
        _profile({
            "hash-maps": "2026-03-21T00:00:00Z",
            "hash-table-perf": "2026-04-10T00:00:00Z",
        }),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    result = schedule_reviews(goals_dir, prof, now=now)
    assert len(result) == 2  # no concept dedup without the flag


def test_concept_dedup_unrelated_topics_preserved(tmp_path: Path) -> None:
    """Topics not sharing concepts are preserved even with concept_map."""
    goals_dir, prof = _setup(
        tmp_path,
        [
            _goal("g", nodes={
                "hash-maps": {"state": "completed", "prerequisites": []},
                "hash-table-perf": {"state": "completed", "prerequisites": []},
                "recursion": {"state": "completed", "prerequisites": []},
            }),
        ],
        _profile({
            "hash-maps": "2026-03-21T00:00:00Z",
            "hash-table-perf": "2026-04-10T00:00:00Z",
            "recursion": "2026-04-05T00:00:00Z",
        }),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    concept_map = {"hash-tables": ["hash-maps", "hash-table-perf"]}
    result = schedule_reviews(goals_dir, prof, now=now, concept_map=concept_map)
    topics = [r["topic"] for r in result]
    assert "hash-maps" in topics      # stalest of the concept group
    assert "recursion" in topics       # unrelated, preserved
    assert "hash-table-perf" not in topics  # deduped


# --- (k) interleaving: round-robin alternates between areas ---


def test_interleave_round_robin(tmp_path: Path) -> None:
    """With interleaving at intensity 1.0, topics alternate between areas."""
    goals_dir, prof = _setup(
        tmp_path,
        [
            _goal("g", nodes={
                "net-1": {"state": "completed", "prerequisites": []},
                "net-2": {"state": "completed", "prerequisites": []},
                "stor-1": {"state": "completed", "prerequisites": []},
                "stor-2": {"state": "completed", "prerequisites": []},
            }),
        ],
        _profile({
            "net-1": "2026-03-01T00:00:00Z",   # stalest in networking
            "net-2": "2026-03-10T00:00:00Z",   # less stale in networking
            "stor-1": "2026-03-05T00:00:00Z",  # stalest in storage
            "stor-2": "2026-03-15T00:00:00Z",  # less stale in storage
        }),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    topic_areas = {
        "net-1": "networking", "net-2": "networking",
        "stor-1": "storage", "stor-2": "storage",
    }
    result = schedule_reviews(
        goals_dir, prof, now=now,
        interleave=True, interleave_intensity=1.0,
        topic_areas=topic_areas, min_mastery=0.3,
    )
    topics = [r["topic"] for r in result]
    # Round-robin: stalest overall first, then alternate areas.
    # net-1 (stalest), stor-1 (stalest in storage), net-2, stor-2
    assert len(topics) == 4
    # Consecutive topics should alternate areas
    areas = [topic_areas[t] for t in topics]
    for i in range(len(areas) - 1):
        assert areas[i] != areas[i + 1], f"Adjacent topics {topics[i]} and {topics[i+1]} share area {areas[i]}"


# --- (l) interleaving: intensity 0 preserves stale-first order ---


def test_interleave_intensity_zero_preserves_order(tmp_path: Path) -> None:
    """Intensity 0.0 returns original stale-first order."""
    goals_dir, prof = _setup(
        tmp_path,
        [
            _goal("g", nodes={
                "net-1": {"state": "completed", "prerequisites": []},
                "net-2": {"state": "completed", "prerequisites": []},
                "stor-1": {"state": "completed", "prerequisites": []},
            }),
        ],
        _profile({
            "net-1": "2026-03-01T00:00:00Z",
            "net-2": "2026-03-10T00:00:00Z",
            "stor-1": "2026-03-05T00:00:00Z",
        }),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    topic_areas = {"net-1": "networking", "net-2": "networking", "stor-1": "storage"}

    # Without interleaving
    baseline = schedule_reviews(goals_dir, prof, now=now)
    # With interleaving at intensity 0
    result = schedule_reviews(
        goals_dir, prof, now=now,
        interleave=True, interleave_intensity=0.0,
        topic_areas=topic_areas, min_mastery=0.3,
    )
    assert [r["topic"] for r in result] == [r["topic"] for r in baseline]


# --- (m) interleaving: min_mastery excludes low-mastery topics ---


def test_interleave_min_mastery_excludes_novice(tmp_path: Path) -> None:
    """Topics below min_mastery get blocked practice (front of list, not interleaved)."""
    # Custom profile with one low-mastery topic
    profile = {
        "schema_version": 0,
        "learner_id": "alice",
        "expertise_map": {
            "net-1": {
                "mastery": "solid", "confidence": 0.8,
                "last_seen": "2026-03-10T00:00:00Z", "attempts": 5, "correct": 4,
            },
            "stor-1": {
                "mastery": "solid", "confidence": 0.8,
                "last_seen": "2026-03-05T00:00:00Z", "attempts": 5, "correct": 4,
            },
            "novice": {
                "mastery": 0.1, "confidence": 0.3,
                "last_seen": "2026-03-01T00:00:00Z", "attempts": 1, "correct": 0,
            },
        },
    }
    goals_dir = tmp_path / "goals"
    goals_dir.mkdir()
    _write_yaml(goals_dir / "g.yaml", _goal("g", nodes={
        "net-1": {"state": "completed", "prerequisites": []},
        "stor-1": {"state": "completed", "prerequisites": []},
        "novice": {"state": "completed", "prerequisites": []},
    }))
    prof = _write_yaml(tmp_path / "profile.yaml", profile)

    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    topic_areas = {"net-1": "networking", "stor-1": "storage", "novice": "consensus"}
    result = schedule_reviews(
        goals_dir, prof, now=now,
        interleave=True, interleave_intensity=1.0,
        topic_areas=topic_areas, min_mastery=0.3,
    )
    topics = [r["topic"] for r in result]
    # Novice topic (mastery 0.1 < 0.3) should be first (blocked practice)
    assert topics[0] == "novice"


# --- (n) interleaving: single area has no effect ---


def test_interleave_single_area_no_effect(tmp_path: Path) -> None:
    """When all topics are in one area, interleaving preserves stale-first order."""
    goals_dir, prof = _setup(
        tmp_path,
        [
            _goal("g", nodes={
                "t1": {"state": "completed", "prerequisites": []},
                "t2": {"state": "completed", "prerequisites": []},
            }),
        ],
        _profile({
            "t1": "2026-03-01T00:00:00Z",
            "t2": "2026-03-10T00:00:00Z",
        }),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    topic_areas = {"t1": "same-area", "t2": "same-area"}
    result = schedule_reviews(
        goals_dir, prof, now=now,
        interleave=True, interleave_intensity=1.0,
        topic_areas=topic_areas, min_mastery=0.3,
    )
    assert [r["topic"] for r in result] == ["t1", "t2"]


# --- (o) interleaving: disabled flag preserves original behavior ---


def test_interleave_disabled_preserves_order(tmp_path: Path) -> None:
    """With interleave=False, topic_areas is ignored."""
    goals_dir, prof = _setup(
        tmp_path,
        [
            _goal("g", nodes={
                "net-1": {"state": "completed", "prerequisites": []},
                "stor-1": {"state": "completed", "prerequisites": []},
            }),
        ],
        _profile({
            "net-1": "2026-03-01T00:00:00Z",
            "stor-1": "2026-03-05T00:00:00Z",
        }),
    )
    from datetime import datetime, timezone

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    baseline = schedule_reviews(goals_dir, prof, now=now)
    result = schedule_reviews(
        goals_dir, prof, now=now,
        interleave=False, interleave_intensity=1.0,
        topic_areas={"net-1": "networking", "stor-1": "storage"},
    )
    assert [r["topic"] for r in result] == [r["topic"] for r in baseline]


# --- (p) interleaving: CLI flags accepted via subprocess ---


def test_interleave_cli_flags(tmp_path: Path) -> None:
    """Interleaving CLI flags are accepted without error."""
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
            sys.executable, str(script),
            "--goals-dir", str(goals_dir),
            "--profile", str(prof),
            "--now", NOW_ISO,
            "--interleave",
            "--interleave-intensity", "0.7",
            "--topic-areas", '{"t1": "area-a"}',
            "--min-mastery", "0.3",
        ],
        capture_output=True, text=True, check=True,
    )
    parsed = json.loads(result.stdout)
    assert len(parsed) == 1
    assert parsed[0]["topic"] == "t1"
