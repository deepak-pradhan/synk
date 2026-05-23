# AGENTS.md — Beyond Compare Clone

## Quick start
```bash
uv sync                    # install deps from uv.lock
uv run python -m src.main  # launch GUI (requires X11/Wayland)
```

## Package management
- **uv** only (no pip, no poetry). Lockfile: `uv.lock`.
- Python 3.12+ pinned in `.python-version`.
- Dependencies: `PySide6` (Qt6), `diff-match-patch` (Myers diff), `xxhash`, `tomli-w` (TOML writes).

## Entrypoint & imports
- Real entry: `src/main.py` (root `main.py` is a stub — ignore it).
- All imports use `src.` prefix: `from src.core.hasher import Hasher`.

## Project layout
```
src/
├── core/       hasher.py, worker.py (QRunnable), archive.py (ZIP/TAR browsing)
├── ui/         main_window.py, file_pane.py, diff_dialog.py, settings_dialog.py
└── utils/      config.py, session.py
tests/
├── test_hasher.py
├── test_archive.py      # archive module (headless)
└── test_prototype.py   # marked @pytest.mark.gui, skipped headless
```

## Tests
- **pytest** via `uv run pytest`.
- `pytest.ini_options` in `pyproject.toml` sets `pythonpath = ["."]` and `testpaths = ["tests"]`.
- GUI tests marked `@pytest.mark.gui` — skipped headless; run with `uv run pytest -m gui` (needs display).

## Testing commands
```bash
uv run pytest                     # headless only (skips gui tests)
uv run pytest -m gui              # GUI integration tests (needs X11/Wayland)
uv run pytest -v                  # verbose
```

## Current state (prototype)
Working: side-by-side file panes, hash comparison (xxh3_64 default), diff dialog, toolbar actions (copy/delete/new folder/open), context menu (right-click: open/copy/delete/rename/properties), drag-and-drop between panes, settings dialog (hash algo/theme/ignore patterns), session save/load (File menu, auto-restore on startup), archive browsing (ZIP/TAR.GZ/TAR.BZ2/TAR.XZ).
Not yet: SFTP/remote, CLI mode, CI.

## Config & sessions
- Config stored at `~/.config/beyondcomp/config.toml` (uses stdlib `tomllib` + `tomli-w`).
- Config sections: `general` (theme, font_size), `comparison` (hash_algorithm, context_lines), `ignore` (patterns, show_identical).
- Last session auto-saved to `~/.config/beyondcomp/last_session.toml` on exit; user prompted to restore on next launch.
- Manual sessions saved/loaded as `.bc-session` files via File menu.

## Quirks & conventions
- Hash algorithms: `xxh3_64` (default), `xxh64`, `md5`, `sha1`, `sha256`.
- Worker uses `QRunnable` + `QThreadPool` — signals for progress, never block the main thread.
- Hidden files (dotfiles) are skipped during comparison.
- Status colors: green (identical), salmon (different), pink (left-only), light blue (right-only).
- Archive browsing uses stdlib `zipfile` + `tarfile` — no external C deps. Double-click an archive to navigate inside; `..` goes back out.
- Archive paths use `archive:/path/to/file.zip` prefix internally. `FilePane._archive_path` and `_archive_prefix` track state.
