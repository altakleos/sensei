"""Config loader: deep-merge engine defaults with instance overrides."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in overlay.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data or {}


def load_config(engine_root: Path, instance_root: Path) -> dict[str, Any]:
    """Load engine defaults and merge instance overrides on top.

    engine_root: path to the engine directory (contains defaults.yaml).
    instance_root: path to the instance directory (may contain instance/config.yaml).
    """
    defaults = _load_yaml(engine_root / "defaults.yaml")
    overrides = _load_yaml(instance_root / "instance" / "config.yaml")
    return _deep_merge(defaults, overrides)
