---
thing_id:        "synk-adr-0012"
thing_type:      "adr"
adr_id:          "0012"
domain:          "synk"
phase:           "p1-core-features"
version:         "1.0"
lifecycle_state: "approved"
deciders:        "Deepak"
reversibility:   "high"
decision_date:   "2026-06-15"
last_updated:    "2026-06-16"
next_review_date: "2026-09-16"
priority:        "low"
confidentiality: "internal"
tags:            [session, schema, persistence, toml]
relations:
  depends_on:    ["synk-adr-0004"]
  related_to:    []
  enables:       []
---

# ADR-0012: Session Schema Design

## Status

**Accepted** (2026-06-15). Implemented in v0.1 M9.

## Context

Users can save and load comparison sessions. The session file must capture the full comparison state:
which directories were compared, what filters were active, and what the view settings were.

## Decision

Define a `.bc-session` TOML schema with three sections and a version field:

```toml
[general]
version = 1

[paths]
left = "/home/user/project-a"
right = "/home/user/project-b"

[settings]
ignore_patterns = ["*.pyc", ".git/", "__pycache__/"]
show_identical = false
hash_algorithm = "xxh3_64"
theme = "light"
```

## Rationale

- TOML is already used for config (ADR-0004) — one less format to learn.
- Sections map cleanly to concerns: `[paths]` are targets, `[settings]` is the View + Comparison
  config.
- `version` field enables future schema migrations (e.g., adding `expanded_dirs`).
- `.bc-session` extension distinguishes Synk files from generic `.toml`.
- On launch, Synk checks for `~/.config/beyondcomp/last_session.toml` and prompts restore.

## Consequences

**Positive:**
- Human-readable — users can inspect, edit, or share session files.
- Version field enables forward-compatible schema upgrades.
- Auto-save on exit + restore prompt provides zero-friction workflow continuity.

**Negative:**
- Session file doesn't capture comparison *results* — must re-compare on load.
- No support for per-pane archive/sftp prefixes (e.g., `archive:/path/to/backup.zip`).
- Version field is not yet validated — future schema change must add migration logic.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| JSON | Less readable, no comments, no date types |
| Pickle/Marshal | Not human-readable, version-sensitive, security risk |
| YAML | Requires PyYAML dependency |
| SQLite export | Over-engineered for a 10-entry config file |
