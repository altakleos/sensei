---
status: accepted
date: 2026-04-20
id: P-validators-close-the-loop
kind: technical
---
# Validators Close the Loop

## Statement

Every spec invariant that can be checked mechanically has a validator that hard-fails CI when the invariant is violated.

## Rationale

Without automated enforcement, invariants become aspirational. Review catches what reviewers look for; validators catch what everyone forgets. A spec whose invariant "every release has a changelog entry" is enforceable only via a reviewer glancing at the checklist is an invariant in name only.

## Implications

- New specs ship with their validator in the same PR (see [`ci/check_package_contents.py`](../../../ci/check_package_contents.py), [`ci/check_foundations.py`](../../../ci/check_foundations.py), [`src/sensei/engine/scripts/check_profile.py`](../../../src/sensei/engine/scripts/check_profile.py) for examples).
- Validators are hard-fail — they exit non-zero on violation and block the CI step, not a warning log.
- Warning-tier output is acceptable for transitional periods (e.g., orphan-principle warnings while the backreference surface is being populated) but must have an explicit promote-to-error plan.

## Exceptions / Tensions

- Behavioural invariants that require LLM interpretation (silence profile, Socratic style, conversational rapport) cannot be checked in CPython. These use transcript fixtures (see [P-prose-verified-by-prose](prose-verified-by-prose.md)) — a different mechanism for a different class of invariant, not an exemption from the principle.
- Invariants that are genuinely subjective ("the protocol should read naturally") are out of scope; if it can't be checked, it isn't an invariant, it's a preference.

## Source

SDD method discipline (`docs/development-process.md` § Verification). First codified as a load-bearing principle in the pre-foundations `sensei-implementation.md`; elevated by [ADR-0012](../../decisions/0012-foundations-layer.md).
