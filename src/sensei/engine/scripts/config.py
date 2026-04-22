"""Config loader: deep-merge engine defaults with learner overrides."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: Missing 'pyyaml'. Install with: pip install sensei-tutor", file=sys.stderr)
    sys.exit(1)


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
        try:
            data = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML in {path}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected a mapping in {path}, got {type(data).__name__}")
    return data


def load_config(engine_root: Path, instance_root: Path) -> dict[str, Any]:
    """Load engine defaults and merge learner overrides on top.

    engine_root: path to the engine directory (contains defaults.yaml).
    instance_root: path to the instance directory (may contain learner/config.yaml).
    """
    defaults = _load_yaml(engine_root / "defaults.yaml")
    overrides = _load_yaml(instance_root / "learner" / "config.yaml")
    return _deep_merge(defaults, overrides)
