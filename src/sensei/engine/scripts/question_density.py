"""Compute mentor question-density from a dogfood transcript.

Question-density complements silence_ratio: silence_ratio measures HOW MUCH
the mentor talks; question-density measures WHAT SHAPE the talk takes. A
Socratic regression (mentor stops asking, starts lecturing) cuts
question-density without necessarily moving silence_ratio.

Heuristic: a "question" is a ``?`` followed by whitespace, end-of-string,
or sentence-terminator punctuation, **outside fenced code blocks**.
Emphatic clusters (``??``, ``???``) count once via a negative lookbehind.
Density = ``total_mentor_questions / total_mentor_turns``; degenerate
zero-mentor-turn transcripts yield density 0.0.

Per-protocol expected ranges (calibrated by the per-fixture bands in
``tests/transcripts/<protocol>.md``):

- High (≥0.8): ``assess`` (probing IS the protocol)
- High (≥0.7): ``challenger`` (provoke, don't tell)
- High (≥0.6): ``cross_goal_review`` (Q&A across topics)
- Medium-high (≥0.4): ``tutor``, ``review``
- Medium (≥0.3): ``goal``
- Low (≤0.4): ``reviewer`` (feedback is the deliverable)
- Low (≤0.3): ``hints`` (narrative triage)
- Very low (≤0.2): ``status``
- Variable: ``performance_training`` (stage-dependent)

Invoked by tests and at the CLI as:
    python -m sensei.engine.scripts.question_density --transcript <path>

Library entry points:
    compute_question_density(text: str) -> float
    compute_question_stats(text: str) -> dict[str, int | float]

Exit codes:
    0 — JSON object on stdout: {mentor_turns, mentor_questions, question_density}
    1 — file missing or unparseable; error JSON on stdout
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Shared with silence_ratio + teaching_density via the public
# split_into_turns API: all three Tier-1 metrics see the same canonical
# notion of a turn.
from sensei.engine.scripts.silence_ratio import split_into_turns

# Triple-backtick fenced code block. Strip these before counting ``?`` so
# a code sample with a rhetorical-comment ``?`` doesn't inflate the
# mentor's question count. ``re.DOTALL`` lets ``.`` match newlines so
# multi-line fences are removed wholesale.
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)

# A question is ``?`` followed by whitespace, end-of-string, or sentence
# punctuation, AND not preceded by another ``?`` (so emphatic ``??`` /
# ``???`` clusters count once, not N times). End-of-string covers the
# common case where a turn ends mid-question without a trailing newline.
_QUESTION_RE = re.compile(r"(?<!\?)\?(?=\s|$|[.!?,;])")


def _strip_code_fences(text: str) -> str:
    """Remove triple-backtick fenced code blocks from *text*."""
    return _CODE_FENCE_RE.sub("", text)


def _count_questions(turns: list[str]) -> int:
    return sum(len(_QUESTION_RE.findall(_strip_code_fences(t))) for t in turns)


def compute_question_stats(text: str) -> dict[str, float]:
    """Return mentor turn count, question count, and per-turn density.

    ``question_density`` is ``mentor_questions / mentor_turns``, or 0.0
    when the transcript has no mentor turns (degenerate but valid).
    """
    mentor, _learner = split_into_turns(text)
    questions = _count_questions(mentor)
    turns = len(mentor)
    density = (questions / turns) if turns > 0 else 0.0
    return {
        "mentor_turns": turns,
        "mentor_questions": questions,
        "question_density": density,
    }


def compute_question_density(text: str) -> float:
    """Convenience wrapper for fixture-level assertions."""
    return float(compute_question_stats(text)["question_density"])


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

    stats = compute_question_stats(text)
    if stats["mentor_turns"] == 0:
        print(json.dumps({"error": "transcript has no [MENTOR] turns"}))
        return 1
    print(json.dumps(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
