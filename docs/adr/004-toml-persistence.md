# ADR-004: TOML for Config and Session Persistence

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Synk needs to persist:
1. **Settings/configuration** — hash algorithm, theme, font size, ignore patterns
2. **Sessions** — left/right paths, filter state, comparison options
3. **Last session** — auto-saved on exit, optionally restored on launch

The format must be human-readable, easy to edit manually, and have Python stdlib support.

## Decision

Use **TOML** for all persistence, with `tomllib` (stdlib) for reading and `tomli-w` for writing.

## Rationale

- TOML is the modern standard for Python config (PEP 621). `tomllib` has been stdlib since Python 3.11.
- More readable than JSON (comments, dates, multi-line strings) and safer than YAML (no arbitrary code execution).
- `tomli-w` is a tiny, pure-Python writer with no dependencies beyond stdlib — ideal for writing config files from the Settings dialog.
- Human-editable: users can modify `~/.config/beyondcomp/config.toml` directly to tweak options not exposed in the UI.
- Single format for both config and sessions reduces cognitive overhead.

## Consequences

**Positive:**
- Zero dependencies for reading configs (`tomllib` is built-in)
- `tomli-w` is 200 lines of pure Python — minimal maintenance risk
- `.bc-session` files are plain TOML — users can version-control them

**Negative:**
- `tomllib` is read-only — must vendor or depend on `tomli-w` for writes
- TOML's type system is strict (no heterogeneous arrays, no `null`) — requires schema discipline
- Less compact than JSON for large session files (but sessions are small)

## Implementation

`src/utils/config.py` — reads `~/.config/beyondcomp/config.toml`:

```toml
[general]
theme = "light"
font_size = 10

[comparison]
hash_algorithm = "xxh3_64"
context_lines = 3

[ignore]
patterns = ["*.pyc", ".git/", "__pycache__/"]
show_identical = true
```

`src/utils/session.py` — reads/writes `.bc-session` files:

```toml
left_path = "/home/user/project-a"
right_path = "/home/user/project-b"
ignore_patterns = ["*.pyc"]
show_identical = true
theme = "light"
```

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| JSON | No comments, no date types, harder to hand-edit |
| YAML | Parsing ambiguity, security concerns (arbitrary code in old versions), requires PyYAML dep |
| INI | No nested sections, no arrays, no booleans — awkward for ignore patterns list |
| SQLite | Overkill for ~50 settings; adds schema migration complexity |
