"""Tests for scripts/config.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from sensei.engine.scripts.config import (
    ConfigValidationError,
    _deep_merge,
    load_config,
)

_REAL_ENGINE = Path(__file__).resolve().parents[2] / "src" / "sensei" / "engine"


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


# -------- ADR-0025: runtime config validation hard-fails by default --------


def test_real_engine_defaults_with_no_override_validate(tmp_path: Path) -> None:
    """Empty learner override on real engine defaults must validate cleanly."""
    instance = tmp_path / "instance"
    instance.mkdir()
    result = load_config(_REAL_ENGINE, instance)
    assert "memory" in result
    assert "half_life_days" in result["memory"]


def test_non_dict_section_override_raises_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A non-mapping overlay over a mapping default is whole-key-replaced
    by `_deep_merge`, surfacing as a schema type error at load time."""
    monkeypatch.delenv("SENSEI_CONFIG_SOFT_FAIL", raising=False)
    instance = tmp_path / "instance"
    _write_yaml(instance / "learner" / "config.yaml", "memory: 5\n")
    with pytest.raises(ConfigValidationError, match="memory"):
        load_config(_REAL_ENGINE, instance)


def test_type_error_override_raises_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SENSEI_CONFIG_SOFT_FAIL", raising=False)
    instance = tmp_path / "instance"
    _write_yaml(
        instance / "learner" / "config.yaml",
        "memory:\n  half_life_days: 'seven'\n  stale_threshold: 0.5\n",
    )
    with pytest.raises(ConfigValidationError, match="half_life_days"):
        load_config(_REAL_ENGINE, instance)


def test_unknown_top_level_key_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SENSEI_CONFIG_SOFT_FAIL", raising=False)
    instance = tmp_path / "instance"
    _write_yaml(instance / "learner" / "config.yaml", "totally_unknown_key: 1\n")
    with pytest.raises(ConfigValidationError):
        load_config(_REAL_ENGINE, instance)


def test_soft_fail_env_returns_merged_and_warns(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("SENSEI_CONFIG_SOFT_FAIL", "1")
    instance = tmp_path / "instance"
    _write_yaml(instance / "learner" / "config.yaml", "memory: 5\n")
    result = load_config(_REAL_ENGINE, instance)
    assert isinstance(result, dict)
    assert result["memory"] == 5  # whole-key replace happened despite invalidity
    captured = capsys.readouterr()
    assert "WARN: config:" in captured.err
    assert "memory" in captured.err


def test_soft_fail_env_only_triggers_on_exact_value_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Truthy strings other than the literal '1' must NOT downgrade the gate."""
    monkeypatch.setenv("SENSEI_CONFIG_SOFT_FAIL", "true")
    instance = tmp_path / "instance"
    _write_yaml(instance / "learner" / "config.yaml", "memory: 5\n")
    with pytest.raises(ConfigValidationError):
        load_config(_REAL_ENGINE, instance)


def test_soft_fail_with_clean_config_does_not_emit_warnings(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("SENSEI_CONFIG_SOFT_FAIL", "1")
    instance = tmp_path / "instance"
    instance.mkdir()
    load_config(_REAL_ENGINE, instance)
    captured = capsys.readouterr()
    assert "WARN" not in captured.err
