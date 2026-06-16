---
thing_id:        "synk-adr-0010"
thing_type:      "adr"
adr_id:          "0010"
domain:          "synk"
phase:           "p2-advanced-features"
version:         "1.0"
lifecycle_state: "approved"
deciders:        "Deepak"
reversibility:   "high"
decision_date:   "2026-06-16"
last_updated:    "2026-06-16"
next_review_date: "2026-09-16"
priority:        "medium"
confidentiality: "internal"
tags:            [merge, three-way, diff, conflict-resolution]
relations:
  depends_on:    ["synk-adr-0005"]
  related_to:    ["synk-moscow-0001"]
  enables:       []
---

# ADR-0010: 3-Way Merge Engine — Line-Based Myers with Overlap Detection

## Status

**Accepted** (2026-06-16). Implemented in v0.2.

## Context

Beyond Compare requires a merge (rather than diff) capability. Given a common BASE and two divergent
versions (LOCAL, REMOTE), Synk must produce a merged result and flag conflicts where both sides
changed the same lines.

## Decision

Implement a **line-based 3-way merge engine** using `difflib.SequenceMatcher` (variant of Myers) to
diff BASE→LOCAL and BASE→REMOTE, then walk both change sets left-to-right to detect overlaps.

## Rationale

- Three-way merge is a classic problem: diff BASE against both sides, then overlay the changes.
- `difflib.SequenceMatcher` is in stdlib and provides opcodes (equal/replace/delete/insert) with
  position ranges.
- Overlap detection: if changes from LOCAL and REMOTE touch the same BASE lines, they conflict.
  If disjoint, both are applied independently.
- Result is a list of `MergeHunk` objects tagged with `MergeOp` — the UI renders each hunk with
  appropriate styling.

## Consequences

**Positive:**
- Pure stdlib — no extra dependencies for the core merge algorithm.
- Conflict resolution is explicit: each hunk is auto-resolved or flagged CONFLICT.
- `to_text()` renders with Git-style conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).

**Negative:**
- `SequenceMatcher` is not guaranteed to produce a minimal diff — rare cases may produce
  surprising overlap groupings.
- Line-based only — no word-level or character-level conflict resolution.
- No support for binary file merge.

## Implementation

`src/core/merge.py` — `three_way_merge(base, local, remote) → MergeResult`.
`src/ui/merge_dialog.py` — `MergeDialog` with BASE/LOCAL/REMOTE panels and conflict navigation.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| Git's merge machinery (libgit2/pygit2) | Heavy dependency; C library build required |
| `diff3` CLI subprocess | Fragile; no structured output |
| word-diff merge | Adds complexity for marginal benefit — most code conflicts are line-level |
