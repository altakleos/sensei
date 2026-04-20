"""Tests for frontier.py — curriculum DAG frontier computation."""
import json
import subprocess
from pathlib import Path

import yaml

PYTHON = "/Users/santorob/dev/sensei/.venv/bin/python"
SCRIPT = "src/sensei/engine/scripts/frontier.py"


def _run(curriculum_path, hints_path=None):
    cmd = [PYTHON, SCRIPT, "--curriculum", str(curriculum_path)]
    if hints_path:
        cmd += ["--hints", str(hints_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result, json.loads(result.stdout)


def test_simple_frontier(tmp_path):
    """A completed, B and C depend on A → frontier = [B, C]."""
    cur = tmp_path / "curriculum.yaml"
    cur.write_text(yaml.safe_dump({"nodes": {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "spawned", "prerequisites": ["A"]},
        "C": {"state": "spawned", "prerequisites": ["A"]},
    }}))
    result, out = _run(cur)
    assert result.returncode == 0
    assert set(out["frontier"]) == {"B", "C"}
    assert out["total_nodes"] == 3


def test_no_frontier(tmp_path):
    """All nodes completed or collapsed → empty frontier."""
    cur = tmp_path / "curriculum.yaml"
    cur.write_text(yaml.safe_dump({"nodes": {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "collapsed", "prerequisites": ["A"]},
    }}))
    _, out = _run(cur)
    assert out["frontier"] == []


def test_active_blocks_frontier(tmp_path):
    """Active node doesn't remove other nodes from frontier."""
    cur = tmp_path / "curriculum.yaml"
    cur.write_text(yaml.safe_dump({"nodes": {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "active", "prerequisites": ["A"]},
        "C": {"state": "spawned", "prerequisites": ["A"]},
    }}))
    _, out = _run(cur)
    assert out["frontier"] == ["C"]
    assert out["active"] == "B"


def test_prerequisite_not_met(tmp_path):
    """Node with non-completed prereq is not on frontier."""
    cur = tmp_path / "curriculum.yaml"
    cur.write_text(yaml.safe_dump({"nodes": {
        "A": {"state": "spawned", "prerequisites": []},
        "B": {"state": "spawned", "prerequisites": ["A"]},
    }}))
    _, out = _run(cur)
    assert out["frontier"] == ["A"]


def test_hints_boost_ordering(tmp_path):
    """Hints boost moves a later node to front of frontier."""
    cur = tmp_path / "curriculum.yaml"
    cur.write_text(yaml.safe_dump({"nodes": {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "spawned", "prerequisites": ["A"]},
        "C": {"state": "spawned", "prerequisites": ["A"]},
    }}))
    hints = tmp_path / "hints.yaml"
    hints.write_text(yaml.safe_dump({"hints": [
        {"status": "active", "relevance": 1.0, "freshness": 1.0, "topics": ["C"]},
    ]}))
    _, out = _run(cur, hints)
    assert out["frontier"][0] == "C"


def test_empty_curriculum(tmp_path):
    """No nodes → empty frontier."""
    cur = tmp_path / "curriculum.yaml"
    cur.write_text(yaml.safe_dump({"nodes": {}}))
    _, out = _run(cur)
    assert out["frontier"] == []
    assert out["total_nodes"] == 0


def test_spawned_node_on_frontier(tmp_path):
    """Spawned node with all prereqs met appears on frontier."""
    cur = tmp_path / "curriculum.yaml"
    cur.write_text(yaml.safe_dump({"nodes": {
        "A": {"state": "completed", "prerequisites": []},
        "B": {"state": "collapsed", "prerequisites": []},
        "C": {"state": "spawned", "prerequisites": ["A", "B"]},
    }}))
    _, out = _run(cur)
    assert out["frontier"] == ["C"]
