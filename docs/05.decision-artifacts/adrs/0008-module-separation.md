---
thing_id:        "synk-adr-0008"
thing_type:      "adr"
adr_id:          "0008"
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
tags:            [architecture, module-structure, separation-of-concerns, testability]
relations:
  depends_on:    ["synk-adr-0001"]
  related_to:    ["synk-adr-0009"]
  enables:       []
---

# ADR-0008: Strict Module Separation — core / ui / utils

## Status

**Accepted** (2026-06-14). Enforced from v0.1 prototype onward.

## Context

Synk has three distinct architectural concerns: comparison logic (hashing, diffing, merging), the
graphical interface, and supporting utilities (config, session). Mixing these makes testing harder,
prevents headless reuse, and couples the engine to Qt.

## Decision

Enforce a **strict three-layer module layout** with a one-way dependency rule:

```
src/
├── core/       # Pure logic — NO Qt imports. Testing: pytest (headless).
├── ui/         # Qt widgets — imports from core/, not from utils/.
├── utils/      # Config, session I/O — pure Python, NO Qt imports.
└── cli.py      # Entry point — imports from core/ and ui/ (optional).
```

**Rule:** `core/` never imports from `ui/` or `utils/`. `utils/` never imports from `ui/` or
`core/`. `ui/` imports from `core/` but not from `utils/` (config injected via constructor).

## Rationale

- **Testability:** `core/` and `utils/` can be tested headless with pytest.
- **Headless CLI:** `cli.py` uses `core/` without importing `ui/` (unless `--gui` flag).
- **Replaceable UI:** If PySide6 is later swapped for TUI or web frontend, `core/` doesn't change.
- **Dependency injection:** `FilePane` receives config as parameters, not by importing `utils.config`.

## Consequences

**Positive:**
- All core tests run headless (`pytest -m "not gui"`) — fast CI, no display required.
- CLI mode works on servers without a display.
- Developer can work on diff engine without installing Qt.

**Negative:**
- Some duplication unavoidable (e.g., `Status` enum in both worker and UI).
- Dependency injection adds boilerplate in `main_window.py`.
- `--gui` flag in CLI requires conditional import.

## Implementation

✅ `core/hasher.py` — no Qt imports.
✅ `core/merge.py` — no Qt imports.
✅ `core/archive.py` — no Qt imports.
✅ `core/remote.py` — no Qt imports.
⚠️ `core/worker.py` — imports `PySide6.QtCore` (bridge layer — accepted).
✅ `utils/config.py` — no Qt imports.
✅ `ui/` — imports from `core/` only.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| Flat module layout | Cannot test headless; UI changes risk breaking core logic |
| Plugin architecture | Over-engineered for current scale |
