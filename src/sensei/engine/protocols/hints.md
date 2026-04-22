# Hints Triage Protocol — Executable

> **This is prose-as-code.** An LLM runtime reads this file, interprets the steps literally, and executes them. Do not paraphrase, reorder, or skip.

## Purpose

When the learner signals intent to process hints (e.g., "process my hints", "triage inbox"), scan the inbox for new files, extract topics, score relevance, deduplicate, cluster, register, and move. Report results.

## Paths

- Profile: `learner/profile.yaml` | Registry: `learner/hints/hints.yaml`
- Inbox: `learner/inbox/` | Active: `learner/hints/active/` | Archive: `learner/hints/archive/`
- Defaults: `.sensei/defaults.yaml` | Overrides: `learner/config.yaml`
- Decay: `.sensei/scripts/hint_decay.py`

Config keys (from `hints:` after deep-merge): `hints.half_life_days` (14.0), `hints.boost_weight` (1.5), `hints.max_boost` (2.0), `hints.cluster_threshold` (3), `hints.expire_threshold` (0.2), `hints.expire_after_days` (28), `hints.relevance_floor` (0.3).

UTC now: `date -u +%Y-%m-%dT%H:%M:%SZ`.

---

## Session Start Nudge

At session start: list `learner/inbox/`, compute SHA-256 per file, compare against registry `content_hash` values. If unregistered files exist, say:

> You have N unprocessed item(s) in your inbox. Want me to triage them?

Do not block. Then run decay recomputation:

```
.sensei/run hint_decay.py \
  --hints-file learner/hints/hints.yaml \
  --half-life-days <hints.half_life_days> \
  --expire-threshold <hints.expire_threshold> \
  --expire-after-days <hints.expire_after_days> \
  --now <utc>
```

`hint_decay.py` recomputes `freshness` and marks any active/triaged hint as `status: expired` when freshness drops below `hints.expire_threshold` or age exceeds `hints.expire_after_days`. Read the updated list from stdout and write it back to `learner/hints/hints.yaml`. For any entry now `status: expired`, move the file from `learner/hints/active/` to `learner/hints/archive/`.

---

## Step 1 — Scan

List `learner/inbox/`. Compute SHA-256 of each file. Collect files with no matching `content_hash` or `file` path in registry. If none: say "Inbox is empty — nothing to triage." Stop.

## Step 2 — Parse

For each new file: extract YAML frontmatter (between `---` delimiters) if present. Read content body. If frontmatter missing, infer from filename pattern `Month-DD_HH-MM_Title.md`: date from `Month-DD` (current year), title from `Title` segment (hyphens → spaces). If pattern doesn't match, leave metadata empty.

## Step 3 — Extract topics

Identify 1–5 concrete learning topics from content. Topics must be specific noun phrases or technical terms matchable against `expertise_map` slugs in profile. Derive from content, not filename alone.

## Step 4 — Score relevance

Read learner's `goal` from `learner/profile.yaml`. Score each file 0.0–1.0 (max of its topic scores): 1.0 = directly matches goal, 0.5 = tangentially related, 0.0 = no connection.

## Step 5 — Deduplicate

Three layers, in order:

1. **File-level:** `content_hash` matches any registry entry (including archived) → skip entirely.
2. **Topic-level:** >80% topic overlap with existing `active`/`triaged` entry → ask learner: "[filename]" overlaps with "[existing]". Keep both or skip? Act on response.
3. **Absorption-level:** ALL extracted topics have mastery ≥ 0.8 in profile `expertise_map` → set status `irrelevant`, register, move directly to archive.

## Step 6 — Cluster

Compare topics against existing active hints. ≥60% topic overlap → assign same cluster name. Otherwise create new cluster name from dominant topic.

## Step 7 — Register

Append to `learner/hints/hints.yaml`:

```yaml
- file: hints/active/<filename>
  ingested: <utc-date>
  relevance: <0.0-1.0>
  topics: [<topic-1>, ...]
  cluster: <cluster-name>
  status: active
  freshness: 1.0
  content_hash: <sha256>
```

If relevance < `hints.relevance_floor`: status → `irrelevant`, file path → `hints/archive/<filename>`.

## Step 8 — Move

Status `active` → move from `learner/inbox/` to `learner/hints/active/`. Status `irrelevant` → move to `learner/hints/archive/`.

## Step 9 — Report

Say:

> **Triage complete.** Processed N file(s). Active: X | Duplicates flagged: Y | Irrelevant: Z | Clusters: [names]

If 3+ hints cluster on a topic NOT in curriculum, append:

> You've saved N items about "[topic]". Add it to your plan?

---

## Curriculum Boosting

After triage (or session start after decay), for each active hint with relevance > 0.5:

```
topic_priority += relevance * freshness * hints.boost_weight
```

Cap total boost per topic at `hints.max_boost`. If 3+ active hints cluster on a topic absent from curriculum, surface it to the learner for acceptance.

## Feedback Handling

- **Implicit:** Learner studies a topic matching an active hint's topics → status `absorbed`, set `acted_on`, move to archive.
- **Explicit:** Learner says "not relevant" → status `irrelevant`, move to archive.

Both are final. Archived hints remain in registry for deduplication.

## Error Handling

| Condition | Response |
|---|---|
| `learner/inbox/` missing | Create it. Say: "Created your inbox folder." |
| `learner/hints/hints.yaml` missing | Create as empty list `[]`. |
| File unreadable | Skip, report: "Skipped [filename]: unreadable." |
| Profile missing/invalid | Say: "Cannot triage — profile is missing or invalid." Stop. |
| Decay helper fails | Log warning, skip freshness recomputation, continue. |

## References

- Spec: `docs/specs/hints.md`
- Design: `docs/design/hints-ingestion.md`
