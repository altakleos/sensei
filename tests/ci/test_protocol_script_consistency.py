"""Linter: every `python .sensei/scripts/<name>.py …` invocation in a protocol
must resolve against the script's actual argparse CLI.

Prose-as-code protocols under `src/sensei/engine/protocols/` contain literal
subprocess invocations that an LLM runtime executes verbatim. When a protocol
drifts from a script's CLI, the LLM emits failing commands at runtime. This
suite parses every invocation from every protocol and validates it against the
parser extracted by importing the script and capturing its ArgumentParser.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import re
import shlex
from pathlib import Path
from typing import NamedTuple

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PROTOCOLS_DIR = _REPO_ROOT / "src" / "sensei" / "engine" / "protocols"

# Subprocess-invokable scripts. Internal-only modules (__init__, _atomic,
# config, migrate) are excluded — they are never called from protocol prose.
_INVOKED_SCRIPTS: frozenset[str] = frozenset({
    "check_goal",
    "check_profile",
    "classify_confidence",
    "decay",
    "frontier",
    "global_knowledge",
    "goal_priority",
    "hint_decay",
    "mastery_check",
    "mutate_graph",
    "resume_planner",
    "review_scheduler",
    "session_allocator",
})

# Matches `python[3] [prefix-path/]<script>.py <args-up-to-eol-or-backtick>`.
# The path prefix is lazy so the regex works for both fenced-block and inline
# forms (`python .sensei/scripts/X.py ...` and `  python .sensei/scripts/X.py …`).
_INVOCATION_RE = re.compile(
    r"python3?\s+[\w./]*?\.sensei/scripts/(\w+)\.py\b([^\n`]*)"
)


class ParserSpec(NamedTuple):
    required: frozenset[str]
    optional: frozenset[str]
    has_positionals: bool


class Invocation(NamedTuple):
    protocol: str
    line: int
    script: str
    args: str


def _extract_spec(script_name: str) -> ParserSpec:
    """Import a script module and capture the ArgumentParser it constructs.

    Each engine script follows the pattern `def main(argv): parser = ...;
    args = parser.parse_args(argv)`. We monkey-patch
    `ArgumentParser.parse_args` to intercept the call, record `self`, then
    raise to abort main(). This avoids reimplementing or parsing the script
    source — we use the real parser object that the script builds.
    """
    module = importlib.import_module(f"sensei.engine.scripts.{script_name}")
    captured: list[argparse.ArgumentParser] = []

    class _StopParsing(Exception):
        pass

    original = argparse.ArgumentParser.parse_args

    def _capture(self: argparse.ArgumentParser, *_args: object, **_kwargs: object) -> object:  # noqa: ANN401
        captured.append(self)
        raise _StopParsing()

    argparse.ArgumentParser.parse_args = _capture  # type: ignore[assignment,method-assign]
    try:
        with contextlib.suppress(_StopParsing, SystemExit):
            module.main([])
    finally:
        argparse.ArgumentParser.parse_args = original  # type: ignore[method-assign]

    if not captured:
        raise RuntimeError(f"Could not capture parser for script {script_name!r}")

    parser = captured[0]
    required: set[str] = set()
    optional: set[str] = set()
    has_positionals = False
    for action in parser._actions:  # noqa: SLF001
        if isinstance(action, argparse._HelpAction):  # noqa: SLF001
            continue
        if action.option_strings:
            target = required if action.required else optional
            for opt in action.option_strings:
                target.add(opt)
        else:
            has_positionals = True
    return ParserSpec(frozenset(required), frozenset(optional), has_positionals)


def _join_continuations(text: str) -> str:
    """Collapse shell `\\<newline>` continuations into a single logical line."""
    return re.sub(r"\\\n\s*", " ", text)


def _find_invocations(protocol_path: Path) -> list[Invocation]:
    original = protocol_path.read_text(encoding="utf-8")
    joined = _join_continuations(original)
    results: list[Invocation] = []
    for match in _INVOCATION_RE.finditer(joined):
        # Map match start back to the original file's line number by counting
        # newlines in the pre-join prefix — the `\<newline>` join removed
        # newlines, so count in the joined text to stay consistent.
        line = joined[: match.start()].count("\n") + 1
        results.append(
            Invocation(
                protocol=protocol_path.name,
                line=line,
                script=match.group(1),
                args=match.group(2).strip(),
            )
        )
    return results


def _check(inv: Invocation, specs: dict[str, ParserSpec]) -> list[str]:
    errors: list[str] = []
    if inv.script not in specs:
        return [f"unknown script {inv.script!r} — not in the invoked-scripts allowlist"]

    spec = specs[inv.script]
    try:
        tokens = shlex.split(inv.args, posix=True)
    except ValueError as exc:
        return [f"shlex parse failed: {exc}"]

    seen: set[str] = set()
    idx = 0
    while idx < len(tokens):
        tok = tokens[idx]
        if tok.startswith("--"):
            name = tok.split("=", 1)[0]
            if name not in spec.required and name not in spec.optional:
                errors.append(f"unknown flag {name!r}")
                idx += 1
                continue
            seen.add(name)
            if "=" in tok:
                idx += 1
                continue
            # Peek ahead for a value; only consume if the next token isn't a flag.
            if idx + 1 < len(tokens) and not tokens[idx + 1].startswith("-"):
                idx += 2
            else:
                idx += 1
        elif tok.startswith("-"):
            errors.append(f"unexpected short-form flag {tok!r}")
            idx += 1
        else:
            if not spec.has_positionals:
                errors.append(f"unexpected positional argument {tok!r}")
            idx += 1

    missing = sorted(spec.required - seen)
    if missing:
        errors.append(f"missing required flag(s): {missing}")
    return errors


@pytest.fixture(scope="module")
def specs() -> dict[str, ParserSpec]:
    return {name: _extract_spec(name) for name in _INVOKED_SCRIPTS}


@pytest.fixture(scope="module")
def invocations() -> list[Invocation]:
    collected: list[Invocation] = []
    for path in sorted(_PROTOCOLS_DIR.rglob("*.md")):
        collected.extend(_find_invocations(path))
    return collected


def test_invocations_detected(invocations: list[Invocation]) -> None:
    assert invocations, "no script invocations detected — regex or fixtures are broken"


def test_all_invoked_scripts_have_parsers(specs: dict[str, ParserSpec]) -> None:
    for name in _INVOKED_SCRIPTS:
        assert name in specs, f"parser extraction failed for {name}"
        assert specs[name].required or specs[name].optional, f"empty parser for {name}"


def test_all_protocol_invocations_match_script_clis(
    invocations: list[Invocation], specs: dict[str, ParserSpec]
) -> None:
    failures: list[str] = []
    for inv in invocations:
        errs = _check(inv, specs)
        if errs:
            failures.append(
                f"{inv.protocol}:{inv.line} → "
                f"`python .sensei/scripts/{inv.script}.py {inv.args}`: "
                + "; ".join(errs)
            )
    if failures:
        rendered = "\n  ".join(failures)
        pytest.fail(
            f"Protocol↔script CLI mismatches ({len(failures)}):\n  {rendered}\n\n"
            "Fix: update the protocol prose to match the script's argparse CLI, "
            "or update the script if the protocol form is preferable."
        )
