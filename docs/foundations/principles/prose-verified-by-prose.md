---
status: accepted
date: 2026-04-20
id: P-prose-verified-by-prose
kind: technical
---
# Prose Verified by Prose

## Statement

Every engine protocol earns a fixture file at `tests/transcripts/<protocol>.md` that pins its spec invariants to lexical assertions over a committed dogfood transcript.

## Rationale

Protocols are prose executed by an LLM. CPython tests can verify that the helpers a protocol invokes compose correctly; they cannot verify that the LLM actually followed the protocol's numbered steps, respected its silence profile, or honoured its refusal branches. Without an artifact that asserts behavioural conformance, protocol correctness is a feeling — and feelings rot silently.

## Implications

- Every accepted protocol at `src/sensei/engine/protocols/<name>.md` has a companion at `.kanon/fidelity/<name>.md` declaring `forbidden_phrases`, `required_one_of`, and/or `required_all_of` per invariant cluster.
- The dogfood transcript at `.kanon/fidelity/<name>.dogfood.md` is captured from a real LLM session and refreshed at each release (tier 1) or when the protocol changes (tier 2).
- Missing dogfood transcripts produce `pytest.skip`, not failure; the signal is "not yet exercised," not "broken."
- Tier-2 LLM-as-judge verification is operator-local (no API keys in CI); tier-1 lexical assertions run free on every push.

## Exceptions / Tensions

- Protocols in draft (`status: draft`) may ship without fixtures; the pairing is required before `status: accepted`.
- This principle tensions with [P-validators-close-the-loop](validators-close-the-loop.md) only in that the medium differs — transcript fixtures ARE the validator for behavioural invariants that cannot be checked in CPython.

## Source

[ADR-0011: Transcript Fixtures as a Verification Artifact](../../decisions/0011-transcript-fixtures.md). Elevated to a foundations principle by [ADR-0012](../../decisions/0012-foundations-layer.md).
.
