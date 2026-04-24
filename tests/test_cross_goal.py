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
        "three_unknowns": {"prior_state": "none", "target_state": "clear", "constraints": "none", "target_depth": "functional"},
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

    def test_redemonstration_override_integration(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Integration: profile says mastered + goal requires re-demonstration → known=false."""
        prof = _write_yaml(tmp_path, "profile.yaml", _profile({"hash-maps": "mastered"}))
        goal = _goal("sys-prog", nodes={
            "hash-maps": {"state": "completed", "prerequisites": [], "require_redemonstration": True},
        })
        goal_path = _write_yaml(tmp_path, "goal.yaml", goal)
        rc = gk_main(["--profile", str(prof), "--topic", "hash-maps", "--goal", str(goal_path)])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["known"] is False
        assert out["redemonstration_required"] is True
        assert out["mastery"] == 1.0


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

    def test_half_life_override_affects_stale_count(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Passing --half-life-days shortens/lengthens the stale window — the
        number of stale completed topics (and thus the score) must change."""
        goals_dir = tmp_path / "goals"
        goals_dir.mkdir()
        _write_yaml(goals_dir, "g.yaml", _goal("g", priority="normal", nodes={
            "t1": {"state": "completed", "prerequisites": []},
            "t2": {"state": "completed", "prerequisites": []},
        }))
        # Topics last seen 10 days ago.
        prof_data = _profile({"t1": "solid", "t2": "solid"})
        prof_data["expertise_map"]["t1"]["last_seen"] = "2026-04-10T00:00:00Z"
        prof_data["expertise_map"]["t2"]["last_seen"] = "2026-04-10T00:00:00Z"
        prof = _write_yaml(tmp_path, "profile.yaml", prof_data)

        # With a 7-day half-life, 10 days elapsed → freshness ≈ 0.37 → stale.
        rc = gp_main([
            "--goals-dir", str(goals_dir), "--profile", str(prof),
            "--half-life-days", "7", "--stale-threshold", "0.5",
            "--now", "2026-04-20T00:00:00Z",
        ])
        assert rc == 0
        out_7 = json.loads(capsys.readouterr().out)
        assert "2 stale topics" in out_7["goals"][0]["reason"]

        # With a 30-day half-life, 10 days elapsed → freshness ≈ 0.79 → fresh.
        rc = gp_main([
            "--goals-dir", str(goals_dir), "--profile", str(prof),
            "--half-life-days", "30", "--stale-threshold", "0.5",
            "--now", "2026-04-20T00:00:00Z",
        ])
        assert rc == 0
        out_30 = json.loads(capsys.readouterr().out)
        assert "stale topic" not in out_30["goals"][0]["reason"]
        # The longer half-life goal scores lower (no decay-risk bonus).
        assert out_30["goals"][0]["score"] < out_7["goals"][0]["score"]


# ---------------------------------------------------------------------------
# Cross-goal integration test — exercises all four invariants (T26)
# ---------------------------------------------------------------------------

class TestCrossGoalIntegration:
    """Multi-goal scenario exercising all four cross-goal invariants.

    Setup: two goals sharing 'recursion'. Profile has 'recursion' mastered
    but stale (last seen 30 days ago). Goal A requires re-demonstration on
    'recursion'. Goal B has an imminent deadline.
    """

    @pytest.fixture()
    def scenario(self, tmp_path: Path):
        """Build the shared multi-goal scenario files."""
        goals_dir = tmp_path / "goals"
        goals_dir.mkdir()

        # Goal A: requires re-demonstration on 'recursion'.
        goal_a = _goal("algo-deep-dive", priority="normal", nodes={
            "recursion": {
                "state": "completed",
                "prerequisites": [],
                "require_redemonstration": True,
            },
            "sorting": {"state": "completed", "prerequisites": ["recursion"]},
        })
        goal_a_path = _write_yaml(goals_dir, "algo-deep-dive.yaml", goal_a)

        # Goal B: imminent deadline, also depends on 'recursion'.
        goal_b = _goal("interview-prep", priority="normal", nodes={
            "recursion": {"state": "completed", "prerequisites": []},
            "dynamic-programming": {"state": "in_progress", "prerequisites": ["recursion"]},
        })
        goal_b["deadline"] = "2026-04-22T00:00:00Z"
        goal_b_path = _write_yaml(goals_dir, "interview-prep.yaml", goal_b)

        # Profile: 'recursion' mastered but stale (30 days), 'sorting' solid and stale.
        prof_data = _profile({"recursion": "mastered", "sorting": "solid"})
        prof_data["expertise_map"]["recursion"]["last_seen"] = "2026-03-21T00:00:00Z"
        prof_data["expertise_map"]["sorting"]["last_seen"] = "2026-03-21T00:00:00Z"
        prof_path = _write_yaml(tmp_path, "profile.yaml", prof_data)

        return {
            "goals_dir": goals_dir,
            "goal_a_path": goal_a_path,
            "goal_b_path": goal_b_path,
            "prof_path": prof_path,
            "now": "2026-04-20T00:00:00Z",
        }

    def test_invariant1_global_knowledge_redemonstration(
        self, scenario: dict, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Invariant 1: global_knowledge with --goal returns known=false for
        the re-demonstration goal, known=true without --goal."""
        s = scenario

        # Without --goal: recursion is mastered → known=true.
        rc = gk_main(["--profile", str(s["prof_path"]), "--topic", "recursion"])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["known"] is True

        # With --goal pointing to goal A (require_redemonstration) → known=false.
        rc = gk_main([
            "--profile", str(s["prof_path"]),
            "--topic", "recursion",
            "--goal", str(s["goal_a_path"]),
        ])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["known"] is False
        assert out["redemonstration_required"] is True

        # With --goal pointing to goal B (no re-demo) → known=true.
        rc = gk_main([
            "--profile", str(s["prof_path"]),
            "--topic", "recursion",
            "--goal", str(s["goal_b_path"]),
        ])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["known"] is True

    def test_invariant2_review_deduplication(
        self, scenario: dict, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Invariant 2: review_scheduler deduplicates 'recursion' across both
        goals — one entry, not two."""
        from sensei.engine.scripts.review_scheduler import main as rs_main

        s = scenario
        rc = rs_main([
            "--goals-dir", str(s["goals_dir"]),
            "--profile", str(s["prof_path"]),
            "--half-life-days", "7",
            "--stale-threshold", "0.5",
            "--now", s["now"],
        ])
        assert rc == 0
        reviews = json.loads(capsys.readouterr().out)

        # 'recursion' appears exactly once despite being in both goals.
        recursion_entries = [r for r in reviews if r["topic"] == "recursion"]
        assert len(recursion_entries) == 1
        # The deduplicated entry references both goals.
        assert set(recursion_entries[0]["goals"]) == {"algo-deep-dive", "interview-prep"}

        # 'sorting' also stale, appears once (only in goal A).
        sorting_entries = [r for r in reviews if r["topic"] == "sorting"]
        assert len(sorting_entries) == 1

    def test_invariant3_priority_and_allocation(
        self, scenario: dict, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Invariant 3: goal_priority ranks the deadline goal higher;
        session_allocator produces allocations."""
        from sensei.engine.scripts.session_allocator import allocate_session

        s = scenario

        # Priority ranking: deadline goal should rank higher.
        rc = gp_main([
            "--goals-dir", str(s["goals_dir"]),
            "--profile", str(s["prof_path"]),
            "--now", s["now"],
        ])
        assert rc == 0
        priority_out = json.loads(capsys.readouterr().out)
        slugs = [g["slug"] for g in priority_out["goals"]]
        assert slugs[0] == "interview-prep", "deadline goal should rank first"

        # Session allocation: feed priority output into allocator.
        result = allocate_session(priority_out["goals"], session_minutes=60)
        assert len(result["allocations"]) >= 1
        alloc_slugs = [a["slug"] for a in result["allocations"]]
        assert "interview-prep" in alloc_slugs

    def test_review_scheduler_skips_malformed_goal_yaml(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """One corrupt goal file must not crash cross-goal review scheduling —
        it should be skipped with a warning on stderr, and reviews for the
        remaining goals should still be produced (exit 0)."""
        from sensei.engine.scripts.review_scheduler import main as rs_main

        goals_dir = tmp_path / "goals"
        goals_dir.mkdir()

        # One valid goal with a stale completed topic.
        good = _goal("good-goal", nodes={
            "recursion": {"state": "completed", "prerequisites": []},
        })
        _write_yaml(goals_dir, "good.yaml", good)

        # One malformed YAML that raises on safe_load.
        (goals_dir / "bad.yaml").write_text("{{{ not yaml", encoding="utf-8")

        # Profile: 'recursion' stale (30 days old with 7-day half-life).
        prof_data = _profile({"recursion": "solid"})
        prof_data["expertise_map"]["recursion"]["last_seen"] = "2026-03-21T00:00:00Z"
        prof = _write_yaml(tmp_path, "profile.yaml", prof_data)

        rc = rs_main([
            "--goals-dir", str(goals_dir),
            "--profile", str(prof),
            "--half-life-days", "7",
            "--stale-threshold", "0.5",
            "--now", "2026-04-20T00:00:00Z",
        ])
        captured = capsys.readouterr()
        assert rc == 0, captured.err
        reviews = json.loads(captured.out)
        # The good goal's stale topic is returned …
        assert len(reviews) == 1
        assert reviews[0]["topic"] == "recursion"
        # … and the malformed file is surfaced via a stderr warning.
        assert "bad.yaml" in captured.err
        assert "warning" in captured.err.lower() or "skipping" in captured.err.lower()

    def test_invariant4_resume_planner_stale_topics(
        self, scenario: dict, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Invariant 4: resume_planner on a paused goal produces review_first
        with stale topics."""
        from sensei.engine.scripts.resume_planner import main as rp_main

        s = scenario

        # Pause goal A and run resume_planner against it.
        paused_goal = _goal("algo-deep-dive", status="paused", nodes={
            "recursion": {
                "state": "completed",
                "prerequisites": [],
                "require_redemonstration": True,
            },
            "sorting": {"state": "completed", "prerequisites": ["recursion"]},
        })
        paused_goal["paused_at"] = "2026-03-21T00:00:00Z"
        paused_path = s["goal_a_path"]
        paused_path.write_text(yaml.safe_dump(paused_goal), encoding="utf-8")

        rc = rp_main([
            "--goal", str(paused_path),
            "--profile", str(s["prof_path"]),
            "--half-life-days", "7",
            "--stale-threshold", "0.5",
            "--now", s["now"],
        ])
        assert rc == 0
        plan = json.loads(capsys.readouterr().out)

        assert plan["recommended_action"] == "review_first"
        stale_slugs = [t["slug"] for t in plan["stale_topics"]]
        assert "recursion" in stale_slugs
        assert "sorting" in stale_slugs
        # Sorted by freshness ascending (most decayed first).
        freshness_values = [t["freshness"] for t in plan["stale_topics"]]
        assert freshness_values == sorted(freshness_values)


# ---------------------------------------------------------------------------
# Concept-aware cross-goal integration tests (T39)
# ---------------------------------------------------------------------------

class TestConceptAwareCrossGoal:
    """Two goals with different slugs but shared concept tags."""

    def test_concept_dedup_review_scheduler(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """review_scheduler with concept_map deduplicates different-slug topics
        sharing a concept tag — keeps the stalest."""
        from sensei.engine.scripts.review_scheduler import main as rs_main

        goals_dir = tmp_path / "goals"
        goals_dir.mkdir()

        # Goal A: "hash-maps" with concept tag "hash-tables"
        _write_yaml(goals_dir, "data-structures.yaml", _goal("data-structures", nodes={
            "hash-maps": {"state": "completed", "prerequisites": [], "concept_tags": ["hash-tables"]},
        }))
        # Goal B: "hash-table-perf" with concept tag "hash-tables"
        _write_yaml(goals_dir, "sys-prog.yaml", _goal("sys-prog", nodes={
            "hash-table-perf": {"state": "completed", "prerequisites": [], "concept_tags": ["hash-tables"]},
        }))

        prof_data = _profile({"hash-maps": "solid", "hash-table-perf": "solid"})
        prof_data["expertise_map"]["hash-maps"]["last_seen"] = "2026-03-21T00:00:00Z"
        prof_data["expertise_map"]["hash-table-perf"]["last_seen"] = "2026-04-10T00:00:00Z"
        prof = _write_yaml(tmp_path, "profile.yaml", prof_data)

        concept_map = {"hash-tables": ["hash-maps", "hash-table-perf"]}
        rc = rs_main([
            "--goals-dir", str(goals_dir),
            "--profile", str(prof),
            "--half-life-days", "7",
            "--stale-threshold", "0.5",
            "--now", "2026-04-20T00:00:00Z",
            "--concept-map", json.dumps(concept_map),
        ])
        assert rc == 0
        reviews = json.loads(capsys.readouterr().out)
        assert len(reviews) == 1
        assert reviews[0]["topic"] == "hash-maps"  # stalest

    def test_concept_evidence_global_knowledge(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """global_knowledge with --concept-peers reports evidence from a known
        peer topic sharing concept tags."""
        prof_data = _profile({"hash-maps": "mastered"})
        prof = _write_yaml(tmp_path, "profile.yaml", prof_data)

        rc = gk_main([
            "--profile", str(prof),
            "--topic", "hash-table-perf",
            "--concept-peers", '["hash-maps"]',
        ])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["known"] is False
        assert out["concept_evidence"] is True
        assert out["evidence_from"] == "hash-maps"
