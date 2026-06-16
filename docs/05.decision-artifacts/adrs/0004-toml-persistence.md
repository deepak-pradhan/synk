---
thing_id:        "synk-adr-0004"
thing_type:      "adr"
adr_id:          "0004"
domain:          "synk"
phase:           "p0-foundations"
version:         "1.0"
lifecycle_state: "approved"
deciders:        "Deepak"
reversibility:   "high"
decision_date:   "2026-06-14"
last_updated:    "2026-06-16"
next_review_date: "2026-09-16"
priority:        "medium"
confidentiality: "internal"
tags:            [config, persistence, toml, session]
relations:
  depends_on:    []
  related_to:    ["synk-adr-0012"]
  enables:       []
---

# ADR-0004: TOML for Config and Session Persistence

## Status

**Accepted** (2026-06-14). Implemented in v0.1 M6 (settings) and M9 (sessions).

## Context

Synk needs to persist: (1) settings/configuration — hash algorithm, theme, font size, ignore
patterns; (2) sessions — left/right paths, filter state, comparison options; (3) last session —
auto-saved on exit, optionally restored on launch.

## Decision

Use **TOML** for all persistence, with `tomllib` (stdlib) for reading and `tomli-w` for writing.

## Rationale

- TOML is the modern standard for Python config (PEP 621). `tomllib` has been stdlib since
  Python 3.11.
- More readable than JSON (comments, dates, multi-line strings) and safer than YAML (no arbitrary
  code execution).
- `tomli-w` is a tiny, pure-Python writer with no dependencies beyond stdlib.
- Human-editable: users can modify `~/.config/beyondcomp/config.toml` directly.
- Single format for both config and sessions reduces cognitive overhead.

## Consequences

**Positive:**
- Zero dependencies for reading configs (`tomllib` is built-in).
- `tomli-w` is ~200 lines of pure Python.
- `.bc-session` files are plain TOML — users can version-control them.

**Negative:**
- `tomllib` is read-only — must depend on `tomli-w` for writes.
- TOML's type system is strict (no heterogeneous arrays, no `null`).
- Less compact than JSON for large session files.

## Implementation

`src/utils/config.py` — reads `~/.config/beyondcomp/config.toml`.
`src/utils/session.py` — reads/writes `.bc-session` files.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| JSON | No comments, no dates, harder to hand-edit |
| YAML | Parsing ambiguity, security concerns, requires PyYAML dep |
| INI | No nested sections, no arrays, no booleans |
| SQLite | Overkill for ~50 settings; schema migration complexity |
