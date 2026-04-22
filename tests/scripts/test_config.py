"""Tests for scripts/config.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from sensei.engine.scripts.config import _deep_merge, load_config


def _write_yaml(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_load_config_valid(tmp_path: Path) -> None:
    engine = tmp_path / "engine"
    engine.mkdir()
    _write_yaml(engine / "defaults.yaml", "a: 1\nb: 2\n")
    instance = tmp_path / "root"
    _write_yaml(instance / "learner" / "config.yaml", "b: 99\nc: 3\n")

    result = load_config(engine, instance)
    assert result == {"a": 1, "b": 99, "c": 3}


def test_load_config_missing_override(tmp_path: Path) -> None:
    engine = tmp_path / "engine"
    engine.mkdir()
    _write_yaml(engine / "defaults.yaml", "x: 10\n")
    instance = tmp_path / "root"
    instance.mkdir()

    result = load_config(engine, instance)
    assert result == {"x": 10}


def test_load_config_invalid_yaml(tmp_path: Path) -> None:
    engine = tmp_path / "engine"
    engine.mkdir()
    _write_yaml(engine / "defaults.yaml", "{{{")

    with pytest.raises(ValueError, match="Invalid YAML"):
        load_config(engine, tmp_path)


def test_load_config_non_dict_yaml(tmp_path: Path) -> None:
    engine = tmp_path / "engine"
    engine.mkdir()
    _write_yaml(engine / "defaults.yaml", "- a list\n")

    with pytest.raises(ValueError, match="Expected a mapping"):
        load_config(engine, tmp_path)


def test_deep_merge_nested() -> None:
    base = {"top": {"a": 1, "b": 2}, "other": "x"}
    overlay = {"top": {"b": 99, "c": 3}}
    result = _deep_merge(base, overlay)
    assert result == {"top": {"a": 1, "b": 99, "c": 3}, "other": "x"}
