import sys
"""Tests for mutate_graph.py — validated state transitions."""
import json
import subprocess
from pathlib import Path

import yaml

PYTHON = sys.executable
SCRIPT = "src/sensei/engine/scripts/mutate_graph.py"


def _run(curriculum_path, operation, node, prerequisites=None, subgraph=None):
    cmd = [PYTHON, SCRIPT, "--curriculum", str(curriculum_path),
           "--operation", operation, "--node", node]
    if prerequisites:
        cmd += ["--prerequisites", ",".join(prerequisites)]
    if subgraph:
        cmd += ["--subgraph", json.dumps(subgraph)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result, json.loads(result.stdout)


def _make_curriculum(tmp_path, nodes):
    cur = tmp_path / "curriculum.yaml"
    cur.write_text(yaml.safe_dump({"nodes": nodes}))
    return cur


def test_activate_success(tmp_path):
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "spawned", "prerequisites": ["A"]},
    })
    result, out = _run(cur, "activate", "B")
    assert result.returncode == 0
    assert out["valid"] is True
    assert out["new_state"] == "active"


def test_activate_fails_already_active(tmp_path):
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "active", "prerequisites": ["A"]},
        "C": {"state": "spawned", "prerequisites": ["A"]},
    })
    result, out = _run(cur, "activate", "C")
    assert result.returncode == 1
    assert out["valid"] is False


def test_activate_fails_not_on_frontier(tmp_path):
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "spawned", "prerequisites": []},
        "B": {"state": "spawned", "prerequisites": ["A"]},
    })
    result, out = _run(cur, "activate", "B")
    assert result.returncode == 1
    assert out["valid"] is False


def test_complete_success(tmp_path):
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "active", "prerequisites": []},
    })
    result, out = _run(cur, "complete", "A")
    assert result.returncode == 0
    assert out["new_state"] == "completed"


def test_complete_fails_not_active(tmp_path):
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "spawned", "prerequisites": []},
    })
    result, out = _run(cur, "complete", "A")
    assert result.returncode == 1
    assert out["valid"] is False


def test_collapse_success(tmp_path):
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "spawned", "prerequisites": ["A"]},
    })
    result, out = _run(cur, "collapse", "B")
    assert result.returncode == 0
    assert out["new_state"] == "collapsed"
    # Verify dependents are unblocked (B collapsed counts as done)
    data = yaml.safe_load(cur.read_text())
    assert data["nodes"]["B"]["state"] == "collapsed"


def test_spawn_success(tmp_path):
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    result, out = _run(cur, "spawn", "B", prerequisites=["A"])
    assert result.returncode == 0
    assert out["new_state"] == "spawned"
    data = yaml.safe_load(cur.read_text())
    assert "B" in data["nodes"]
    assert data["nodes"]["B"]["prerequisites"] == ["A"]


def test_spawn_fails_cycle(tmp_path):
    """Spawning a node that creates a cycle → exit 2."""
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "spawned", "prerequisites": ["B"]},
        "B": {"state": "spawned", "prerequisites": []},
    })
    # Spawn C with prereq A, then make A depend on C indirectly
    # Actually: spawn C depending on A, where A depends on B — no cycle.
    # For a real cycle: A→B, spawn C with prereq A, then we need B→C somehow.
    # Simplest: A depends on B, B depends on nothing. Spawn C with prereq A.
    # Then make A depend on C? Can't with spawn.
    # Real cycle: A→B (A depends on B). Spawn C with prereq=[A].
    # Then nodes: A→B, C→A. No cycle.
    # For cycle: B depends on C, C depends on A, A depends on B.
    # Setup: A depends on B, B has no prereqs. Spawn C with prereqs=[A].
    # Result: A→B, C→A. Still no cycle.
    # Need: A→B→C→A. Start with A(prereqs=[B]), B(prereqs=[]).
    # Spawn C with prereqs=[B]. Now A→B, C→B. No cycle.
    # Start with A(prereqs=[B]), B(prereqs=[C_future])... can't.
    # Correct approach: A depends on B. Spawn C with prereqs that create cycle.
    # A(prereqs=[B]), B(prereqs=[]). Spawn C(prereqs=[A]).
    # Then graph: B←A←C. No cycle.
    # For actual cycle we need existing circular potential:
    # A(prereqs=[B]), B(prereqs=[A]) — already a cycle! Can't start there.
    # Let's do: A(no prereqs), B(prereqs=[A]). Spawn C(prereqs=[B]),
    # but also make B depend on C? Can't with spawn alone.
    # The only way spawn creates a cycle: if the new node's prereqs
    # form a cycle with existing edges. E.g., A(prereqs=[B]), B(prereqs=[]).
    # Spawn C(prereqs=[B]) — no cycle. 
    # Actually impossible to create cycle with spawn alone since new node
    # only adds incoming edges (prereqs). Need existing node pointing to new node.
    # That can't happen since new node didn't exist before.
    # So spawn alone can't create a cycle. Let's test with expand instead
    # or accept this is an edge case that won't trigger exit 2 via spawn.
    # Per the code: _has_cycle checks after mutation. We can craft it by
    # having an existing node that somehow references the new slug already.
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "spawned", "prerequisites": ["B"]},
        "B": {"state": "spawned", "prerequisites": []},
    })
    # Manually inject a forward reference: A depends on B, B depends on C (not yet existing)
    data = yaml.safe_load(cur.read_text())
    data["nodes"]["B"]["prerequisites"] = ["C"]
    # Now A→B→C. If we spawn C with prereqs=[A], we get C→A→B→C = cycle
    cur.write_text(yaml.safe_dump(data))
    result, out = _run(cur, "spawn", "C", prerequisites=["A"])
    assert result.returncode == 2
    assert out["valid"] is False
    assert "cycle" in out["error"]


def test_spawn_fails_missing_prerequisite(tmp_path):
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
    })
    result, out = _run(cur, "spawn", "B", prerequisites=["X"])
    assert result.returncode == 1
    assert out["valid"] is False


def test_expand_success(tmp_path):
    cur = _make_curriculum(tmp_path, {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "spawned", "prerequisites": ["A"]},
        "C": {"state": "spawned", "prerequisites": ["B"]},
    })
    subgraph = {"nodes": {
        "B1": {"prerequisites": ["A"]},
        "B2": {"prerequisites": ["B1"]},
    }}
    result, out = _run(cur, "expand", "B", subgraph=subgraph)
    assert result.returncode == 0
    assert out["new_state"] == "expanded"
    data = yaml.safe_load(cur.read_text())
    assert "B1" in data["nodes"]
    assert "B2" in data["nodes"]
    # C should now depend on B2 (leaf of subgraph) instead of B
    assert "B2" in data["nodes"]["C"]["prerequisites"]
    assert "B" not in data["nodes"]["C"]["prerequisites"]
