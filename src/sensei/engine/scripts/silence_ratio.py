"""Compute mentor talk-share from a dogfood transcript.

`engine.md` § Invariants codifies per-mode silence profiles ("Tutor ~40%
silent; Assessor silent while learner works; Challenger silent for
productive failure; Reviewer NOT silent"). This helper turns those prose
claims into a number a fixture can assert against.

Word-share = mentor_words / (mentor_words + learner_words). Punctuation
and whitespace are excluded so a mentor speaking in short clipped
sentences ("Got it.") is not penalised for using more punctuation than
the learner.

Invoked by protocols and tests as:
    python -m sensei.engine.scripts.silence_ratio --transcript <path>

Library entry points:
    compute_word_share(text: str) -> float
    compute_turn_stats(text: str) -> dict[str, int | float]

Exit codes:
    0 — JSON object on stdout: {mentor_words, learner_words,
        mentor_word_share, mentor_turns, learner_turns}
    1 — file missing or unparseable; error JSON on stdout
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Pattern matches the same line-marker convention used by
# tests/transcripts/conftest.py:extract_mentor_turns. Kept as a regex so
# leading whitespace inside a turn doesn't accidentally re-trigger.
_MENTOR_PREFIX = "[MENTOR]"
_LEARNER_PREFIX = "[LEARNER]"

# Word boundary: any maximal run of unicode word characters. Excludes
# punctuation, whitespace, and turn markers.
_WORD_RE = re.compile(r"\w+", re.UNICODE)


def _strip_frontmatter(text: str) -> str:
    """Strip a leading YAML frontmatter block if present."""
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end < 0:
        return text
    return text[end + len("\n---\n"):]


def _split_into_turns(text: str) -> tuple[list[str], list[str]]:
    """Walk the body and accumulate mentor and learner turn texts.

    Each `[MENTOR]` line opens a mentor turn; each `[LEARNER]` line opens
    a learner turn. Lines without a marker are appended to whichever
    turn is currently open. A new marker closes the previous turn.
    """
    body = _strip_frontmatter(text)
    mentor_turns: list[str] = []
    learner_turns: list[str] = []
    current_kind: str | None = None
    buffer: list[str] = []

    def _flush() -> None:
        if current_kind is None:
            return
        joined = "\n".join(buffer).strip()
        if joined:
            (mentor_turns if current_kind == "mentor" else learner_turns).append(joined)

    for line in body.splitlines():
        if line.startswith(_MENTOR_PREFIX):
            _flush()
            current_kind = "mentor"
            buffer = [line[len(_MENTOR_PREFIX):].lstrip()]
        elif line.startswith(_LEARNER_PREFIX):
            _flush()
            current_kind = "learner"
            buffer = [line[len(_LEARNER_PREFIX):].lstrip()]
        elif current_kind is not None:
            buffer.append(line)
    _flush()
    return mentor_turns, learner_turns


def _count_words(turns: list[str]) -> int:
    return sum(len(_WORD_RE.findall(t)) for t in turns)


def compute_turn_stats(text: str) -> dict[str, float]:
    """Return mentor/learner word counts, turn counts, and mentor share.

    `mentor_word_share` is `mentor_words / (mentor_words + learner_words)`,
    or 0.0 if neither side has any words (degenerate transcript).
    """
    mentor, learner = _split_into_turns(text)
    m_words = _count_words(mentor)
    l_words = _count_words(learner)
    total = m_words + l_words
    share = (m_words / total) if total > 0 else 0.0
    return {
        "mentor_words": m_words,
        "learner_words": l_words,
        "mentor_word_share": share,
        "mentor_turns": len(mentor),
        "learner_turns": len(learner),
    }


def compute_word_share(text: str) -> float:
    """Convenience wrapper for fixture-level assertions."""
    return float(compute_turn_stats(text)["mentor_word_share"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--transcript", required=True, help="Path to a dogfood transcript file")
    args = parser.parse_args(argv)

    path = Path(args.transcript)
    if not path.is_file():
        print(json.dumps({"error": f"transcript not found: {path}"}))
        return 1
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(json.dumps({"error": f"read failed: {exc}"}))
        return 1

    stats = compute_turn_stats(text)
    if stats["mentor_turns"] == 0 and stats["learner_turns"] == 0:
        print(json.dumps({"error": "transcript has no [MENTOR] or [LEARNER] turns"}))
        return 1
    print(json.dumps(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
