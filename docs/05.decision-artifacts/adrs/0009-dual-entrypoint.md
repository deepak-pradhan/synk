---
thing_id:        "synk-adr-0009"
thing_type:      "adr"
adr_id:          "0009"
domain:          "synk"
phase:           "p1-core-features"
version:         "1.0"
lifecycle_state: "approved"
deciders:        "Deepak"
reversibility:   "high"
decision_date:   "2026-06-15"
last_updated:    "2026-06-16"
next_review_date: "2026-09-16"
priority:        "high"
confidentiality: "internal"
tags:            [cli, gui, entrypoint, architecture, headless]
relations:
  depends_on:    ["synk-adr-0001", "synk-adr-0008"]
  related_to:    []
  enables:       []
---

# ADR-0009: CLI + GUI Dual Entrypoint

## Status

**Accepted** (2026-06-15). Implemented in v0.2.

## Context

Synk serves two use cases: (1) interactive visual comparison with side-by-side panels (GUI), and
(2) headless/automated comparison for CI pipelines and scripts (CLI). A single codebase with two
entrypoints avoids maintaining separate projects.

## Decision

Provide **two entrypoints** from the same codebase:

- **`synk` CLI** — `src/cli.py:main` — argparse-based headless interface (registered in
  `pyproject.toml` `[project.scripts]`).
- **`python -m src.main`** — PySide6 GUI application.

The CLI can optionally launch the GUI for merge operations (`synk merge --gui`).

## Rationale

- `cli.py` is pure Python with no Qt import on the common code path. Qt is only imported when
  `--gui` is passed — so the CLI works on headless servers.
- Shared `core/hasher.py`, `core/merge.py` between both modes.
- Proper exit codes (0 = no differences, 1 = differences/error) for `&&` chaining.
- `pyproject.toml` scripts entrypoint makes the CLI discoverable via `pipx` or `pip install`.

## Consequences

**Positive:**
- CI pipelines use Synk without a display (`synk diff dir1/ dir2/`).
- Single install handles both modes.
- CLI features tested via pytest without GUI fixtures.

**Negative:**
- Two entrypoints means two `if __name__ == "__main__"` patterns.
- Some configuration must be specified via CLI flags (no settings dialog in headless mode).
- `synk merge --gui` requires conditional import pattern.

## Interface

```
$ synk diff file1.txt file2.txt        # inline color diff
$ synk diff dir1/ dir2/                # summary table
$ synk merge base local remote -o out  # 3-way merge to file
$ synk merge base local remote --gui   # 3-way merge in dialog
$ synk hash file1.txt file2.txt        # print hashes
```

Exit codes: 0 = identical/no conflicts, 1 = differences/conflicts or error.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| GUI-only | Excludes CI use case |
| CLI-only | No visual diff capability |
| Two separate packages | Duplicate code, more CI work |
| Web UI (localhost server) | Requires running a daemon; adds latency and security surface |
