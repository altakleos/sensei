"""Config loader: deep-merge engine defaults with learner overrides."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: Missing 'pyyaml'. Install with: pip install sensei-tutor", file=sys.stderr)
    sys.exit(1)


class ConfigValidationError(ValueError):
    """Raised when the merged config fails schema validation at load time.

    Per ADR-0025, runtime validation is hard-fail by default. The
    SENSEI_CONFIG_SOFT_FAIL=1 environment variable downgrades the failure
    to stderr WARN lines for engine-repair / dev / CI-smoke scenarios.
    """


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


def _validate(merged: dict[str, Any], engine_root: Path) -> None:
    """Validate *merged* config against defaults.schema.json.

    Per ADR-0025, hard-fails by default — raises ConfigValidationError
    listing every violation. Set ``SENSEI_CONFIG_SOFT_FAIL=1`` to downgrade
    to stderr WARN lines and continue (engine-repair / dev / CI-smoke).

    No-op when the schema file is absent or jsonschema is not installed —
    the strict gate at `sensei verify` is the canonical authority; deferring
    here lets the engine bootstrap on partial installs.
    """
    schema_path = engine_root / "schemas" / "defaults.schema.json"
    if not schema_path.exists():
        return
    try:
        import json

        import jsonschema
    except ImportError:
        return
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(merged), key=lambda e: list(e.absolute_path))
    if not errors:
        return
    formatted = [
        f"{list(err.absolute_path) or '<root>'}: {err.message}" for err in errors
    ]
    if os.environ.get("SENSEI_CONFIG_SOFT_FAIL") == "1":
        for line in formatted:
            print(f"WARN: config: {line}", file=sys.stderr)
        return
    raise ConfigValidationError(
        "merged config failed schema validation:\n  - "
        + "\n  - ".join(formatted)
        + "\nset SENSEI_CONFIG_SOFT_FAIL=1 to downgrade to a warning."
    )


def load_config(engine_root: Path, instance_root: Path) -> dict[str, Any]:
    """Load engine defaults and merge learner overrides on top.

    engine_root: path to the engine directory (contains defaults.yaml).
    instance_root: path to the instance directory (may contain learner/config.yaml).

    Raises:
        ConfigValidationError: merged config violates defaults.schema.json
            (hard-fail by default; downgrade with SENSEI_CONFIG_SOFT_FAIL=1).
        ValueError: defaults.yaml or learner/config.yaml is invalid YAML or
            not a top-level mapping.
    """
    defaults = _load_yaml(engine_root / "defaults.yaml")
    overrides = _load_yaml(instance_root / "learner" / "config.yaml")
    merged = _deep_merge(defaults, overrides)
    _validate(merged, engine_root)
    return merged
