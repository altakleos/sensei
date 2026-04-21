---
status: provisional
date: 2026-04-21
---
# ADR-0020: Phase Overlay Composition — Single Phase Protocol

## Context

Performance training (see [`docs/specs/performance-training.md`](../specs/performance-training.md)) is a cross-cutting journey phase that modifies how existing behavioral modes operate when a learner shifts from understanding to performing under pressure. It is explicitly not a fifth mode — it overlays the four existing modes with phase-specific behavioral deltas (Tutor adds time awareness, Challenger adds interview-style pressure, etc.).

The existing context composition model (ADR-0013) loads: base personality (full) + active mode (full) + inactive mode summaries. Performance training needs to inject additional behavioral instructions into this composition without breaking the focused-loading strategy that prevents attention dilution.

## Decision

Add a **single phase protocol file** (`protocols/performance-training.md`) as an additional context layer, loaded only when the performance phase is active for the current goal. The file contains per-mode overlay sections (`## When Tutor is Active`, `## When Challenger is Active`, etc.) that the LLM reads conditionally based on the active mode.

The composition model becomes:

```
personality (full) + active mode (full) + inactive §Summaries [+ phase protocol (full, when active)]
```

This adds one conditional slot to the context model. Future phases (e.g., onboarding, remediation) follow the same pattern: one protocol file per phase, loaded when that phase is active.

## Alternatives Considered

### A. Conditional sections within mode files

Each mode file gains a `## Performance Phase` section included only when the phase is active.

**Rejected.** Couples mode authoring to phase authoring — every future phase requires editing all four mode files. Violates separation of concerns. Mode files should define mode behavior; phase files should define phase behavior.

### B. Separate overlay files per mode

One overlay file per mode-phase combination (`protocols/overlays/performance-tutor.md`, etc.).

**Rejected.** File proliferation — 4 files for one phase, 8+ as phases grow. Each overlay is a few paragraphs, making per-file overhead disproportionate. A single file with per-mode sections is more maintainable and easier to review holistically.

## Consequences

### Positive

- Minimal file proliferation: one file per phase, not one per mode-phase combination.
- Clean separation: mode files are untouched; phase behavior lives in phase files.
- Consistent with ADR-0013: extends the composition model with one additional slot rather than restructuring it.
- Extensible: future phases follow the identical pattern.

### Negative

- The phase protocol file contains sections for all four modes, so the LLM sees overlay instructions for non-active modes (though it should attend primarily to the matching section). Mitigated by the same selective-attention pattern that already works for inactive mode summaries.
- Adds ~400–600 tokens to the context window when active. Acceptable given frontier model context limits.

## References

- [ADR-0013: Context Composition Strategy](0013-context-composition.md) — the base composition model this extends.
- [`docs/design/performance-training.md`](../design/performance-training.md) — full design doc with option analysis and context budget.
- [`docs/design/behavioral-modes.md`](../design/behavioral-modes.md) — the composition and transition model for behavioral modes.
