---
status: accepted
date: 2026-04-20
---
# ADR-0012: Adopt `docs/foundations/` for Cross-Cutting Concerns

## Context

The six-layer SDD model (`docs/specs/`, `docs/design/`, `docs/decisions/`, `docs/plans/`, `docs/operations/`, Implementation + Verification) has no clean home for:

1. **Product vision** — pedagogical pillars, mentor relationship, mission (currently in `PRODUCT-IDEATION.md`, a 57KB monolith).
2. **Technical principles** that span all mechanisms (currently in `docs/sensei-implementation.md` § "Load-Bearing Principles").
3. **Policy ADRs** that apply to all features (currently ADRs 0006, 0009, 0011 sit alongside feature-scoped ADRs with no scope distinction).
4. **Personas** — Jacundu (senior SDE interview prep) stress-tests every pillar and protocol but fits neither a feature spec nor a design doc.

The spec template at `docs/specs/README.md` requires "Invariants" — observable properties that must hold. Pedagogical pillars ("restraint is teaching", "ask don't tell") are not observable in this sense; forcing them into the spec template produces either vacuous invariants or fraudulent ones.

External research (AWS Kiro `.kiro/steering/`, GitHub Spec Kit `.specify/memory/constitution.md`, Python PEPs, Rust RFCs, Kubernetes `design-proposals-archive/architecture/principles.md`, TOGAF principle template, Diataxis "explanation" mode) converges on two patterns: (a) cross-cutting material lives in a distinct directory, not mixed with feature specs; (b) cross-cutting material uses a template shape different from the feature-spec template.

Five structural alternatives were evaluated via a 5-agent parallel analysis (A: minimalist in-place via `kind:` frontmatter; B: three sibling directories with distinct templates; C: PEP-style type tags in one directory; D: memory/steering layer adjacent to specs; E: method-level seventh layer "Tenets"). An adversarial critic then reviewed the leading synthesis and mandated six amendments.

## Decision

Add a new top-level directory `docs/foundations/` — **source material above the six-layer stack**, not a seventh processing layer. The six-layer flow (Specs → Design → Decisions → Plans → Implementation → Verification) is unchanged. Foundations sits alongside `docs/specs/` as corpus that specs cite; feature work continues to flow through the existing layers.

### Shape

```
docs/foundations/
├── README.md             — index, linkage conventions, linter contract
├── vision.md             — product mission + identity (narrative prose, single file)
├── principles/<slug>.md  — cross-cutting principles (unified template)
└── personas/<slug>.md    — design-stressing personas
```

`docs/decisions/` is unchanged; cross-cutting ADRs gain an optional `scope: policy` frontmatter field (default: `feature`).

### Templates

**Principle** — unified for pedagogical, technical, and product principles distinguished by a `kind:` frontmatter field (prior draft split `pillars/` and `principles/`; the adversarial critic identified these as the same artifact type). Structure: YAML frontmatter (`status`, `date`, `id: P-<slug>`, `kind: pedagogical | technical | product`), then sections Statement / Rationale / Implications / Exceptions-and-Tensions / Source. TOGAF-flavoured.

**Persona** — YAML frontmatter (`status`, `owner`, `id: persona-<slug>`, `stresses: [spec-slug, P-slug, ...]`), then sections Scenario / Goals / Frictions / Stress-tests / Success-and-Anti-signals. **No `last_validated` field** — decorative timestamps without CI enforcement were rejected during adversarial review. Personas are either present (valid) or superseded.

**Vision** — single file, narrative prose, light frontmatter only.

### Linkage

Feature specs gain optional frontmatter arrays:

- `serves: [vision-slug, P-slug, ...]` — which principles / vision this spec realises.
- `realizes: [P-slug, ...]` — which technical principles this spec embodies (same tag space as `serves:`, scope can be finer at author discretion).
- `stressed_by: [persona-slug, ...]` — which personas stress this feature.

Personas carry `stresses: [...]` pointing at specs and principles they stress-test.

### Enforcement

`ci/check_foundations.py` — hard-fail CI gate, ships in the same PR as the foundations directory (no linter, no directory):

- Every `serves:` / `realizes:` / `stressed_by:` / `stresses:` slug resolves to an existing foundation file with correct type.
- Every accepted principle is referenced by at least one spec within N commits (warning-tier).
- `kind:` in principles is one of the allowed values.
- `scope: policy` ADRs carry an explicit "Enforcement Evidence" section listing per-feature realisation (deferred to a follow-up ADR — not mandatory in this first pass).

### Migration workflow

Promoting an invariant from a feature spec to a foundation principle, or demoting a foundation invariant to a feature spec, requires an **ADR-lite** with explicit Before-state / After-state / Why-the-migration sections. The superseded artifact retains a `superseded-by:` frontmatter reference and is never deleted.

### Method-level recognition in `development-process.md`

A new section "Foundations" is inserted before § "Specs" describing the layer as project-agnostic source material — vision / principles / personas — that feature artifacts cite. The new section is fuller than a one-paragraph mention (per user directive) but contains no Sensei-specific content; Sensei's instantiation of foundations lives in `docs/sensei-implementation.md`.

## Alternatives Considered

- **A. Minimalist in-place** (`kind:` frontmatter in existing `docs/specs/`, principles catalog in `sensei-implementation.md`). Rejected because it forces philosophy into the feature-spec template (Intent / Invariants), producing vacuous invariants per the adversarial critic.
- **B. Three sibling directories** (`docs/principles/`, `docs/personas/`, `docs/vision/`). Partially adopted — became `docs/foundations/{vision.md, principles/, personas/}` per the adversarial critic's amendment: pillars and principles are the same artifact type with a `kind:` discriminator.
- **C. PEP-style type tags** (`type: feature-spec | product-vision | principle | policy | persona` in one directory). Rejected because flat-directory-plus-tags loses the legibility of `ls docs/` and makes enforcement brittle when tag discipline slips.
- **D. Memory / steering layer** (Kiro `steering/`, Spec Kit `memory/constitution.md`). Partially adopted in naming: the research confirmed "steering" carries car-driving metaphor baggage and "memory" is overloaded with agent-written auto-notes. "Foundations" was chosen.
- **E. Method-level seventh layer "Tenets"** (extends the 6-layer stack). Rejected: the adversarial critic correctly noted that cross-cutting material is *input to* the stack, not a stage of it. The layer stack stays at six; foundations sits above as source material.

## Consequences

### Positive

- Product vision, principles, and personas have distinct homes with shape-appropriate templates. Pillars are not shoehorned into "Invariants."
- Technical principles live outside the instantiation doc; `sensei-implementation.md` shrinks to its proper concern (Implementation + Verification tables).
- Linkage is mechanically checked from day 1 via the hard-fail `check_foundations.py` gate.
- External practice (Kiro, Spec Kit, Kubernetes, TOGAF) is reflected without importing discipline that doesn't match Sensei's scale.
- The six-layer method stays intact — `development-process.md` gains a "Foundations" section without restructuring the flow diagram.
- Project-agnosticism is preserved: a project with no cross-cutting philosophy leaves `docs/foundations/` empty; the extension is optional-but-prescribed.

### Negative

- New artifact type to learn; contributors must know four homes (foundations / specs / design / decisions) instead of three.
- Risk of pillar/principle conflation for contributors unfamiliar with the `kind:` discriminator (mitigated by the linter + a decision guide in `foundations/README.md`).
- Migration of the 6 existing principles from `sensei-implementation.md` + 7 pedagogical pillars from `PRODUCT-IDEATION.md` + 1 persona is a substantial one-time content move.

### Config Impact

- `ci/check_foundations.py` — new validator (hard-fail in CI).
- `tests/ci/test_check_foundations.py` — test suite.
- `docs/development-process.md` — new "Foundations" section.
- `docs/sensei-implementation.md` — Load-Bearing Principles section migrates out.
- `docs/specs/README.md` — template gains optional `serves:` / `realizes:` / `stressed_by:` frontmatter fields.

## References

- [`docs/development-process.md`](../development-process.md) — method doc gaining the new section.
- [`docs/sensei-implementation.md`](../sensei-implementation.md) — source of technical principles migrating out.
- [`docs/foundations/`](../foundations/) — destination of pedagogical pillars and Jacundu persona.
- [ADR-0005: ADR-Lite Format](0005-adr-lite-format.md) — precedent for the `scope: policy` frontmatter approach and the migration-ADR format.
- [ADR-0011: Transcript Fixtures](0011-transcript-fixtures.md) — precedent for widening artifact inventory (Verification) without adding a new layer.
- External research: AWS Kiro `.kiro/steering/`, GitHub Spec Kit `.specify/memory/constitution.md`, Kubernetes `design-proposals-archive/architecture/principles.md`, TOGAF principle template, Python PEPs, Diataxis framework.
