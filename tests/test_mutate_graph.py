"""Tests for mutate_graph.py — validated state transitions.

Calls `mutate_graph.main(argv)` directly so pytest-cov can observe the code
paths. One subprocess smoke test at the end verifies the CLI entry point
still runs as a separate process (how protocols actually invoke it per
ADR-0006).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from sensei.engine.scripts.mutate_graph import main


def _make_curriculum(tmp_path: Path, nodes: dict) -> Path:
    cur = tmp_path / "curriculum.yaml"
    cur.write_text(yaml.safe_dump({"nodes": nodes}), encoding="utf-8")
    return cur


def _run(
    cur: Path,
    operation: str,
    node: str,
    capsys: pytest.CaptureFixture[str],
    prerequisites: list[str] | None = None,
    subgraph: dict | None = None,
) -> tuple[int, dict]:
    argv = ["--curriculum", str(cur), "--operation", operation, "--node", node]
    if prerequisites:
        argv += ["--prerequisites", ",".join(prerequisites)]
    if subgraph:
        argv += ["--subgraph", json.dumps(subgraph)]
    rc = main(argv)
    return rc, json.loads(capsys.readouterr().out)


def test_activate_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "pending", "prerequisites": ["A"]},
    })
    rc, out = _run(cur, "activate", "B", capsys)
    assert rc == 0
    assert out["valid"] is True
    assert out["new_state"] == "active"


def test_activate_fails_already_active(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "active", "prerequisites": ["A"]},
        "C": {"state": "pending", "prerequisites": ["A"]},
    })
    rc, out = _run(cur, "activate", "C", capsys)
    assert rc == 1
    assert out["valid"] is False


def test_activate_fails_not_on_frontier(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "pending", "prerequisites": []},
        "B": {"state": "pending", "prerequisites": ["A"]},
    })
    rc, out = _run(cur, "activate", "B", capsys)
    assert rc == 1
    assert out["valid"] is False


def test_complete_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "active", "prerequisites": []},
    })
    rc, out = _run(cur, "complete", "A", capsys)
    assert rc == 0
    assert out["new_state"] == "completed"


def test_complete_fails_not_active(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "pending", "prerequisites": []},
    })
    rc, out = _run(cur, "complete", "A", capsys)
    assert rc == 1
    assert out["valid"] is False


def test_skip_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "pending", "prerequisites": ["A"]},
    })
    rc, out = _run(cur, "skip", "B", capsys)
    assert rc == 0
    assert out["new_state"] == "skipped"
    # On-disk state reflects the skip (dependents would now see B as done).
    data = yaml.safe_load(cur.read_text())
    assert data["nodes"]["B"]["state"] == "skipped"


def test_insert_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc, out = _run(cur, "insert", "B", capsys, prerequisites=["A"])
    assert rc == 0
    assert out["new_state"] == "inserted"
    data = yaml.safe_load(cur.read_text())
    assert "B" in data["nodes"]
    assert data["nodes"]["B"]["prerequisites"] == ["A"]


def test_insert_fails_cycle(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Constructing a cycle via insert requires priming the graph with a forward
    reference first: A→B→C (where C doesn't exist yet), then insert C→A closes
    the loop A→B→C→A. `_has_cycle` rejects the mutation with exit 2."""
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "pending", "prerequisites": ["B"]},
        "B": {"state": "pending", "prerequisites": []},
    })
    data = yaml.safe_load(cur.read_text())
    data["nodes"]["B"]["prerequisites"] = ["C"]
    cur.write_text(yaml.safe_dump(data), encoding="utf-8")
    rc, out = _run(cur, "insert", "C", capsys, prerequisites=["A"])
    assert rc == 2
    assert out["valid"] is False
    assert "cycle" in out["error"]


def test_insert_fails_missing_prerequisite(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc, out = _run(cur, "insert", "B", capsys, prerequisites=["X"])
    assert rc == 1
    assert out["valid"] is False


def test_decompose_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "pending", "prerequisites": ["A"]},
        "C": {"state": "pending", "prerequisites": ["B"]},
    })
    subgraph = {"nodes": {
        "B1": {"prerequisites": ["A"]},
        "B2": {"prerequisites": ["B1"]},
    }}
    rc, out = _run(cur, "decompose", "B", capsys, subgraph=subgraph)
    assert rc == 0
    assert out["new_state"] == "decomposed"
    data = yaml.safe_load(cur.read_text())
    assert "B1" in data["nodes"]
    assert "B2" in data["nodes"]
    # C should now depend on B2 (leaf of subgraph) instead of B
    assert "B2" in data["nodes"]["C"]["prerequisites"]
    assert "B" not in data["nodes"]["C"]["prerequisites"]


def test_missing_curriculum_file_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--curriculum", str(tmp_path / "missing.yaml"), "--operation", "activate", "--node", "A"])
    assert rc == 1


def test_unknown_operation_rejected(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {"A": {"state": "pending", "prerequisites": []}})
    with pytest.raises(SystemExit):
        # argparse choices rejection exits the process before main returns.
        main(["--curriculum", str(cur), "--operation", "destroy", "--node", "A"])


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    """Smoke test: protocols invoke this helper via subprocess (per ADR-0006). Verify that path works."""
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "pending", "prerequisites": ["A"]},
    })
    script = Path(__file__).resolve().parent.parent / "src" / "sensei" / "engine" / "scripts" / "mutate_graph.py"
    assert script.is_file(), f"script path wrong: {script}"
    result = subprocess.run(
        [sys.executable, str(script), "--curriculum", str(cur), "--operation", "activate", "--node", "B"],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["new_state"] == "active"


# --- Coverage: _do_activate node not in nodes (line 96) ---


def test_activate_fails_nonexistent_node(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc, out = _run(cur, "activate", "Z", capsys)
    assert rc == 1
    assert "does not exist" in out["error"]


# --- Coverage: _do_skip node not in nodes (line 115) ---


def test_skip_fails_nonexistent_node(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc, out = _run(cur, "skip", "Z", capsys)
    assert rc == 1
    assert "does not exist" in out["error"]


# --- Coverage: _do_insert node already exists (line 124) ---


def test_insert_fails_node_already_exists(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc, out = _run(cur, "insert", "A", capsys, prerequisites=["A"])
    assert rc == 1
    assert "already exists" in out["error"]


# --- Coverage: _do_insert no prerequisites (line 126) ---


def test_insert_fails_no_prerequisites(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc = main(["--curriculum", str(cur), "--operation", "insert", "--node", "B"])
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert "prerequisites required" in out["error"]


# --- Coverage: _do_decompose node not in nodes (line 138) ---


def test_decompose_fails_nonexistent_node(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    subgraph = {"nodes": {"X": {"prerequisites": []}}}
    rc, out = _run(cur, "decompose", "Z", capsys, subgraph=subgraph)
    assert rc == 1
    assert "does not exist" in out["error"]


# --- Coverage: _do_decompose no subgraph (line 140) ---


def test_decompose_fails_no_subgraph(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc = main(["--curriculum", str(cur), "--operation", "decompose", "--node", "A"])
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert "subgraph required" in out["error"]


# --- Coverage: mutate() unknown op (line 184) — not reachable via CLI due to argparse choices,
#     but exercised via direct mutate() call ---

from sensei.engine.scripts.mutate_graph import mutate  # noqa: E402  (import sited near its single test for locality)


def test_mutate_unknown_op_returns_error() -> None:
    nodes = {"A": {"state": "completed", "prerequisites": []}}
    code, state = mutate(nodes, "destroy", "A", None, None)
    assert code == 1
    assert state == ""


# --- Coverage: YAML parse error (lines 203-204) ---


def test_main_yaml_parse_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad = tmp_path / "curriculum.yaml"
    bad.write_text(":\n  - :\n    bad: [unclosed", encoding="utf-8")
    rc = main(["--curriculum", str(bad), "--operation", "activate", "--node", "A"])
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert "yaml parse error" in out["error"]


# --- Coverage: no 'nodes' key (line 207) ---


def test_main_missing_nodes_key(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad = tmp_path / "curriculum.yaml"
    bad.write_text(yaml.safe_dump({"title": "no nodes here"}), encoding="utf-8")
    rc = main(["--curriculum", str(bad), "--operation", "activate", "--node", "A"])
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert "nodes" in out["error"]


# --- Coverage: invalid subgraph JSON (lines 217-218) ---


def test_main_invalid_subgraph_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {"A": {"state": "completed", "prerequisites": []}})
    rc = main(["--curriculum", str(cur), "--operation", "decompose", "--node", "A",
               "--subgraph", "{bad json}"])
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert "invalid subgraph JSON" in out["error"]


# --- T11: _do_complete stamps completed_at ---


def test_complete_stamps_completed_at(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Completing a node sets completed_at to the passed now value."""
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "active", "prerequisites": []},
    })
    now_val = "2026-04-27T12:00:00Z"
    rc = main(["--curriculum", str(cur), "--operation", "complete", "--node", "A", "--now", now_val])
    assert rc == 0
    data = yaml.safe_load(cur.read_text())
    assert data["nodes"]["A"]["completed_at"] == now_val


def test_complete_completed_at_matches_now_arg(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A specific --now value appears verbatim in the output and on-disk node."""
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "active", "prerequisites": []},
    })
    specific_now = "2025-12-25T08:30:00Z"
    rc = main(["--curriculum", str(cur), "--operation", "complete", "--node", "A", "--now", specific_now])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["valid"] is True
    data = yaml.safe_load(cur.read_text())
    assert data["nodes"]["A"]["completed_at"] == specific_now


# --- T14: Integration — complete stamps completed_at, review_scheduler uses stability ---


def test_complete_then_review_uses_stability(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Integration: complete a node via mutate, verify completed_at, then
    confirm review_scheduler respects per-topic stability."""
    from datetime import datetime, timezone

    from sensei.engine.scripts.review_scheduler import schedule_reviews

    # Step 1: create curriculum with one active node and complete it
    cur = _make_curriculum(tmp_path, {
        "topic-a": {"state": "active", "prerequisites": []},
    })
    now_iso = "2026-04-20T00:00:00Z"
    rc = main(["--curriculum", str(cur), "--operation", "complete", "--node", "topic-a", "--now", now_iso])
    assert rc == 0

    # Step 2: verify completed_at is set
    data = yaml.safe_load(cur.read_text())
    assert data["nodes"]["topic-a"]["completed_at"] == now_iso

    # Step 3: set up goals dir and profile with stability for review_scheduler
    goals_dir = tmp_path / "goals"
    goals_dir.mkdir()
    goal = {
        "schema_version": 0,
        "goal_id": "test-goal",
        "expressed_as": "Test",
        "created": "2026-04-01T00:00:00Z",
        "status": "active",
        "three_unknowns": {
            "prior_state": "none", "target_state": "clear",
            "constraints": "none", "target_depth": "functional",
        },
        "nodes": {"topic-a": {"state": "completed", "prerequisites": []}},
    }
    (goals_dir / "test-goal.yaml").write_text(yaml.safe_dump(goal), encoding="utf-8")

    # Profile: topic-a seen 10 days ago, stability=30 (long half-life → fresher)
    profile = {
        "schema_version": 0,
        "learner_id": "alice",
        "expertise_map": {
            "topic-a": {
                "mastery": "solid", "confidence": 0.8,
                "last_seen": "2026-04-10T00:00:00Z",
                "attempts": 5, "correct": 4,
                "stability": 30.0,
            },
        },
    }
    prof_path = tmp_path / "profile.yaml"
    prof_path.write_text(yaml.safe_dump(profile), encoding="utf-8")

    now = datetime(2026, 4, 20, tzinfo=timezone.utc)
    # With stability=30, freshness = 2^(-10/30) ≈ 0.79 → above 0.5 threshold → excluded
    result = schedule_reviews(goals_dir, prof_path, now=now)
    assert result == [], "High stability should keep topic fresh (above stale threshold)"


# --- FIX 11: _do_skip rejects terminal states ---


def test_skip_rejects_completed_node(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A completed node cannot be skipped — it is already terminal."""
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc, out = _run(cur, "skip", "A", capsys)
    assert rc == 1
    assert out["valid"] is False
    data = yaml.safe_load(cur.read_text())
    assert data["nodes"]["A"]["state"] == "completed"


def test_skip_rejects_decomposed_node(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A decomposed node cannot be skipped — it is already terminal."""
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "decomposed", "prerequisites": []},
    })
    rc, out = _run(cur, "skip", "A", capsys)
    assert rc == 1
    assert out["valid"] is False
    data = yaml.safe_load(cur.read_text())
    assert data["nodes"]["A"]["state"] == "decomposed"


def test_skip_rejects_already_skipped(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """An already-skipped node cannot be skipped again."""
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "skipped", "prerequisites": []},
    })
    rc, out = _run(cur, "skip", "A", capsys)
    assert rc == 1
    assert out["valid"] is False
    data = yaml.safe_load(cur.read_text())
    assert data["nodes"]["A"]["state"] == "skipped"


# --- FIX 22: _do_decompose rejects slug collisions ---


def test_decompose_rejects_slug_collision(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Decomposing A with a subgraph that contains a node named B must be
    rejected when B already exists in the graph."""
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "pending", "prerequisites": []},
        "B": {"state": "pending", "prerequisites": ["A"]},
    })
    subgraph = {"nodes": {
        "B": {"prerequisites": []},  # collides with existing B
        "A1": {"prerequisites": ["B"]},
    }}
    rc, out = _run(cur, "decompose", "A", capsys, subgraph=subgraph)
    assert rc == 1
    assert out["valid"] is False
    # Original node B must be unchanged.
    data = yaml.safe_load(cur.read_text())
    assert data["nodes"]["B"]["state"] == "pending"
    assert data["nodes"]["B"]["prerequisites"] == ["A"]
