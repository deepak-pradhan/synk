---
thing_id:        "synk-adr-0001"
thing_type:      "adr"
adr_id:          "0001"
domain:          "synk"
phase:           "p0-foundations"
version:         "1.0"
lifecycle_state: "approved"
deciders:        "Deepak"
reversibility:   "medium"
decision_date:   "2026-06-14"
last_updated:    "2026-06-16"
next_review_date: "2026-09-16"
priority:        "high"
confidentiality: "internal"
tags:            [gui, python, pyside6, qt6, ui-framework]
relations:
  depends_on:    []
  related_to:    ["synk-adr-0008", "synk-adr-0009"]
  enables:       ["synk-adr-0003"]
---

# ADR-0001: Python + PySide6 (Qt6) as UI Framework

## Status

**Accepted** (2026-06-14). Ratified as the first architecture decision during the
prototyping phase. Implementation verified in v0.1.

## Context

Synk needs a cross-platform GUI with tree views, drag-and-drop, rich text display, and dialog
support. The framework choice determines development velocity, packaging complexity, and platform
reach.

## Decision

Use **Python 3.12+** with **PySide6** (Qt6 official bindings, LGPL licensed).

## Rationale

- **Python** gives rapid prototyping, a mature stdlib (`pathlib`, `hashlib`), and direct access
  to diff/hash libraries without FFI.
- **PySide6** (vs PyQt6) is LGPL-licensed, aligning with MIT distribution without licensing
  conflicts.
- Qt's `QTreeView`, `QSplitter`, `QTextEdit`, and `QDrag` provide the exact widgets needed for
  side-by-side comparison without custom widget development.
- `QThreadPool` + `QRunnable` enables non-blocking background comparison (see ADR-0003).
- The trade-off (larger package, slower startup vs native toolkit) is acceptable for a
  developer-focused tool.

## Consequences

**Positive:**
- Full cross-platform support (Linux, macOS, Windows) from a single codebase.
- Mature widget ecosystem — no need to build tree views, split panes, or DnD from scratch.
- LGPL license allows MIT-licensed distribution without GPL contagion.

**Negative:**
- Larger distribution size (PySide6 wheels ~50 MB).
- Qt6 system dependencies may not be present on headless servers (mitigated by CLI mode — ADR-0009).
- Slower startup than native or TUI alternatives.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| PyQt6 | GPL/commercial license conflicts with MIT distribution |
| Dear ImGui (pyimgui) | No tree view built-in; requires custom widget management |
| Tauri + Svelte | Heavier build chain; web UI is overkill for file comparison |
| TUI (Textual / urwid) | No visual diff capabilities; poor mouse/drag support |
| tkinter | Outdated widget set; no native tree view with DnD |

## Next Steps

1. ✅ Prototype the side-by-side split pane in M1.
2. ✅ Implement tree view with custom model in M1–M2.
3. ✅ Verify worker thread compatibility (M2).
