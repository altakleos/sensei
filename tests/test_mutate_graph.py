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
        "B": {"state": "spawned", "prerequisites": ["A"]},
    })
    rc, out = _run(cur, "activate", "B", capsys)
    assert rc == 0
    assert out["valid"] is True
    assert out["new_state"] == "active"


def test_activate_fails_already_active(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "active", "prerequisites": ["A"]},
        "C": {"state": "spawned", "prerequisites": ["A"]},
    })
    rc, out = _run(cur, "activate", "C", capsys)
    assert rc == 1
    assert out["valid"] is False


def test_activate_fails_not_on_frontier(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "spawned", "prerequisites": []},
        "B": {"state": "spawned", "prerequisites": ["A"]},
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
        "A": {"state": "spawned", "prerequisites": []},
    })
    rc, out = _run(cur, "complete", "A", capsys)
    assert rc == 1
    assert out["valid"] is False


def test_collapse_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "spawned", "prerequisites": ["A"]},
    })
    rc, out = _run(cur, "collapse", "B", capsys)
    assert rc == 0
    assert out["new_state"] == "collapsed"
    # On-disk state reflects the collapse (dependents would now see B as done).
    data = yaml.safe_load(cur.read_text())
    assert data["nodes"]["B"]["state"] == "collapsed"


def test_spawn_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc, out = _run(cur, "spawn", "B", capsys, prerequisites=["A"])
    assert rc == 0
    assert out["new_state"] == "spawned"
    data = yaml.safe_load(cur.read_text())
    assert "B" in data["nodes"]
    assert data["nodes"]["B"]["prerequisites"] == ["A"]


def test_spawn_fails_cycle(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Constructing a cycle via spawn requires priming the graph with a forward
    reference first: A→B→C (where C doesn't exist yet), then spawn C→A closes
    the loop A→B→C→A. `_has_cycle` rejects the mutation with exit 2."""
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "spawned", "prerequisites": ["B"]},
        "B": {"state": "spawned", "prerequisites": []},
    })
    data = yaml.safe_load(cur.read_text())
    data["nodes"]["B"]["prerequisites"] = ["C"]
    cur.write_text(yaml.safe_dump(data), encoding="utf-8")
    rc, out = _run(cur, "spawn", "C", capsys, prerequisites=["A"])
    assert rc == 2
    assert out["valid"] is False
    assert "cycle" in out["error"]


def test_spawn_fails_missing_prerequisite(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc, out = _run(cur, "spawn", "B", capsys, prerequisites=["X"])
    assert rc == 1
    assert out["valid"] is False


def test_expand_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "spawned", "prerequisites": ["A"]},
        "C": {"state": "spawned", "prerequisites": ["B"]},
    })
    subgraph = {"nodes": {
        "B1": {"prerequisites": ["A"]},
        "B2": {"prerequisites": ["B1"]},
    }}
    rc, out = _run(cur, "expand", "B", capsys, subgraph=subgraph)
    assert rc == 0
    assert out["new_state"] == "expanded"
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
    cur = _make_curriculum(tmp_path, {"A": {"state": "spawned", "prerequisites": []}})
    with pytest.raises(SystemExit):
        # argparse choices rejection exits the process before main returns.
        main(["--curriculum", str(cur), "--operation", "destroy", "--node", "A"])


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    """Smoke test: protocols invoke this helper via subprocess (per ADR-0006). Verify that path works."""
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "spawned", "prerequisites": ["A"]},
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


# --- Coverage: _do_collapse node not in nodes (line 115) ---


def test_collapse_fails_nonexistent_node(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc, out = _run(cur, "collapse", "Z", capsys)
    assert rc == 1
    assert "does not exist" in out["error"]


# --- Coverage: _do_spawn node already exists (line 124) ---


def test_spawn_fails_node_already_exists(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc, out = _run(cur, "spawn", "A", capsys, prerequisites=["A"])
    assert rc == 1
    assert "already exists" in out["error"]


# --- Coverage: _do_spawn no prerequisites (line 126) ---


def test_spawn_fails_no_prerequisites(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc = main(["--curriculum", str(cur), "--operation", "spawn", "--node", "B"])
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert "prerequisites required" in out["error"]


# --- Coverage: _do_expand node not in nodes (line 138) ---


def test_expand_fails_nonexistent_node(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    subgraph = {"nodes": {"X": {"prerequisites": []}}}
    rc, out = _run(cur, "expand", "Z", capsys, subgraph=subgraph)
    assert rc == 1
    assert "does not exist" in out["error"]


# --- Coverage: _do_expand no subgraph (line 140) ---


def test_expand_fails_no_subgraph(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    rc = main(["--curriculum", str(cur), "--operation", "expand", "--node", "A"])
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert "subgraph required" in out["error"]


# --- Coverage: mutate() unknown op (line 184) — not reachable via CLI due to argparse choices,
#     but exercised via direct mutate() call ---

from sensei.engine.scripts.mutate_graph import mutate


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
    rc = main(["--curriculum", str(cur), "--operation", "expand", "--node", "A",
               "--subgraph", "{bad json}"])
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert "invalid subgraph JSON" in out["error"]
