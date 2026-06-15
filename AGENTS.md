# AGENTS.md — Beyond Compare Clone

## Quick start
```bash
uv sync                    # install deps from uv.lock
uv run python -m src.main  # launch GUI (requires X11/Wayland)
```

## Package management
- **uv** only (no pip, no poetry). Lockfile: `uv.lock`.
- Python 3.12+ pinned in `.python-version`.
- Dependencies: `PySide6` (Qt6), `diff-match-patch` (Myers diff), `xxhash`, `tomli-w` (TOML writes), `paramiko` (SFTP).

## Entrypoint & imports
- Real entry: `src/main.py` (root `main.py` is a stub — ignore it).
- All imports use `src.` prefix: `from src.core.hasher import Hasher`.

## Project layout
```
src/
├── core/       hasher.py, worker.py (QRunnable), archive.py (ZIP/TAR browsing), remote.py (SFTP)
├── ui/         main_window.py, file_pane.py, diff_dialog.py, settings_dialog.py, sftp_connect_dialog.py
└── utils/      config.py, session.py
tests/
├── test_hasher.py
├── test_archive.py      # archive module (headless)
├── test_remote.py       # remote module (headless, unit only — no live SFTP server)
└── test_prototype.py   # marked @pytest.mark.gui, skipped headless
```

## Tests
- **pytest** via `uv run pytest`.
- `pytest.ini_options` in `pyproject.toml` sets `pythonpath = ["."]` and `testpaths = ["tests"]`.
- GUI tests marked `@pytest.mark.gui` — skipped headless; run with `uv run pytest -m gui` (needs display).

## Testing commands
```bash
uv run pytest                          # headless only (skips gui tests)
uv run pytest -m gui                   # GUI integration tests (needs X11/Wayland)
uv run pytest -v                       # verbose
uv run pytest tests/test_hasher.py     # single test file
uv run pytest tests/test_hasher.py -k test_compare  # match by name
```

## Config & sessions
- Config stored at `~/.config/beyondcomp/config.toml` (stdlib `tomllib` reads, `tomli-w` writes).
- Sections: `[general]` (theme, font_size), `[comparison]` (hash_algorithm, context_lines), `[ignore]` (patterns, show_identical).
- Last session auto-saved to `~/.config/beyondcomp/last_session.toml` on exit; user prompted to restore on next launch.
- Manual sessions saved/loaded as `.bc-session` files via File menu.

## Conventions
- Hash algorithms: `xxh3_64` (default), `xxh64`, `md5`, `sha1`, `sha256`.
- Worker uses `QRunnable` + `QThreadPool` — signals for progress, never block the main thread.
- Hidden files (dotfiles) are skipped during comparison.
- Status colors: green (identical), salmon (different), pink (left-only), light blue (right-only).
- Archive paths use `archive:/path/to/file.zip` prefix internally. `FilePane._archive_path` and `_archive_prefix` track state.
- Archive browsing uses stdlib `zipfile` + `tarfile` — no external C deps. Double-click an archive to navigate inside; `..` goes back out.
- SFTP paths use `sftp://user@host:port/path` format. Click "Connect SFTP..." button or type an sftp:// URL in the path bar. `FilePane._sftp_conn` holds the active connection. Remote module (`src/core/remote.py`) uses paramiko; no live server needed for unit tests.

## Gotchas
- `SFTP_PREFIX = "sftp://"` is referenced in `file_pane.py:157,437` but never defined — it will cause a `NameError` at runtime if an SFTP path is used. Define it or import from `src.core.remote`.
- `src/ui/src/utils/` is an empty dead directory — ignore it.
- `.obsidian/` and `ddd.md.save` at the repo root are unrelated noise — ignore them.
- No lint, formatter, typechecker, or CI is configured yet.
