"""Integration test — end-to-end curriculum lifecycle."""

import json
import subprocess
import sys

import yaml

PYTHON = sys.executable
FRONTIER = "src/sensei/engine/scripts/frontier.py"
MUTATE = "src/sensei/engine/scripts/mutate_graph.py"


def _frontier(cur):
    r = subprocess.run([PYTHON, FRONTIER, "--curriculum", str(cur)], capture_output=True, text=True)
    return r, json.loads(r.stdout)


def _mutate(cur, op, node, **kwargs):
    cmd = [PYTHON, MUTATE, "--curriculum", str(cur), "--operation", op, "--node", node]
    if "prerequisites" in kwargs:
        cmd += ["--prerequisites", ",".join(kwargs["prerequisites"])]
    if "subgraph" in kwargs:
        cmd += ["--subgraph", json.dumps(kwargs["subgraph"])]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r, json.loads(r.stdout)


def test_linear_chain_lifecycle(tmp_path):
    """Walk a linear chain A→B→C→D→E with activate, complete, collapse, spawn."""
    cur = tmp_path / "curriculum.yaml"
    cur.write_text(yaml.safe_dump({"nodes": {
        "A": {"state": "spawned", "prerequisites": []},
        "B": {"state": "spawned", "prerequisites": ["A"]},
        "C": {"state": "spawned", "prerequisites": ["B"]},
        "D": {"state": "spawned", "prerequisites": ["C"]},
        "E": {"state": "spawned", "prerequisites": ["D"]},
    }}))

    # Step 1: frontier = [A]
    _, out = _frontier(cur)
    assert out["frontier"] == ["A"]

    # Step 2: activate A
    r, out = _mutate(cur, "activate", "A")
    assert r.returncode == 0 and out["valid"]

    # Step 3: complete A
    r, out = _mutate(cur, "complete", "A")
    assert r.returncode == 0 and out["valid"]

    # Step 4: frontier = [B]
    _, out = _frontier(cur)
    assert out["frontier"] == ["B"]

    # Step 5: collapse B
    r, out = _mutate(cur, "collapse", "B")
    assert r.returncode == 0 and out["valid"]

    # Step 6: frontier = [C]
    _, out = _frontier(cur)
    assert out["frontier"] == ["C"]

    # Step 7: spawn F with prereq C
    r, out = _mutate(cur, "spawn", "F", prerequisites=["C"])
    assert r.returncode == 0 and out["valid"]

    # Step 8: activate C
    r, out = _mutate(cur, "activate", "C")
    assert r.returncode == 0 and out["valid"]

    # Step 9: complete C
    r, out = _mutate(cur, "complete", "C")
    assert r.returncode == 0 and out["valid"]

    # Step 10: frontier contains both D and F
    _, out = _frontier(cur)
    assert set(out["frontier"]) == {"D", "F"}
