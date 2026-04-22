"""Tests for scripts/session_allocator.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from sensei.engine.scripts.session_allocator import allocate_session, main

# --- allocate_session library function ---


def test_single_goal_gets_full_budget() -> None:
    """One goal with positive score receives the entire session budget."""
    goals = [{"slug": "rust", "score": 20.0}]
    result = allocate_session(goals, session_minutes=60)
    assert len(result["allocations"]) == 1
    assert result["allocations"][0]["slug"] == "rust"
    assert result["allocations"][0]["minutes"] == 60
    assert result["dropped"] == []


def test_two_goals_split_proportionally() -> None:
    """Two goals split minutes proportional to their scores."""
    goals = [
        {"slug": "rust", "score": 30.0},
        {"slug": "python", "score": 10.0},
    ]
    result = allocate_session(goals, session_minutes=60)
    slugs = {a["slug"]: a["minutes"] for a in result["allocations"]}
    # 30/(30+10)*60 = 45, 10/(30+10)*60 = 15
    assert slugs["rust"] == 45
    assert slugs["python"] == 15


def test_goal_below_minimum_is_dropped() -> None:
    """A goal whose proportional share is below min_minutes is dropped."""
    goals = [
        {"slug": "big", "score": 95.0},
        {"slug": "tiny", "score": 5.0},
    ]
    result = allocate_session(goals, session_minutes=60, min_minutes=5)
    # tiny gets floor(60 * 5/100) = floor(3.0) = 3 < 5 → dropped
    assert len(result["allocations"]) == 1
    assert result["allocations"][0]["slug"] == "big"
    assert len(result["dropped"]) == 1
    assert result["dropped"][0]["slug"] == "tiny"
    assert "below minimum" in result["dropped"][0]["reason"]


def test_empty_input_returns_empty_allocations() -> None:
    """No goals → empty allocations and dropped lists."""
    result = allocate_session([], session_minutes=60)
    assert result == {"allocations": [], "dropped": []}


def test_paused_goals_with_zero_score_skipped() -> None:
    """Paused goals (score=0) are not allocated any time."""
    goals = [
        {"slug": "active", "score": 20.0},
        {"slug": "paused", "score": 0},
    ]
    result = allocate_session(goals, session_minutes=60)
    slugs = [a["slug"] for a in result["allocations"]]
    assert "paused" not in slugs
    assert result["allocations"][0]["minutes"] == 60


def test_residue_distributed_largest_remainder_first() -> None:
    """Three equal-score goals with a 10-minute budget used to lose 1 minute
    to the floor operation (each got 3, total 9). With largest-remainder
    apportionment the sum matches session_minutes exactly: one goal gets the
    extra minute, ties broken by input order."""
    goals = [
        {"slug": "g1", "score": 3.0},
        {"slug": "g2", "score": 3.0},
        {"slug": "g3", "score": 3.0},
    ]
    result = allocate_session(goals, session_minutes=10, min_minutes=1)
    assert len(result["allocations"]) == 3
    total = sum(a["minutes"] for a in result["allocations"])
    assert total == 10
    # Residue goes to the earliest-declared candidate on residue-tie.
    by_slug = {a["slug"]: a["minutes"] for a in result["allocations"]}
    assert by_slug == {"g1": 4, "g2": 3, "g3": 3}


def test_residue_respects_dropped_minimum() -> None:
    """A candidate whose (floor + possible residue bonus) share is still below
    min_minutes remains dropped. Residue does not subvert the minimum floor."""
    # Scores [7, 1, 1, 1], session=10, total_score=10 → raws [7.0, 1.0, 1.0, 1.0]
    # Floors 7, 1, 1, 1, residue 0 — no redistribution needed.
    # With min_minutes=2, all three 1-minute candidates are dropped.
    goals = [
        {"slug": "big", "score": 7.0},
        {"slug": "small1", "score": 1.0},
        {"slug": "small2", "score": 1.0},
        {"slug": "small3", "score": 1.0},
    ]
    result = allocate_session(goals, session_minutes=10, min_minutes=2)
    assert [a["slug"] for a in result["allocations"]] == ["big"]
    assert result["allocations"][0]["minutes"] == 7
    assert {d["slug"] for d in result["dropped"]} == {"small1", "small2", "small3"}


# --- main() CLI ---


def test_main_reads_goals_json_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data = {"goals": [{"slug": "solo", "score": 10.0}]}
    gf = tmp_path / "goals.json"
    gf.write_text(json.dumps(data), encoding="utf-8")
    rc = main(["--goals-json", str(gf), "--session-minutes", "30"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out["allocations"]) == 1
    assert out["allocations"][0]["slug"] == "solo"


def test_main_missing_file_returns_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = main(["--goals-json", str(tmp_path / "nope.json"), "--session-minutes", "30"])
    assert rc == 1


# --- subprocess invocation (ADR-0006) ---


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    data = {"goals": [{"slug": "g", "score": 20.0}]}
    gf = tmp_path / "goals.json"
    gf.write_text(json.dumps(data), encoding="utf-8")
    script = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "sensei"
        / "engine"
        / "scripts"
        / "session_allocator.py"
    )
    assert script.is_file(), f"script path wrong: {script}"
    result = subprocess.run(
        [sys.executable, str(script), "--goals-json", str(gf), "--session-minutes", "60"],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert len(parsed["allocations"]) == 1
    assert parsed["allocations"][0]["slug"] == "g"
