# ADR-008: Strict Module Separation — core / ui / utils

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Synk has three distinct architectural concerns: comparison logic (hashing, diffing, merging), the graphical interface, and supporting utilities (config, session). Mixing these makes testing harder, prevents headless reuse, and couples the engine to Qt.

## Decision

Enforce a **strict three-layer module layout** with a one-way dependency rule:

```
src/
├── core/       # Pure logic — NO Qt imports. Testing: pytest (headless).
├── ui/         # Qt widgets — imports from core/, but NOT from utils/ (config is injected).
├── utils/      # Config, session I/O — pure Python, NO Qt imports.
└── cli.py      # Entry point — imports from core/ and ui/ (optional).
```

**Rule:** `core/` must never import from `ui/` or `utils/`. `utils/` must never import from `ui/` or `core/`. `ui/` may import from `core/` but not from `utils/` (config is injected via constructor/dependency injection).

## Rationale

- **Testability:** `core/` and `utils/` modules can be tested headless with pytest. No Qt display required.
- **Headless CLI:** `cli.py` uses `core/` for diff/hash/merge without importing `ui/` at all (unless `--gui` flag is passed).
- **Replaceable UI:** If PySide6 is later swapped for a TUI or web frontend, `core/` doesn't change.
- **Dependency injection:** `FilePane` receives config settings as parameters, not by importing `utils.config` — keeps modules decoupled and mockable.

## Consequences

**Positive:**
- All core tests run headless (`pytest -m "not gui"`) — fast CI, no X11/Wayland required
- CLI mode (`synk diff`, `synk hash`, `synk merge`) works on servers without a display
- A developer can work on the diff engine without installing Qt on their machine

**Negative:**
- Some duplication is unavoidable (e.g., `Status` enum is defined in `worker.py` for UI and used in core logic) — a shared `core/status.py` would reduce this
- Dependency injection adds boilerplate in `main_window.py` (constructing panes with injected config)
- The `--gui` flag in CLI requires conditional import that bypasses the module-level import check

## Current State

✅ `core/hasher.py` — no Qt imports
✅ `core/merge.py` — no Qt imports  
✅ `core/archive.py` — no Qt imports  
✅ `core/remote.py` — no Qt imports  
⚠️ `core/worker.py` — imports `PySide6.QtCore` (QRunnable, Signal) — accepted because this is the bridge layer
✅ `utils/config.py` — no Qt imports  
✅ `ui/` — imports from `core/` only

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Flat module layout (everything in one package) | Impossible to test headless; UI changes risk breaking core logic |
| Plugin architecture | Over-engineered for the current scale; adds interface boilerplate |
| Shared `models/` layer | Not enough shared data types to justify; would be a "dumping ground" |
