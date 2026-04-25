"""Tests for src/sensei/engine/schemas/defaults.schema.json.

Two complementary checks:

1. Forward: every default value shipped in `defaults.yaml` must validate
   against the schema. Catches drift if a maintainer changes the schema
   without updating defaults (e.g. tightens a range below the shipped value).

2. Inverse: every top-level key present in `defaults.yaml` must appear in
   the schema's `properties`. Catches new tunables that get added to
   `defaults.yaml` without a corresponding schema update — those would
   silently bypass `sensei verify`.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULTS_PATH = _REPO_ROOT / "src" / "sensei" / "engine" / "defaults.yaml"
_SCHEMA_PATH = _REPO_ROOT / "src" / "sensei" / "engine" / "schemas" / "defaults.schema.json"


def _load_schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_defaults() -> dict:
    return yaml.safe_load(_DEFAULTS_PATH.read_text(encoding="utf-8"))


def test_schema_file_exists() -> None:
    assert _SCHEMA_PATH.is_file(), f"schema not found: {_SCHEMA_PATH}"


def test_schema_is_valid_jsonschema() -> None:
    """The schema itself must be a valid Draft-2020-12 schema."""
    schema = _load_schema()
    jsonschema.Draft202012Validator.check_schema(schema)


def test_shipped_defaults_validate_against_schema() -> None:
    """Forward check: defaults.yaml as shipped must satisfy the schema."""
    schema = _load_schema()
    defaults = _load_defaults()
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(defaults),
        key=lambda e: list(e.absolute_path),
    )
    assert not errors, "\n".join(
        f"  - {list(e.absolute_path) or '<root>'}: {e.message}" for e in errors
    )


def test_every_top_level_default_is_in_schema() -> None:
    """Inverse check: every top-level key in defaults.yaml must appear in
    the schema's `properties`. A new tunable added without schema update
    would otherwise silently bypass `sensei verify`."""
    schema = _load_schema()
    defaults = _load_defaults()
    schema_props = set(schema.get("properties", {}).keys())
    default_keys = set(defaults.keys())
    unregistered = sorted(default_keys - schema_props)
    assert not unregistered, (
        "The following top-level keys are in defaults.yaml but not in "
        "defaults.schema.json. Add them to the schema's `properties:`:\n  - "
        + "\n  - ".join(unregistered)
    )


def test_schema_rejects_unknown_top_level_property() -> None:
    """additionalProperties:false at the top level must reject typos."""
    schema = _load_schema()
    bad = _load_defaults()
    bad["totally_made_up_section"] = {"foo": 1}
    errors = list(jsonschema.Draft202012Validator(schema).iter_errors(bad))
    assert any("totally_made_up_section" in e.message for e in errors), (
        "schema should reject unknown top-level keys"
    )


@pytest.mark.parametrize(
    "path,bad_value,expected_substring",
    [
        # Wrong type
        (("memory", "half_life_days"), "seven", "number"),
        # Out of range (stale_threshold must be in (0, 1])
        (("memory", "stale_threshold"), 1.5, "1"),
        # Enum violation
        (("performance_training", "mastery_gate"), "legendary", "is not one of"),
        # Negative when minimum is 0
        (("curriculum", "prior_knowledge_percentile"), -10, "0"),
        # Above maximum
        (("interleaving", "intensity"), 2.0, "1"),
    ],
)
def test_schema_rejects_invalid_values(
    path: tuple, bad_value: object, expected_substring: str
) -> None:
    """Spot-check that representative invariants actually fire."""
    schema = _load_schema()
    bad = _load_defaults()
    cursor = bad
    for key in path[:-1]:
        cursor = cursor.setdefault(key, {})
    cursor[path[-1]] = bad_value
    errors = list(jsonschema.Draft202012Validator(schema).iter_errors(bad))
    matched = [e for e in errors if list(e.absolute_path) == list(path)]
    assert matched, f"expected an error at {path}, got: {[(list(e.absolute_path), e.message) for e in errors]}"
    assert any(expected_substring in e.message.lower() or expected_substring in e.message for e in matched)
