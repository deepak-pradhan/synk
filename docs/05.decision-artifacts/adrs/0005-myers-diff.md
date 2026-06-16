---
thing_id:        "synk-adr-0005"
thing_type:      "adr"
adr_id:          "0005"
domain:          "synk"
phase:           "p0-foundations"
version:         "1.0"
lifecycle_state: "approved"
deciders:        "Deepak"
reversibility:   "high"
decision_date:   "2026-06-14"
last_updated:    "2026-06-16"
next_review_date: "2026-09-16"
priority:        "high"
confidentiality: "internal"
tags:            [diff, algorithm, myers, diff-match-patch]
relations:
  depends_on:    []
  related_to:    ["synk-adr-0010"]
  enables:       []
---

# ADR-0005: Myers Diff Algorithm via diff-match-patch

## Status

**Accepted** (2026-06-14). Verified in v0.1 M3 (diff dialog) and v0.2 (CLI diff).

## Context

When files differ by hash, Synk needs to show the user _how_ they differ — line-by-line or
character-level inline diff. The diff algorithm determines the quality of the output (minimal edit
script, readability) and performance on large files.

## Decision

Use the **Myers O(ND) diff algorithm** via the `diff-match-patch` Python package.

## Rationale

- Myers' algorithm produces a *minimal* edit script (shortest edit distance), giving the most
  intuitive diff output for code and text files.
- `diff-match-patch` implements Myers with semantic cleanup (`diff_cleanupSemantic`) — produces
  diffs that align with natural language boundaries.
- Pure Python, well-tested, no external dependencies.
- Supports conversion to HTML for rich-text display in the diff dialog.

## Consequences

**Positive:**
- High-quality diffs — minimal, semantically clean edit scripts.
- Pure Python — no native compilation needed.
- Also provides patch application (`patch_apply`) for future merge-to-file operations.

**Negative:**
- Myers is O(ND) time and O(D) space — very large files (>100k lines) may cause memory pressure.
- Pure Python is slower than C-based alternatives for naive use.
- No built-in syntax highlighting — diff dialog renders plain text with color-coded changes.

## Implementation

```python
dmp = diff_match_patch()
diffs = dmp.diff_main(text1, text2)
dmp.diff_cleanupSemantic(diffs)
```

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| `difflib.SequenceMatcher` | Produces non-minimal diffs; no semantic cleanup |
| `difflib.unified_diff` | Text-only output, no structured data for custom rendering |
| Patience Diff (Git's algorithm) | No standalone Python package with active maintenance |
