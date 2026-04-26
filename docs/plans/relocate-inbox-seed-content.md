---
feature: relocate-inbox-seed-content
serves: docs/specs/release-process.md
design: "No design doc — pure repo-layout cleanup. Move 25 maintainer-curated seed-hint files from the source repo's top-level inbox/ to the sibling platform/sensei-hints/tech-interview/ directory; delete the now-empty inbox/; add /inbox/ to .gitignore as a safety net. Mechanism is filesystem mv + git rm; no Python, schema, or CLI change. learner/inbox/ (the per-instance drop zone scaffolded by `sensei init`) is unaffected."
status: done
date: 2026-04-26
---
# Plan: Relocate Maintainer Inbox Seed Content Out of Source Repo

The 2026-04-25 follow-up audit's recommendation #7: `inbox/` at the source-repo root holds 25 maintainer-curated seed files (`inbox/April-*.md` tech-interview prep notes) added in commits `b1ed6ac` and `edf8e01`. They're correctly excluded from the wheel by `ci/check_package_contents.py:67`'s `FORBIDDEN_PREFIXES` check, but they're not source-repo content in any meaningful sense — they're the maintainer's personal hints corpus, eligible for being dropped into a learner instance's `learner/inbox/` for triage by the hints protocol. Their presence in the sensei source repo conflates "source code + ops" with "seed content for exercising the hints feature."

The audit named three options (separate repo / `git update-index --skip-worktree` / leave-as-is with formal naming). The maintainer's choice: relocate to `/home/rosantos/workspace/platform/sensei-hints/tech-interview/`, a sibling directory under `platform/`. Whether `sensei-hints/` later becomes a git repo of its own is the maintainer's separate decision; this plan only ensures the files leave the sensei tree.

`learner/inbox/` (the per-instance drop zone scaffolded by `sensei init` per ADR-0019) is unaffected. That's a distinct concept — one created on every `sensei init`, holds learner-supplied content — from the source-repo `inbox/`, which is a one-shot maintainer corpus that's never shipped and never instantiated.

## Distinguishing the two `inbox/` concepts

| Concept | Location | Owner | Lifecycle | Touched by this plan? |
|---|---|---|---|---|
| Source-repo `inbox/` | `<sensei-source>/inbox/` | maintainer (private seed) | one-shot, manually curated | **yes — relocated and deleted** |
| Per-instance `learner/inbox/` | `<learner-instance>/learner/inbox/` | learner (drop zone) | created on every `sensei init` | no — unaffected |

`README.md:70`, `docs/foundations/personas/tomas.md:23`, and `docs/design/hints-ingestion.md:23` all describe the per-instance concept; they remain accurate.

## Tasks

- [x] T1 — Create the target directory: `mkdir -p /home/rosantos/workspace/platform/sensei-hints/tech-interview/`. Idempotent.
- [x] T2 — Move all 25 `.md` files from the sensei repo's top-level `inbox/` to the target with `mv -n` (no-clobber to refuse silent overwrite of any pre-existing target file). Verify count after move: 25 files at the target.
- [x] T3 — `git rm -r inbox/` from the sensei repo (the directory is empty after T2; git removes the tracked entries).
- [x] T4 — Add `/inbox/` to `.gitignore` (anchored to repo root with leading slash so unrelated paths like `tests/fixtures/inbox/` are not accidentally swept). One-line addition with a one-line comment pointing at this plan.
- [x] T5 — Run the full local pipeline from the project venv: `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_foundations.py && python ci/check_links.py && python ci/check_links.py --root src/sensei/engine && python ci/check_changelog_links.py && python ci/check_plan_completion.py`. All must stay green; this plan touches no code, schema, or referenced markdown.
- [x] T6 — Add row to `docs/plans/README.md` § Shipped index.
- [x] T7 — Commit message: `chore: relocate maintainer inbox/ seed content out of source repo`. Body cites this plan, the file count, the target path, and the distinction from `learner/inbox/`.

## Acceptance Criteria

- [x] AC1 — `test ! -e inbox` from the sensei repo root succeeds (the dir is gone).
- [x] AC2 — `ls /home/rosantos/workspace/platform/sensei-hints/tech-interview/ | wc -l` returns 25.
- [x] AC3 — `grep -n "/inbox/" .gitignore` returns the new line.
- [x] AC4 — `git ls-files inbox/` returns nothing (no tracked entries remain).
- [x] AC5 — Full local pipeline (T5) passes.
- [x] AC6 — `git diff --stat` shows 25 file deletions under `inbox/`, plus modifications to `.gitignore`, `docs/plans/README.md`, and the new plan file. No collateral.

## Out of Scope

- **Updating `docs/plans/hints-ingestion.md:18` T7** ("N/A — inbox/ files are source-repo seed data, not instance data"). That plan is `status: done`; per project convention completed plans are historical artifacts and are not re-edited. The statement was true at the time it was written; the new policy is recorded by this plan, not by overwriting the old one.
- **Initializing `/home/rosantos/workspace/platform/sensei-hints/` as its own git repo.** Separate decision the maintainer can make independently — `git init` is a one-line follow-up.
- **Adding the corpus to a `sensei-content` PyPI sibling.** Out of scope per the maintainer's stated preference (sibling directory, not a parallel package).
- **Touching `README.md:70`, `docs/foundations/personas/tomas.md:23`, or `docs/design/hints-ingestion.md:23`.** All three reference `learner/inbox/`; distinct concept.
- **CHANGELOG entry.** The user-visible release flow and wheel contents are unchanged; this is repo-internal cleanup, invisible to PyPI consumers.

## Risk and reversal

The 25 files remain tracked in git history (commits `b1ed6ac`, `edf8e01`). Recoverable via `git show <sha>:inbox/<filename>` or `git checkout <sha>~1 -- inbox/`. Relocation is reversible — the `/inbox/` gitignore line would also need to be reverted before re-adding files at the source-repo root.
