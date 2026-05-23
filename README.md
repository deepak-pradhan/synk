# Beyond Compare Clone

A personal file/folder comparison utility for Linux, similar to Beyond Compare.

**Status:** Prototype. Core features working: side-by-side panes, hash comparison, diff dialog, file operations, settings persistence, session save/load, context menus, drag-and-drop, archive browsing.

## Stack

- Python 3.12+ / PySide6 (Qt6)
- diff-match-patch (Myers diff algorithm)
- xxHash (content hashing for fast file matching)
- tomli-w (TOML config writes)

## Quick Start

```bash
uv sync
uv run python -m src.main
```

## Testing

```bash
uv run pytest              # headless unit tests
uv run pytest -m gui       # GUI tests (needs X11/Wayland)
uv run pytest -v           # verbose
```

## Project Structure

```
src/
├── main.py              # Entry point
├── core/
│   ├── hasher.py        # xxHash content hashing (multi-algo)
│   ├── worker.py        # Background comparison worker (QRunnable)
│   └── archive.py       # ZIP/TAR archive browsing + extraction
├── ui/
│   ├── main_window.py   # Main window / toolbar / menu
│   ├── file_pane.py     # Side-by-side file display + DnD + context menu
│   ├── diff_dialog.py   # Inline diff view
│   └── settings_dialog.py # Settings (hash algo, theme, ignore patterns)
└── utils/
    ├── config.py        # TOML config load/save (~/.config/beyondcomp/)
    └── session.py       # Session load/save (.bc-session files)
tests/
├── test_hasher.py       # Unit tests (headless)
├── test_archive.py      # Archive module tests (headless)
└── test_prototype.py    # GUI integration tests (needs display)
```

## Features

- Side-by-side directory comparison with color-coded status
- Content hashing (xxh3_64, xxh64, md5, sha1, sha256)
- Inline diff dialog for text files (Myers algorithm)
- Toolbar: Compare, Copy L↔R, Delete, New Folder, Open With, Settings
- Context menu: Open, Copy to Other Side, Delete, Rename, Properties
- Drag-and-drop between panes
- Settings dialog with persistent config (`~/.config/beyondcomp/config.toml`)
- Session save/load (`File → Save/Load Session`, auto-restore on startup)
- Ignore patterns (glob) to filter out files
- Archive browsing — double-click a .zip/.tar.gz to navigate inside like a folder

## Roadmap

- [x] Basic Qt UI with split panes
- [x] File diff dialog
- [x] Content hashing (xxh3_64 default, multiple algorithms)
- [x] Toolbar actions (copy, delete, new folder, open with)
- [x] Context menu (right-click: open, copy, delete, rename, properties)
- [x] Drag-and-drop between panes
- [x] Settings dialog with config persistence (TOML)
- [x] Session save/load with auto-restore
- [x] Ignore patterns support
- [x] pytest setup with gui/headless markers
- [x] Archive support (ZIP, TAR, GZ, BZ2, XZ) — browse inside archives
- [ ] SFTP/remote comparison
- [ ] CLI for headless diff
- [ ] CI