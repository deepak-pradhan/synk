# ADR-001: Python + PySide6 (Qt6) as UI Framework

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Synk needs a cross-platform GUI with tree views, drag-and-drop, rich text display, and dialog support. The framework choice determines development velocity, packaging complexity, and platform reach.

## Decision

Use **Python 3.12+** with **PySide6** (Qt6 official bindings, LGPL licensed).

## Rationale

- **Python** gives rapid prototyping, a mature stdlib (`pathlib`, `hashlib`), and direct access to the diff/hash libraries without FFI.
- **PySide6** (vs PyQt6) is LGPL-licensed, which aligns with MIT distribution without licensing conflicts.
- Qt's `QTreeView`, `QSplitter`, `QTextEdit`, and `QDrag` provide the exact widgets needed for side-by-side comparison without custom widget development.
- `QThreadPool` + `QRunnable` enables non-blocking background comparison (see ADR-003).
- The trade-off (larger package, slower startup vs a native toolkit) is acceptable for a developer-focused tool.

## Consequences

**Positive:**
- Full cross-platform support (Linux, macOS, Windows) from a single codebase
- Mature widget ecosystem — no need to build tree views, split panes, or drag-and-drop from scratch
- LGPL license allows MIT-licensed distribution without GPL contagion

**Negative:**
- Larger distribution size (PySide6 wheels are ~50 MB)
- Slightly slower startup than native or TUI alternatives
- Qt6 system dependencies may not be present on minimal headless servers (but CLI mode works without Qt — see ADR-009)

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| PyQt6 | GPL/commercial license conflicts with MIT distribution |
| Dear ImGui (pyimgui) | Immediate-mode GUI requires custom widget management; no tree view built-in |
| Tauri + Svelte | Web-based UI is overkill for a file comparison tool; heavier build chain |
| TUI (Textual / urwid) | No visual diff capabilities; poor mouse/drag support |
| tkinter | Outdated widget set; no native tree view with drag-and-drop |
