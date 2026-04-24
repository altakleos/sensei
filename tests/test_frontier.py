"""Tests for frontier.py — curriculum DAG frontier computation.

Calls `frontier.main(argv)` directly so pytest-cov can observe the code paths.
One subprocess smoke test at the end verifies the CLI entry point still runs
as a separate process (how protocols actually invoke it per ADR-0006).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from sensei.engine.scripts.frontier import main


def _write_curriculum(tmp_path: Path, nodes: dict) -> Path:
    cur = tmp_path / "curriculum.yaml"
    cur.write_text(yaml.safe_dump({"nodes": nodes}), encoding="utf-8")
    return cur


def _run(
    tmp_path: Path,
    nodes: dict,
    capsys: pytest.CaptureFixture[str],
    hints: list | None = None,
) -> tuple[int, dict]:
    cur = _write_curriculum(tmp_path, nodes)
    argv = ["--curriculum", str(cur)]
    if hints is not None:
        hints_path = tmp_path / "hints.yaml"
        hints_path.write_text(yaml.safe_dump({"hints": hints}), encoding="utf-8")
        argv += ["--hints", str(hints_path)]
    rc = main(argv)
    out = capsys.readouterr().out
    return rc, json.loads(out)


def test_simple_frontier(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A completed, B and C depend on A → frontier = [B, C]."""
    rc, out = _run(
        tmp_path,
        {
            "A": {"state": "completed", "prerequisites": []},
            "B": {"state": "pending", "prerequisites": ["A"]},
            "C": {"state": "pending", "prerequisites": ["A"]},
        },
        capsys,
    )
    assert rc == 0
    assert set(out["frontier"]) == {"B", "C"}
    assert out["total_nodes"] == 3


def test_no_frontier(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """All nodes completed or skipped → empty frontier."""
    _, out = _run(
        tmp_path,
        {
            "A": {"state": "completed", "prerequisites": []},
            "B": {"state": "skipped", "prerequisites": ["A"]},
        },
        capsys,
    )
    assert out["frontier"] == []


def test_active_blocks_frontier(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Active node doesn't remove other nodes from frontier."""
    _, out = _run(
        tmp_path,
        {
            "A": {"state": "completed", "prerequisites": []},
            "B": {"state": "active", "prerequisites": ["A"]},
            "C": {"state": "pending", "prerequisites": ["A"]},
        },
        capsys,
    )
    assert out["frontier"] == ["C"]
    assert out["active"] == "B"


def test_prerequisite_not_met(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Node with non-completed prereq is not on frontier."""
    _, out = _run(
        tmp_path,
        {
            "A": {"state": "pending", "prerequisites": []},
            "B": {"state": "pending", "prerequisites": ["A"]},
        },
        capsys,
    )
    assert out["frontier"] == ["A"]


def test_hints_boost_ordering(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Hints boost moves a later node to front of frontier."""
    _, out = _run(
        tmp_path,
        {
            "A": {"state": "completed", "prerequisites": []},
            "B": {"state": "pending", "prerequisites": ["A"]},
            "C": {"state": "pending", "prerequisites": ["A"]},
        },
        capsys,
        hints=[{"status": "active", "relevance": 1.0, "freshness": 1.0, "topics": ["C"]}],
    )
    assert out["frontier"][0] == "C"


def test_empty_curriculum(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """No nodes → empty frontier."""
    _, out = _run(tmp_path, {}, capsys)
    assert out["frontier"] == []
    assert out["total_nodes"] == 0


def test_pending_node_on_frontier(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Pending node with all prereqs met (mix of completed and skipped) appears on frontier."""
    _, out = _run(
        tmp_path,
        {
            "A": {"state": "completed", "prerequisites": []},
            "B": {"state": "skipped", "prerequisites": []},
            "C": {"state": "pending", "prerequisites": ["A", "B"]},
        },
        capsys,
    )
    assert out["frontier"] == ["C"]


def test_missing_curriculum_file_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--curriculum", str(tmp_path / "missing.yaml")])
    assert rc == 1
    assert "not found" in json.loads(capsys.readouterr().out)["error"]


def test_corrupt_curriculum_yaml_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = tmp_path / "bad.yaml"
    cur.write_text("{{{", encoding="utf-8")
    rc = main(["--curriculum", str(cur)])
    assert rc == 1
    assert "yaml parse error" in json.loads(capsys.readouterr().out)["error"]


def test_non_mapping_curriculum_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = tmp_path / "list.yaml"
    cur.write_text("- just\n- a\n- list\n", encoding="utf-8")
    rc = main(["--curriculum", str(cur)])
    assert rc == 1
    assert "nodes" in json.loads(capsys.readouterr().out)["error"]


def test_missing_hints_file_returns_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cur = _write_curriculum(tmp_path, {"A": {"state": "pending", "prerequisites": []}})
    rc = main(["--curriculum", str(cur), "--hints", str(tmp_path / "missing-hints.yaml")])
    assert rc == 1


def test_script_runs_as_subprocess(tmp_path: Path) -> None:
    """Smoke test: protocols invoke this helper via subprocess (per ADR-0006). Verify that path works."""
    cur = _write_curriculum(tmp_path, {"A": {"state": "pending", "prerequisites": []}})
    script = Path(__file__).resolve().parent.parent / "src" / "sensei" / "engine" / "scripts" / "frontier.py"
    assert script.is_file(), f"script path wrong: {script}"
    result = subprocess.run(
        [sys.executable, str(script), "--curriculum", str(cur)],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["frontier"] == ["A"]


def test_frontier_order_independent_of_yaml_key_order(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Frontier ordering must be deterministic on slug, not on YAML key layout.

    Before the fix, priority was assigned by `enumerate(nodes.items())` — so
    reordering keys in `curriculum.yaml` silently re-sequenced the frontier.
    Writing the file with a non-alphabetical key order exercises the
    difference between the old and new behaviours.
    """
    cur = tmp_path / "curriculum.yaml"
    # Non-alphabetical key order on disk — charlie, alpha, bravo.
    cur.write_text(
        "nodes:\n"
        "  charlie:\n"
        "    state: pending\n"
        "    prerequisites: []\n"
        "  alpha:\n"
        "    state: pending\n"
        "    prerequisites: []\n"
        "  bravo:\n"
        "    state: pending\n"
        "    prerequisites: []\n",
        encoding="utf-8",
    )
    rc = main(["--curriculum", str(cur)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    # Post-fix: alphabetical ordering regardless of file layout.
    assert out["frontier"] == ["alpha", "bravo", "charlie"]
