"""Engine bundle management: install, upgrade, atomic swap."""

from __future__ import annotations

import os
import shutil
import stat
import sys
from pathlib import Path

import click

import sensei


def engine_source() -> Path:
    """Return a filesystem path to the bundled engine directory.

    The engine bundle is shipped inside the `sensei` package at `sensei/engine/`.
    It is a data directory of markdown, yaml, and helper scripts (with a
    minimal ``__init__.py`` for import-path setup) that ``sensei init``
    copies into ``.sensei/``.
    """
    package_root = Path(sensei.__file__).parent
    engine_dir = package_root / "engine"
    if not engine_dir.is_dir():
        raise click.ClickException(f"Engine bundle not found at {engine_dir}")
    return engine_dir


def fsync_dir(path: Path) -> None:
    """fsync *path* as a directory so recent rename dirents are durable.

    POSIX rename(2) only guarantees atomicity — not durability. Without an
    fsync on the containing directory, a power loss after rename() returns
    can lose the dirent update. No-op on non-POSIX.
    """
    if os.name != "posix":
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_replace_engine(src: Path, sensei_dir: Path, version: str) -> None:
    """Install or replace `sensei_dir` with a fresh copy of `src`, atomically.

    Honors the per-upgrade atomicity contract documented in ADR-0004 and
    `docs/operations/release-playbook.md`: the learner's existing `.sensei/`
    is preserved across any failure of the copy step, and is recoverable
    after a crash during the short swap window.

    Algorithm (platform-agnostic, three-step swap):
      1. Copy the engine bundle to a sibling `.sensei.tmp/`.
      2. If `.sensei/` exists, rename it aside to `.sensei.old/`.
      3. Rename `.sensei.tmp/` into place as `.sensei/`.
      4. Remove `.sensei.old/`.

    Each rename is followed by _fsync_dir on the parent so the dirent update
    survives power loss.

    Crash recovery: if a previous run died between steps 2 and 3, the next
    call (or any subsequent `sensei` command that invokes this helper) sees
    `.sensei.old/` present and `.sensei/` missing, and restores the old.
    Leftover `.sensei.tmp/` from a prior failed copy is always cleaned first.
    """
    parent = sensei_dir.parent
    tmp_dir = parent / ".sensei.tmp"
    old_dir = parent / ".sensei.old"

    # Crash recovery from a prior interrupted swap.
    if old_dir.exists() and not sensei_dir.exists():
        old_dir.rename(sensei_dir)
        fsync_dir(parent)
    elif old_dir.exists() and sensei_dir.exists():
        # Prior run completed the new install but died before cleanup.
        shutil.rmtree(old_dir)

    # Clean leftover temp from a prior failed copy.
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)

    # Step 1 — copy bundle to temp. Any failure here leaves `.sensei/` intact.
    try:
        shutil.copytree(src, tmp_dir)
        (tmp_dir / ".sensei-version").write_text(f"{version}\n", encoding="utf-8")
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    # Steps 2–3 — swap aside + install new.
    swapped_aside = False
    try:
        if sensei_dir.exists():
            sensei_dir.rename(old_dir)
            fsync_dir(parent)
            swapped_aside = True
        tmp_dir.rename(sensei_dir)
        fsync_dir(parent)
    except Exception:
        # Best-effort rollback: put the old dir back if we moved it.
        if swapped_aside and old_dir.exists() and not sensei_dir.exists():
            old_dir.rename(sensei_dir)
            fsync_dir(parent)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    # Step 4 — remove the aside. `.sensei/` is now authoritative.
    if old_dir.exists():
        shutil.rmtree(old_dir, ignore_errors=True)


def install_run_script(sensei_dir: Path) -> None:
    """Record the Python interpreter and make the run wrapper executable."""
    (sensei_dir / ".python_path").write_text(sys.executable + "\n", encoding="utf-8")
    run_script = sensei_dir / "run.sh"
    run_dest = sensei_dir / "run"
    if run_script.exists():
        run_script.rename(run_dest)
    if run_dest.exists():
        run_dest.chmod(run_dest.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
