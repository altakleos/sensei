"""End-to-end smoke test exercising the full Sensei pipeline."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

PYTHON = sys.executable
SENSEI = shutil.which("sensei") or str(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "sensei")
SCRIPTS = str(Path(__file__).resolve().parents[1] / "src" / "sensei" / "engine" / "scripts")


def _run(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, **kwargs)


def test_full_pipeline(tmp_path: Path) -> None:
    """Walk through: init → hint drop → hint_decay → frontier → graph mutations."""

    # 1. sensei init
    instance = tmp_path / "test-instance"
    r = _run([SENSEI, "init", str(instance)])
    assert r.returncode == 0, r.stderr

    # 2. Verify scaffolded structure
    assert (instance / "instance" / "inbox").is_dir()
    assert (instance / "instance" / "hints" / "active").is_dir()
    assert (instance / "instance" / "hints" / "archive").is_dir()
    assert (instance / "instance" / "hints" / "hints.yaml").is_file()

    # 3. Drop a hint file into inbox
    hint_file = instance / "instance" / "inbox" / "rust-ownership.md"
    hint_file.write_text(
        "---\n"
        "date: 2026-04-20\n"
        "source_url: https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html\n"
        "channel: web\n"
        "tags: [rust, ownership, memory]\n"
        "---\n\n"
        "Rust ownership rules are fundamental to memory safety.\n",
        encoding="utf-8",
    )
    assert hint_file.exists()

    # 4. Run hint_decay on the empty hints.yaml (should succeed with empty list)
    hints_yaml = instance / "instance" / "hints" / "hints.yaml"
    r = _run([
        PYTHON, f"{SCRIPTS}/hint_decay.py",
        "--hints-file", str(hints_yaml),
        "--half-life-days", "14",
        "--expire-threshold", "0.2",
        "--expire-after-days", "28",
    ])
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout) == []

    # 5. Create curriculum.yaml with 3 nodes: A (no prereqs), B→A, C→B
    goal_dir = instance / "instance" / "goals" / "rust-basics"
    goal_dir.mkdir(parents=True)
    curriculum = goal_dir / "curriculum.yaml"
    curriculum.write_text(yaml.safe_dump({
        "nodes": {
            "A": {"state": "pending", "prerequisites": []},
            "B": {"state": "pending", "prerequisites": ["A"]},
            "C": {"state": "pending", "prerequisites": ["B"]},
        }
    }, default_flow_style=False, sort_keys=False), encoding="utf-8")

    # 6. frontier.py → frontier should be [A]
    r = _run([PYTHON, f"{SCRIPTS}/frontier.py", "--curriculum", str(curriculum)])
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["frontier"] == ["A"]

    # 7. mutate_graph: activate A
    r = _run([
        PYTHON, f"{SCRIPTS}/mutate_graph.py",
        "--curriculum", str(curriculum),
        "--operation", "activate",
        "--node", "A",
    ])
    assert r.returncode == 0, r.stderr
    result = json.loads(r.stdout)
    assert result["valid"] is True
    assert result["new_state"] == "active"

    # 8. mutate_graph: complete A
    r = _run([
        PYTHON, f"{SCRIPTS}/mutate_graph.py",
        "--curriculum", str(curriculum),
        "--operation", "complete",
        "--node", "A",
    ])
    assert r.returncode == 0, r.stderr
    result = json.loads(r.stdout)
    assert result["valid"] is True
    assert result["new_state"] == "completed"

    # 9. frontier.py → frontier should now be [B]
    r = _run([PYTHON, f"{SCRIPTS}/frontier.py", "--curriculum", str(curriculum)])
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["frontier"] == ["B"]

    # 10. hint_decay with one active hint ingested today → freshness = 1.0
    now = datetime.now(tz=timezone.utc).isoformat()
    decay_hints = tmp_path / "decay_hints.yaml"
    decay_hints.write_text(yaml.safe_dump({
        "schema_version": 1,
        "hints": [{
            "id": "hint-001",
            "status": "active",
            "ingested": now,
            "topics": ["rust-ownership"],
            "relevance": 0.9,
        }],
    }, default_flow_style=False, sort_keys=False), encoding="utf-8")

    r = _run([
        PYTHON, f"{SCRIPTS}/hint_decay.py",
        "--hints-file", str(decay_hints),
        "--half-life-days", "14",
        "--expire-threshold", "0.2",
        "--expire-after-days", "28",
        "--now", now,
    ])
    assert r.returncode == 0, r.stderr
    updated = json.loads(r.stdout)
    assert len(updated) == 1
    assert updated[0]["freshness"] == 1.0
    assert updated[0]["status"] == "active"
