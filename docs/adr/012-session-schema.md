# ADR-012: Session Schema Design

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Users can save and load comparison sessions. The session file must capture the full comparison state to restore a session exactly as it was left: which directories were compared, what filters were active, and what the view settings were.

## Decision

Define a `.bc-session` TOML schema with three sections:

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

- TOML is already used for config (see ADR-004) — one less format to learn.
- Sections map cleanly to concerns: `[paths]` are the comparison targets, `[settings]` is the View + Comparison config.
- `version` field in `[general]` enables future schema migrations (e.g., adding `left_pane_filters` or `expanded_dirs`).
- `.bc-session` extension distinguishes Synk files from generic `.toml`.
- On launch, Synk checks for `~/.config/beyondcomp/last_session.toml` and prompts the user to restore.

## Consequences

**Positive:**
- Human-readable — users can inspect, edit, or share session files
- Version field enables forward-compatible schema upgrades
- Auto-save on exit + restore prompt provides zero-friction workflow continuity

**Negative:**
- Session file doesn't capture the _results_ of comparison (file list, hashes, status) — must re-compare on load
- No support for saving per-pane archive/sftp prefixes (e.g., `left = "archive:/path/to/backup.zip"`) — the current schema assumes local filesystem paths
- Version field is not yet validated — a future schema change must add migration logic

## Future Schema (planned)

```toml
[general]
version = 2

[paths]
left = "archive:/home/user/backup.zip"
right = "sftp://user@host:/data/production"

[settings]
ignore_patterns = ["*.pyc"]
show_identical = false
hash_algorithm = "xxh3_64"
theme = "dark"
font_size = 11
context_lines = 5

[view]
expanded_dirs = ["src/core", "src/ui"]
left_pane_width = 400
right_pane_width = 400
```

## Implementation

`src/utils/session.py` — `save_session()` and `load_session()` using `tomli-w` / `tomllib`.

The `MainWindow` serializes its current state into the schema on save and applies the loaded values on restore (set paths, apply filters, trigger comparison).

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| JSON schema | Less readable, no comments, no date types |
| Pickle/Marshal | Not human-readable, version-sensitive, security risk (arbitrary code execution) |
| YAML | Requires PyYAML dependency; parsing ambiguity |
| SQLite export | Over-engineered for a 10-entry config file |
