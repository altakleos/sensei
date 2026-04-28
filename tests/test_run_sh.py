"""Tests for run.sh security hardening: script allowlist and .python_path validation."""

from __future__ import annotations

import stat
import subprocess
from pathlib import Path

import pytest

from sensei.cli import _engine_source


@pytest.fixture()
def run_sh(tmp_path: Path) -> Path:
    """Set up a minimal engine directory with run.sh and a dummy script."""
    engine = tmp_path / ".sensei"
    scripts = engine / "scripts"
    scripts.mkdir(parents=True)

    # Copy the real run.sh from the engine source.
    src_run = _engine_source() / "run.sh"
    run = engine / "run"
    run.write_text(src_run.read_text(encoding="utf-8"), encoding="utf-8")
    run.chmod(run.stat().st_mode | stat.S_IEXEC)

    # Create a dummy decay.py script (on the allowlist).
    (scripts / "decay.py").write_text(
        'import sys, json; print(json.dumps({"ok": True})); sys.exit(0)\n',
        encoding="utf-8",
    )

    # Point .python_path at the current interpreter.
    import sys

    (engine / ".python_path").write_text(sys.executable + "\n", encoding="utf-8")

    return run


def test_run_sh_allows_valid_script(run_sh: Path) -> None:
    result = subprocess.run(
        [str(run_sh), "decay.py"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert '"ok"' in result.stdout


def test_run_sh_rejects_unknown_script(run_sh: Path) -> None:
    result = subprocess.run(
        [str(run_sh), "evil.py"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode != 0
    assert "unknown script" in result.stderr.lower()


def test_run_sh_rejects_path_traversal(run_sh: Path) -> None:
    result = subprocess.run(
        [str(run_sh), "../../../etc/passwd"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode != 0
    assert "unknown script" in result.stderr.lower()


def test_run_sh_rejects_relative_python_path(run_sh: Path) -> None:
    python_path_file = run_sh.parent / ".python_path"
    python_path_file.write_text("python3\n", encoding="utf-8")

    result = subprocess.run(
        [str(run_sh), "decay.py"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode != 0
    assert "absolute path" in result.stderr.lower()
