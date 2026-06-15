# Merge Concepts: 2-Way Diff vs 3-Way Merge

## 2-Way Diff

Compares two files or directories directly, showing what is different between them.

**Use case:** Quick comparisons — "Is file A the same as file B?"

**Panels:**
```
┌──────────────┬──────────────┐
│   FILE A     │   FILE B     │
│ (left side)  │ (right side) │
├──────────────┼──────────────┤
│ hello world  │ hello mars   │  ← shows difference
│ foo bar      │ foo bar      │  ← identical lines
│ baz qux      │ baz qux      │
└──────────────┴──────────────┘
```

**Limitation:** When both files changed from a common starting point, you cannot tell which change belongs to which side. You only see that they differ now.

**When to use:**
- Verifying a copy is identical
- Comparing two arbitrary files
- Directory synchronization (file present/absent, hash mismatch)

---

## 3-Way Merge

Compares two divergent versions against their common ancestor (the BASE), then produces a merged result.

**Use case:** Resolving conflicts — "You and another person both edited the same file. What changed, and which version should win?"

**Panels:**
```
┌──────────────┬──────────────┬──────────────┐
│     BASE     │    LOCAL     │    REMOTE    │
│  (ancestor)  │  (my edit)   │ (their edit) │
├──────────────┼──────────────┼──────────────┤
│ hello world  │ hello world  │ hello mars   │
│ foo bar      │ foo baz      │ foo bar      │
│ baz qux      │ baz qux      │ baz qux      │
└──────────────┴──────────────┴──────────────┘
              ↓
        ┌──────────────┐
        │    MERGED    │  ← user chooses which side wins per conflict
        │              │
        │ hello world  │  ← take LOCAL (or REMOTE, or edit manually)
        │ foo baz      │  ← take LOCAL (only LOCAL changed this)
        │ baz qux      │  ← unchanged from BASE
        └──────────────┘
```

**Advantage:** You can see *who changed what relative to the original*. If only LOCAL changed a line, you know it's safe to keep. If both LOCAL and REMOTE changed the same line, that's a **conflict** — you decide.

**Conflict detection:**
| BASE | LOCAL | REMOTE | Action |
|------|-------|--------|--------|
| `hello world` | `hello mars` | `hello world` | Take LOCAL (only LOCAL changed it) |
| `hello world` | `hello world` | `hello mars` | Take REMOTE (only REMOTE changed it) |
| `hello world` | `hello mars` | `hello jupiter` | **CONFLICT** — both changed it |
| `hello world` | `hello world` | `hello world` | Unchanged — keep BASE |

**When to use:**
- Git merge conflicts (`git mergetool`)
- Pull request conflict resolution
- Reconciling divergent config files
- Any scenario where two versions diverged from a common origin

---

## Summary

| Feature | 2-Way Diff | 3-Way Merge |
|---------|-----------|-------------|
| Panels | 2 (A vs B) | 3 (BASE + LOCAL + REMOTE) + merged output |
| Use case | "Are these different?" | "How do I combine these changes?" |
| Conflict resolution | Manual, no context | Automatic for non-overlapping changes; highlighted for conflicts |
| Common tools | `diff`, `meld`, `kompare` | Beyond Compare, kdiff3, IntelliJ, VS Code |
| Pro tier? | Usually free | Usually paid / advanced |

## In Synk

**Current (v0.1):** 2-way file diff, 2-way directory comparison.

**Planned:** 3-way merge view with BASE/LOCAL/REMOTE panels and conflict-resolution actions (take left, take right, take both, edit inline).
