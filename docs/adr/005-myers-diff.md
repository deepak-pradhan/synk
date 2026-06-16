# ADR-005: Myers Diff Algorithm via diff-match-patch

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

When files differ by hash, Synk needs to show the user _how_ they differ — line-by-line or character-level inline diff. The diff algorithm determines the quality of the output (minimal edit script, readability) and performance on large files.

## Decision

Use the **Myers O(ND) diff algorithm** via the `diff-match-patch` Python package.

## Rationale

- Myers' algorithm produces a *minimal* edit script (shortest edit distance), which gives the most intuitive diff output for code and text files.
- `diff-match-patch` implements Myers with semantic cleanup (`diff_cleanupSemantic`) — produces diffs that align with natural language boundaries, avoiding fragmented single-character changes.
- The library is pure Python, well-tested, and has no external dependencies.
- Handles text and supports conversion to HTML for rich-text display in the diff dialog.

## Consequences

**Positive:**
- High-quality diffs — minimal, semantically clean edit scripts
- Pure Python — no native compilation needed, easy to install
- Also provides patch application (`patch_apply`) — useful for future merge-to-file operations

**Negative:**
- Myers is O(ND) in time and O(D) in space — very large files (>100k lines) may cause memory pressure
- Pure Python is slower than C-based `difflib` for naive use, but `diff-match-patch` performs comparably for files under 10k lines (the common case)
- No built-in syntax highlighting — the diff dialog renders plain text with color-coded insertions/deletions

## Usage

```python
from diff_match_patch import diff_match_patch

dmp = diff_match_patch()
diffs = dmp.diff_main(text1, text2)
dmp.diff_cleanupSemantic(diffs)

for op, text in diffs:
    if op == -1:  # deletion (left-only in side-by-side)
    elif op == 1: # insertion (right-only in side-by-side)
    else:         # equal
```

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| `difflib.SequenceMatcher` (Python stdlib) | Produces non-minimal diffs; "junk" heuristic can skip meaningful changes; no semantic cleanup |
| `difflib.unified_diff` | Text-only output, no structured data for custom rendering |
| `google-diff-patch-apply` (fork of same) | Same algorithm; `diff-match-patch` has better Python packaging and more active maintenance |
| Patience Diff (Git's algorithm) | Better for code with long common context, but no standalone Python package with maintainer |
