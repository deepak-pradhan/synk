# ADR-010: 3-Way Merge Engine — Line-Based Myers with Overlap Detection

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Beyond Compare requires a merge (rather than diff) capability. Given a common BASE and two divergent versions (LOCAL, REMOTE), Synk must produce a merged result and flag conflicts where both sides changed the same lines.

## Decision

Implement a **line-based 3-way merge engine** using `difflib.SequenceMatcher` (variant of Myers) to diff BASE→LOCAL and BASE→REMOTE, then walk both change sets left-to-right to detect overlaps.

## Rationale

- Three-way merge is a classic problem with a well-known algorithm: diff BASE against both sides, then overlay the changes.
- `difflib.SequenceMatcher` is in stdlib and provides opcodes (equal/replace/delete/insert) with position ranges — sufficient for change extraction.
- Overlap detection: if changes from LOCAL and REMOTE touch the same BASE lines (share a start/end range), they conflict. If they're disjoint, both are applied independently.
- The result is a list of `MergeHunk` objects, each tagged with `MergeOp` (BASE/LOCAL/REMOTE/CONFLICT) — the UI renders each hunk with appropriate styling.

## Consequences

**Positive:**
- Pure stdlib — no extra dependencies for the core merge algorithm
- Conflict resolution is explicit: each hunk is auto-resolved (LOCAL/REMOTE) or flagged as CONFLICT for user decision
- `to_text()` renders with Git-style conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) — compatible with Git's merge format

**Negative:**
- `SequenceMatcher` is not guaranteed to produce a minimal diff (unlike true Myers) — in rare cases, overlapping changes may be disjointed differently than a human would expect
- Line-based only — no word-level or character-level conflict resolution
- No support for binary file merge (displayed as "Binary files differ")

## Implementation

`src/core/merge.py`:

```python
@dataclass
class MergeHunk:
    op: MergeOp
    base_lines: tuple[str, ...]
    local_lines: tuple[str, ...]
    remote_lines: tuple[str, ...]
    merged_lines: tuple[str, ...]

def three_way_merge(base: str, local: str, remote: str) -> MergeResult:
    # 1. Diff base→local and base→remote
    # 2. Sort changes by start position in base
    # 3. Walk base left-to-right, apply non-overlapping, flag overlapping as CONFLICT
```

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Git's merge machinery (libgit2/pygit2) | Heavy dependency for a single feature; C library build required |
| `diff3` command-line subprocess | Fragile; no structured output; can't control merge strategy |
| `difflib.SequenceMatcher` with `ndiff` | Produces character-level comparison, not structured per-line merge hunks |
| word-diff merge | Adds complexity for marginal benefit — most code conflicts are line-level |
