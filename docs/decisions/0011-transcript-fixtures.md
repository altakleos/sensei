---
status: accepted
date: 2026-04-20
weight: lite
protocols: [all]
---
# ADR-0011: Transcript Fixtures as a Verification Artifact

## Decision

Transcript fixtures become a first-class artifact type in the Verification layer, alongside CPython `tests/scripts/`, `tests/ci/`, and `tests/test_init.py`. Each engine protocol (under `src/sensei/engine/protocols/`) earns a fixtures file at `tests/transcripts/<protocol>.md` plus a companion dogfood transcript at `tests/transcripts/<protocol>.dogfood.md`. A pytest loader (`tests/transcripts/conftest.py`) parses both and emits parametrised test cases that assert the LLM's mentor turns satisfy the invariants declared in the protocol spec.

Tier-1 checks are lexical (regex / phrase presence/absence) and run free in CI. Tier-2 checks (LLM-as-judge) are operator-local and deferred beyond the MVP. Load-bearing principle #6 — "Prose verified by prose" — is added to `docs/sensei-implementation.md`.

## Why

Implementation in Sensei is partly markdown-protocol prose executed by an LLM. Verification today is CPython-only and cannot assert whether the LLM actually follows the protocol's numbered steps, respects its silence profile, or honours its refusal branches. Without a committed verification artifact, protocol behavioural correctness is a feeling, not a contract. Transcript fixtures fill that gap without introducing a new SDD layer — Verification's functional definition ("verifiers may run on a CPU, in an LLM, or both") already covers them.

## Alternative

Add "Behavioural Verification" as a new layer between Implementation and Verification. Rejected because it duplicates Verification's purpose and would force re-documenting every flow rule that already applies to Verification. Widening an existing layer's artifact inventory is cheaper and matches the method-neutral intent of the SDD stack.
