"""Pytest loader for transcript fixtures.

Discovers `tests/transcripts/<protocol>.md` fixture files and pairs each
with a `<protocol>.dogfood.md` companion. For every `fixtures:` entry in
the frontmatter, emits one parametrised pytest case via the
`transcript_case` parameter consumed by `test_fixtures.py`.

Missing dogfood transcripts produce `pytest.skip`, never a failing case.

See `docs/design/transcript-fixtures.md` for the full design, and
`docs/decisions/0011-transcript-fixtures.md` for the ADR.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

_TRANSCRIPTS_DIR = Path(__file__).resolve().parent


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    fm = yaml.safe_load(text[4:end]) or {}
    body = text[end + len("\n---\n"):]
    return fm, body


def _load_fixture_file(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    fm, _ = _split_frontmatter(path.read_text(encoding="utf-8"))
    return fm, list(fm.get("fixtures") or [])


def extract_mentor_turns(dogfood_text: str) -> list[str]:
    """Return the list of mentor turns from a dogfood transcript.

    Turn markers: lines starting with `[MENTOR]` open a mentor turn;
    `[LEARNER]` closes whatever turn is open; other lines are ignored
    outside a turn and appended inside a turn. Frontmatter (if present)
    is stripped before parsing.
    """
    _, body = _split_frontmatter(dogfood_text)
    turns: list[str] = []
    current: list[str] | None = None
    for line in body.splitlines():
        if line.startswith("[MENTOR]"):
            if current is not None:
                turns.append("\n".join(current).strip())
            current = [line[len("[MENTOR]"):].lstrip()]
        elif line.startswith("[LEARNER]"):
            if current is not None:
                turns.append("\n".join(current).strip())
                current = None
        elif current is not None:
            current.append(line)
    if current is not None:
        turns.append("\n".join(current).strip())
    return [t for t in turns if t]


def _discover_cases() -> list[tuple[str, Path, Path, dict[str, Any]]]:
    cases: list[tuple[str, Path, Path, dict[str, Any]]] = []
    for path in sorted(_TRANSCRIPTS_DIR.glob("*.md")):
        name = path.name
        if name == "README.md" or name.endswith(".dogfood.md"):
            continue
        fm, fixtures = _load_fixture_file(path)
        dogfood_path = path.with_name(f"{path.stem}.dogfood.md")
        for fixture in fixtures:
            case_id = f"{path.stem}::{fixture['name']}"
            cases.append((case_id, path, dogfood_path, fixture))
    return cases


def pytest_generate_tests(metafunc):
    if "transcript_case" in metafunc.fixturenames:
        cases = _discover_cases()
        metafunc.parametrize(
            "transcript_case",
            cases,
            ids=[c[0] for c in cases],
        )
