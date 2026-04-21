---
feature: hints-transcript-fixture
serves: docs/specs/hints.md
design: docs/design/transcript-fixtures.md
status: done
date: 2026-04-21
---
# Plan: Hints Transcript Fixture + ADR Graduation

Close the round-trip of the v0.1.0a9 methodology gate: add a Tier-1 transcript fixture for `protocols/hints.md`, then graduate the three hints-related ADRs (0017 file-drop ingestion, 0018 curriculum boosting, 0019 universal inbox) from `provisional` back to `accepted` now that live LLM evidence exists.

This plan is scoped as a **Behavioral-Change** flow per `docs/development-process.md` § How Work Flows Through the Layers: no new spec, no new design (existing artifacts `docs/specs/hints.md` + `docs/design/hints-ingestion.md` + `docs/design/transcript-fixtures.md` already cover intent and mechanism). One new verification artifact + three ADR status updates + one spec frontmatter backfill.

## Phases

### Phase 1 — Fixture scaffolding

- [ ] T1: Create `tests/transcripts/hints.md` with YAML frontmatter (`protocol: hints`, `spec: docs/specs/hints.md`, `status: golden`, `date: 2026-04-21`, and a `fixtures:` list). Author at least three `## Fixture: <name>` entries pinning the mentor-facing invariants below. Mirror the structure of `tests/transcripts/assess.md` and `tests/transcripts/review.md`. → `tests/transcripts/hints.md`
- [ ] T2: Create `tests/transcripts/hints.dogfood.md` as a **synthetic seed** (ADR-0011 allows this; the `assess.dogfood.md` precedent did the same). Frontmatter: `agent: synthetic-seed`, `status: seed`, `date: 2026-04-21`. Captures one representative triage session (scan inbox → extract topics → classify ambiguity → register → summarise). Leave a TODO note saying "replace with a real captured session at the next release" per `docs/design/transcript-fixtures.md` § Cadence. → `tests/transcripts/hints.dogfood.md`

### Phase 2 — Invariants to pin

The fixture must assert at least the following Tier-1 lexical properties, extracted from the hints spec + ADR-0017/0018/0019:

- [ ] T3: **triage-not-teaching** fixture.
  - `forbidden_phrases`: teaching leakage during triage — `"Let me explain"`, `"Actually,"`, `"Here's why"`, `"To help you understand"`, `"The answer is"`.
  - Rationale: `protocols/hints.md` operates in an administrative triage mode, not the tutor mode. Teaching during triage violates the behavioural-modes spec.
- [ ] T4: **concise-summary** fixture.
  - `required_one_of`: regex for triage-completion summary phrasing — e.g. `processed \d+ hint`, `boosted .* topic`, `archived .* expired`.
  - Rationale: per `docs/specs/hints.md`, the learner should see *counts and outcomes*, not per-item commentary.
- [ ] T5: **boost-visibility** fixture.
  - `required_one_of`: regex naming at least one boosted topic or the boost mechanism — e.g. `boost`, `prioritised`, `priority bump`.
  - Rationale: ADR-0018's "subtle influence" consequence is the risk this fixture exists to close. If the LLM silently boosts without telling the learner, the decision's downside materialises.
- [ ] T6: **ambiguity-classification** fixture.
  - `required_one_of`: regex matching a clarification-ask when a hint is genuinely unclassifiable — e.g. `What topic does this relate to\?`, `unsure.*classify`.
  - Rationale: ADR-0019's universal-inbox-with-LLM-triage design has a known gap around unclassifiable content; the learner must be asked, not silently ignored.

### Phase 3 — Verify

- [ ] T7: `pytest tests/transcripts/ -v` shows the new `hints::*` parametrised cases passing against the committed dogfood seed. Full suite remains green; coverage floor (89%) remains met.
- [ ] T8: Delete the dogfood transcript locally and re-run pytest — the `hints::*` cases should `SKIPPED`, not fail (loader-guarantee from `tests/transcripts/conftest.py`). Restore the transcript.

### Phase 4 — Graduate the ADRs

ADR provisional-callouts each name their review trigger ("review once a hints-protocol fixture lands"). This plan's Phase 1+2 IS that trigger.

- [ ] T9: Re-read [ADR-0017 — File-Drop Ingestion](../decisions/0017-file-drop-ingestion.md). Does the accepted decision still hold given the fixture behaviour? Expected: yes. Update frontmatter `status: provisional` → `status: accepted`. Replace the provisional callout with a short verified-by note referencing `tests/transcripts/hints.md` and today's date.
- [ ] T10: Same for [ADR-0018 — Curriculum Boosting over Rewriting](../decisions/0018-curriculum-boosting.md). The **boost-visibility** fixture (T5) specifically addresses the "subtle influence" consequence that drove this ADR to provisional.
- [ ] T11: Same for [ADR-0019 — Universal Inbox over Typed Drop Zones](../decisions/0019-universal-inbox.md). The **ambiguity-classification** fixture (T6) specifically validates the classify-at-triage bet.
- [ ] T12: Update `docs/decisions/README.md` index table — three rows flip from `provisional` back to `accepted`.

### Phase 5 — Spec and CHANGELOG wrap

- [ ] T13: Update `docs/specs/hints.md` frontmatter: the `fixtures_deferred:` line ("protocols/hints.md is still draft — add end-to-end coverage once ingestion + triage are committed") is no longer applicable; replace with a proper `fixtures:` entry listing `tests/transcripts/hints.md` and `tests/test_hint_decay.py`. Leave the fixtures-deferred field empty / remove.
- [ ] T14: `python ci/check_foundations.py` — still exits 0, no new warnings. Hints spec now has `fixtures:` so it's no longer warned.
- [ ] T15: Append two `## [Unreleased]` CHANGELOG entries:
  - `test: ...` describing the new hints fixture + dogfood seed.
  - `docs: ...` describing the ADR graduation from provisional → accepted (0017, 0018, 0019).

### Phase 6 — Branch + PR

- [ ] T16: All Phase 1–5 commits on `test/hints-transcript-fixture` (this branch). The plan was the first commit.
- [ ] T17: `pytest` green, `ruff check` + `mypy` clean, `python ci/check_foundations.py` ok.
- [ ] T18: Push the branch and open a PR. PR title: `test: hints transcript fixture + ADR 0017/0018/0019 graduation`. PR body summarises the round-trip demonstration of the methodology gate.

## Acceptance Criteria

- [ ] AC1: `tests/transcripts/hints.md` + `tests/transcripts/hints.dogfood.md` committed; new parametrised cases present in the pytest output.
- [ ] AC2: Removing the dogfood file results in `SKIPPED` cases, not `FAILED` — matches ADR-0011 loader invariant.
- [ ] AC3: ADRs 0017, 0018, 0019 all read `status: accepted` in frontmatter AND in the index README. Each ADR body's former provisional callout is replaced with a "verified by" note citing this PR's fixture.
- [ ] AC4: `docs/specs/hints.md` no longer carries `fixtures_deferred:`; carries `fixtures:` naming the new transcript fixture.
- [ ] AC5: `ci/check_foundations.py` status: ok with no warnings naming `hints.md`.
- [ ] AC6: Full suite (`pytest`) green; coverage floor still met; ruff + mypy clean.
- [ ] AC7: Branch merged to `main` via PR, matching `docs/development-process.md` § Pull request workflow.

## Out of Scope

- **Real captured dogfood transcript** (not a synthetic seed). Per `docs/design/transcript-fixtures.md` § Cadence, a real capture is owed at the next release or protocol change; this plan commits a synthetic seed and the real capture is a follow-up.
- **Tier-2 LLM-as-judge coverage** for hints. Tier-2 is deferred project-wide (see `tests/transcripts/README.md` tier table); adding it here would break the project-wide discipline.
- **New ADR** superseding one of the three. If Phase 4's re-read surfaces a reason to reverse any of 0017/0018/0019 (e.g. the boost-visibility fixture fails and we discover the mechanism is genuinely wrong), that discovery triggers a **separate** ADR under the immutability rule, not an edit to this plan.
- **Tier-2 E2E for hints in `tests/e2e/`**. A Tier-2 behavioural E2E would complement the Tier-1 lexical fixture but isn't required for ADR graduation. Possible follow-up after this lands.

## Notes

**Why the synthetic seed is acceptable at the graduation step.** The ADR-0011 precedent set by `review.dogfood.md` and `assess.dogfood.md` is that a synthetic seed exercises the loader pipeline and calibrates the fixture invariants, while a real capture replaces it later. Graduation triggers on the *fixture* landing, not on the dogfood transcript being real — because the fixture is the contract and the synthetic seed proves the invariants can be asserted against a coherent session. If the synthetic seed misrepresents what the LLM would actually do, the real-capture replacement (at the next release per design § Cadence) will surface the divergence — and that divergence is itself valuable signal, triggering another provisional review.

**Why 0018 graduates too, even though its evidence lives in `tests/test_frontier.py`.** ADR-0018's provisional rationale specifically named "subtle influence" as the unverified consequence — a mentor-facing behavior problem that unit tests on `frontier.py` cannot detect. The boost-visibility fixture (T5) closes that specific gap, which is what justifies graduation.
