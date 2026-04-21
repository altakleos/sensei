"""Tests for the atomic_write_text helper."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from sensei.engine.scripts._atomic import atomic_write_text


def test_happy_path(tmp_path: Path) -> None:
    """atomic_write_text produces the expected content on the target path."""
    target = tmp_path / "profile.yaml"
    atomic_write_text(target, "key: value\n")
    assert target.read_text(encoding="utf-8") == "key: value\n"


def test_no_tmp_left_after_success(tmp_path: Path) -> None:
    """No .tmp file is left behind after a successful write."""
    target = tmp_path / "profile.yaml"
    atomic_write_text(target, "key: value\n")
    tmp = target.with_suffix(target.suffix + ".tmp")
    assert not tmp.exists()


def test_crash_on_replace_leaves_original_untouched(tmp_path: Path) -> None:
    """If os.replace raises, the original file is untouched and the tmp file is removed."""
    target = tmp_path / "profile.yaml"
    original_content = "original: true\n"
    target.write_text(original_content, encoding="utf-8")

    with (
        patch("sensei.engine.scripts._atomic.os.replace", side_effect=OSError("disk full")),
        pytest.raises(OSError, match="disk full"),
    ):
        atomic_write_text(target, "new: content\n")

    # Original file is intact
    assert target.read_text(encoding="utf-8") == original_content
    # Tmp file is cleaned up
    tmp = target.with_suffix(target.suffix + ".tmp")
    assert not tmp.exists()


def test_crash_on_fsync_leaves_original_untouched(tmp_path: Path) -> None:
    """If os.fsync raises mid-write (after data is buffered but before rename),
    the original file is untouched AND the tmp file is cleaned up."""
    target = tmp_path / "profile.yaml"
    original_content = "original: true\n"
    target.write_text(original_content, encoding="utf-8")

    with (
        patch("sensei.engine.scripts._atomic.os.fsync", side_effect=OSError("fsync failed")),
        pytest.raises(OSError, match="fsync failed"),
    ):
        atomic_write_text(target, "new: content\n")

    # Original file is intact
    assert target.read_text(encoding="utf-8") == original_content
    # Tmp file is cleaned up
    tmp = target.with_suffix(target.suffix + ".tmp")
    assert not tmp.exists()


def test_large_content(tmp_path: Path) -> None:
    """fsync path handles multi-KB content without truncation."""
    target = tmp_path / "profile.yaml"
    # 50 KB of content
    content = "line: " + "x" * 100 + "\n"
    large_content = content * 500
    atomic_write_text(target, large_content)
    assert target.read_text(encoding="utf-8") == large_content


def test_overwrites_existing_file(tmp_path: Path) -> None:
    """atomic_write_text overwrites an existing file atomically."""
    target = tmp_path / "profile.yaml"
    target.write_text("old: data\n", encoding="utf-8")
    atomic_write_text(target, "new: data\n")
    assert target.read_text(encoding="utf-8") == "new: data\n"
