---
status: accepted
date: 2026-04-20
---
# Release Communication

## Intent

Every Sensei release is accompanied by a curated "what changed" artifact so that a user running `pip install sensei-tutor==X.Y.Z` — or a maintainer reading git history a year from now — can determine what is different from the previous version without reconstructing it from the commit log. This spec captures the product-level guarantees the project makes about release communication. The mechanism lives in [`docs/operations/release-playbook.md`](../operations/release-playbook.md); the enforcement of mechanical invariants lives in `ci/check_package_contents.py`.

Release communication is a product contract, not merely an operational convenience. A release without a curated summary of what it contains is a broken release — the user does not know what they installed.

## Invariants

- **Changelog presence.** `CHANGELOG.md` exists at the repo root, is part of the sdist, and is readable from the built artifact. Every public version appears in it with a dated entry. A release attempted without an entry for the target version is a release-blocking error (enforced by `ci/check_package_contents.py`).
- **Changelog format stability.** Entries follow [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/) sectioning — `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`, with semver-aligned `## [X.Y.Z] — YYYY-MM-DD` headings. The `## [Unreleased]` section sits at the top of the file. Changing the format is a spec-level change; it requires editing this spec.
- **Unreleased accumulation.** User-visible changes are appended to `## [Unreleased]` in the same PR (or commit on main) that introduces them, not batched at release time. At release time, the Unreleased content is promoted to the new version heading with today's date.
- **Changelog authority.** For any released version, `CHANGELOG.md` at the tagged commit is the canonical "what changed" artifact. GitHub Release notes and the PyPI long-description are derived views — they are copies or subsets of the changelog entry; they do not contradict it. If they differ, the changelog wins.
- **GitHub Release parity.** Every tag that matches the release tag filter earns a GitHub Release within the same maintainer session as the tag push. The Release body contains at minimum the `CHANGELOG.md` section for that version (copied verbatim) plus a `pip install sensei-tutor==X.Y.Z` install hint.
- **Yank visibility.** When a release is yanked on PyPI, a follow-up commit amends that version's `CHANGELOG.md` entry with a line `**Yanked:** <reason, link to fix version>`. The entry itself is never deleted.
- **User-visible scope.** The changelog records only user-visible changes: CLI behaviour, installed bundle contents, schema changes, public Python surface, supported Python versions, documented defaults. Pure refactors, internal tests, and documentation-only edits that do not change observable behaviour do not require an entry.
- **No hidden promises.** Additional communication channels — mailing lists, blog posts, social announcements, curated PyPI long-description updates, RSS feeds — are explicitly out of scope. If added later, they must earn their place in a new version of this spec or a superseding spec.

## Rationale

**Canonical changelog authority** mirrors the pattern of `CHANGELOG.md` as the single source of truth that successful Python ecosystems (pip itself, hatch, pypa's own projects) converge on. The GitHub Release and PyPI description are presentation surfaces; the file in the sdist is the auditable record.

**Keep a Changelog 1.1** was chosen because it is the de-facto standard for Python packages, requires zero tooling, and the sectioning maps cleanly to what users actually want to know (breaking changes, new features, fixes). Home-grown formats drift; Keep a Changelog is frozen.

**Unreleased accumulation** (appending in the feature PR rather than writing at release time) exists to prevent the "we'll write it later" failure mode. By the time a release is cut, the changelog entry is already written; release day becomes promotion, not authorship.

**Mechanical enforcement** (`check_package_contents.py` rejects a wheel whose tag has no changelog entry) is what converts a spec invariant from aspiration to contract. Without enforcement, the spec is vibes.

**Yank-with-amendment-not-deletion** matches the PyPI model (yanked versions are hidden from unpinned installs but remain installable for anyone who pinned). A user who pinned a yanked version should find an explanation in the changelog, not a hole.

## Out of Scope

- **Choice of release-notes automation.** Conventional Commits, `git-cliff`, `semantic-release`, Changie, towncrier — none are required, and Sensei adopts none at v1. This spec is compatible with any of them being added later; the file format stays the same.
- **Commit-message conventions** (beyond preferring [Conventional Commits](https://www.conventionalcommits.org/) as a loose convention documented in `AGENTS.md`). No CI gate on commit messages; no commitlint.
- **Long-description regeneration.** The PyPI project description is static prose in `pyproject.toml` / `README.md`; automatic regeneration per release is out of scope.
- **Cryptographic signing of the changelog.** Sigstore and PEP 740 attestations are already out of scope in the release-process spec; same here.
- **Announcement channels beyond GitHub Release.** A mailing list, blog, or social feed is the maintainer's prerogative, not a project promise.

## Decisions

- [ADR-0004: Sensei Distribution Model](../decisions/0004-sensei-distribution-model.md) — the sdist this spec says `CHANGELOG.md` ships inside.
- [Release Process spec](release-process.md) — this spec complements it; together they bind the release surface.
- Design: there is no separate design doc. The mechanism is thin (add file, extend validator, update playbook) and is described in the plan that implements this spec.

## References

- [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/)
- [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
