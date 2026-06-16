# ADR-009: CLI + GUI Dual Entrypoint

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Synk serves two use cases that demand different interfaces:
1. **Interactive comparison** — user wants a visual diff with side-by-side panels, drag-and-drop, and context menus (GUI)
2. **Headless/automated comparison** — a script or CI pipeline needs to check two directories and get an exit code (CLI)

A single binary with two modes avoids maintaining separate codebases.

## Decision

Provide **two entrypoints** from the same codebase:

- **`synk` CLI** (via `pyproject.toml` `[project.scripts]`) — `src/cli.py:main` — argparse-based headless interface
- **`python -m src.main`** — PySide6 GUI application

The CLI can optionally launch the GUI for merge operations (`synk merge --gui`).

## Rationale

- `cli.py` is pure Python with no Qt import on the common code path. Qt is only imported when `--gui` is passed to `synk merge` — so the CLI works on headless servers with no display.
- `hashlib`-based hashing is shared (both CLI and GUI use `core/hasher.py`).
- The CLI returns proper exit codes (0 = no differences, 1 = differences or error) for `&&` chaining in shell scripts.
- `pyproject.toml` scripts entrypoint (`synk = "src.cli:main"`) makes the CLI discoverable via `pipx` or `pip install`.

## Consequences

**Positive:**
- CI pipelines and backup scripts use Synk without a display (`synk diff dir1/ dir2/`)
- Single install handles both modes — no separate "server" and "desktop" packages
- CLI features are automatically tested via pytest without GUI fixtures

**Negative:**
- Two entrypoints means two `if __name__ == "__main__"` patterns — potential confusion
- Some configuration must be specified via CLI flags (no settings dialog in headless mode)
- `synk merge --gui` requires an import-time decision that makes the conditional import pattern necessary

## Implementation

```
$ synk diff file1.txt file2.txt        # inline color diff
$ synk diff dir1/ dir2/                # summary table
$ synk merge base local remote -o out  # 3-way merge to file
$ synk merge base local remote --gui   # 3-way merge in dialog
$ synk hash file1.txt file2.txt        # print hashes
```

Exit codes: 0 = identical/no conflicts, 1 = differences/conflicts or error.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| GUI-only | Excludes CI use case — the primary reason the author built Synk (deployment verification) |
| CLI-only | No visual diff capability; hard to browse large directory comparisons |
| Two separate packages (`synk-cli`, `synk-gui`) | Duplicate code, more CI work, confusing for users |
| Web UI (localhost server) | Requires running a server daemon; adds latency and security surface |
