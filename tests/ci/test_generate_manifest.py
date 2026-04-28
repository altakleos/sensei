"""Tests for ci/generate_manifest.py."""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "ci" / "generate_manifest.py"
assert _SCRIPT_PATH.is_file(), f"script not found: {_SCRIPT_PATH}"


def _load_generator():
    spec = importlib.util.spec_from_file_location("generate_manifest", _SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


gen = _load_generator()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# -- _group_key tests --


def test_group_key_top_level() -> None:
    assert gen._group_key("AGENTS.md") == "."


def test_group_key_nested() -> None:
    assert gen._group_key("protocols/tutor.md") == "protocols"


def test_group_key_deeply_nested() -> None:
    assert gen._group_key("protocols/modes/assess.md") == "protocols/modes"


# -- _collect_files tests (against real engine dir) --


def test_collect_files_returns_entries() -> None:
    """_collect_files returns a non-empty sorted list of (rel_path, sha256) tuples."""
    entries = gen._collect_files()
    assert len(entries) > 0
    # Verify sorted
    paths = [e[0] for e in entries]
    assert paths == sorted(paths)


def test_collect_files_excludes_manifest_and_init() -> None:
    """Excluded files must not appear in collected entries."""
    entries = gen._collect_files()
    paths = {e[0] for e in entries}
    for excluded in ("__init__.py", "manifest.yaml", "run.sh"):
        assert excluded not in paths, f"{excluded} should be excluded"


def test_collect_files_checksums_are_correct() -> None:
    """Verify SHA-256 checksums match actual file contents."""
    engine_dir = gen._ENGINE_DIR
    for rel, digest in gen._collect_files():
        actual = hashlib.sha256((engine_dir / rel).read_bytes()).hexdigest()
        assert actual == digest, f"checksum mismatch for {rel}"


# -- generate() tests --


def test_generate_includes_all_collected_files() -> None:
    """Every file from _collect_files appears in the generated manifest text."""
    entries = gen._collect_files()
    output = gen.generate()
    for rel, digest in entries:
        assert f"path: {rel}" in output, f"{rel} missing from generated manifest"
        assert digest in output, f"checksum for {rel} missing from generated manifest"


def test_generate_is_deterministic() -> None:
    """Calling generate() twice produces identical output."""
    first = gen.generate()
    second = gen.generate()
    assert first == second


def test_generate_has_schema_version() -> None:
    output = gen.generate()
    assert "schema_version: 2" in output


def test_generate_has_required_section() -> None:
    output = gen.generate()
    assert "required:" in output
