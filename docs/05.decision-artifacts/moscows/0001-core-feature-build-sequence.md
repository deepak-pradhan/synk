---
thing_id:         "synk-moscow-0001"
thing_type:       "moscow"
domain:           "synk"
lifecycle_state:  "active"
priority:         "high"
confidentiality:  "internal"
owner:            "Deepak"
version:          "1.0"
last_updated:     "2026-06-16"
next_review_date: "2026-09-16"
relations:
  depends_on:     ["synk-bdr-0006"]
  related_to:     ["synk-adr-0002", "synk-adr-0006", "synk-adr-0007", "synk-adr-0010"]
  enables:        []
tags:             [moscow, backlog, comparison, diff, merge, archive, sftp, cli]
---

# MoSCoW 0001 — Core feature build sequence

> Prioritizes the feature set derived from the build-vs-buy decision
> ([`synk-bdr-0001`](../bdrs/0001-build-vs-buy.md)) and the dogfood-first philosophy
> ([`synk-bdr-0006`](../bdrs/0006-prioritization-philosophy.md)). Each MUST/SHOULD item was
> delivered across milestones M1–M10 of the implementation plan.
>
> **As-built (2026-06-16, `active`).** MUST 1–18, SHOULD 1–6, and COULD 1 (theme toggle) are
> shipped in v0.1–v0.2. Forward work is captured in the COULD backlog below; no new MoSCoW
> needed until a new strategy cycle starts.

## MUST

1. **Side-by-side directory tree panes** — `QSplitter` + two `QTreeView` instances with columns:
   Name, Size, Modified, Status.
2. **Recursive file walk with metadata** — `pathlib.Path.rglob()` on worker thread; captures
   size, mtime, is_dir per entry.
3. **Fast content hashing (xxh3_64 default)** — `Hasher` class with pluggable dispatch; 64KB
   chunked reading. See `synk-adr-0002`.
4. **Color-coded status per file** — green (identical), salmon (different), pink (left-only),
   light blue (right-only). See `synk-adr-0011`.
5. **Status bar with summary counts** — identical, different, left-only, right-only counts;
   progress bar during scan.
6. **Worker thread for non-blocking UI** — `QRunnable` + `QThreadPool`; `WorkerSignals` for
   thread-safe UI updates. See `synk-adr-0003`.
7. **Toolbar: Compare, Copy L↔R, Delete, New Folder, Open With** — standard actions with
   `QToolBar`.
8. **Context menu (right-click)** — Open, Copy to Other Side, Delete, Rename, Properties.
9. **Drag-and-drop between panes** — internal drag-drop mode; QDrag support.
10. **Diff dialog on double-click** — Myers algorithm via `diff-match-patch`. See `synk-adr-0005`.
11. **Ignore patterns** — glob-based filtering via `fnmatch`; settings dialog.
12. **Settings persistence** — TOML at `~/.config/beyondcomp/config.toml`. See `synk-adr-0004`.
13. **Session save/load** — `.bc-session` files with auto-restore on launch. See `synk-adr-0012`.
14. **Package on PyPI** — `synk-diff` package with hatchling build system. See `synk-bdr-0005`.
15. **CLI mode (headless diff)** — `synk diff`, `synk hash`, `synk merge` commands. See `synk-adr-0009`.
16. **CI (GitHub Actions)** — automated test + publish on release tag.
17. **Hide identical files toggle** — checkbox to filter identical rows from tree view.
18. **Refresh (F5)** — re-run comparison on current paths.

## SHOULD

1. **Archive browsing** — ZIP, TAR, GZ, BZ2, XZ as virtual folders; lazy listing; stream-extract
   on copy. See `synk-adr-0006`.
2. **SFTP remote panel** — browse, download, upload via paramiko. See `synk-adr-0007`.
3. **SFTP connection dialog** — `sftp://user@host:port/path` URL entry; password/key auth.
4. **3-way merge engine** — BASE/LOCAL/REMOTE with overlap detection. See `synk-adr-0010`.
5. **3-way merge dialog** — conflict navigation; take local/remote/both/base buttons.
6. **Light/dark theme toggle** — `QStyleSheet` switching.

## COULD

1. **Syntax highlighting in diff view** — would require QsciScintilla or custom highlighter.
2. **Hex view for binary files** — hex dump panel for binary comparison.
3. **Folder sync wizard** — two-way synchronize (Beyond Compare's "Synchronize" action).
4. **Git difftool/mergetool integration** — script to invoke Synk from Git.
5. **Archive creation** — pack folders into ZIP/TAR from within Synk.
6. **Keyboard shortcut customization** — beyond hardcoded F5/Enter/Del.
7. **Command palette** — VS Code-style fuzzy command search.
8. **Portable Windows build** — PyInstaller or Nuitka single .exe.
9. **macOS .dmg package** — native macOS distribution.
10. **Folder-compare report export** — HTML/CSV summary of differences.

## WON'T (this cycle)

- **Real-time collaborative editing** — requires server infrastructure; out of scope.
- **Cloud storage integration (S3, GDrive, OneDrive)** — massive API surface; low personal need.
- **Plugin system / scriptable API** — no concrete use case yet; ABI stability burden.
- **Watch-mode (live file monitoring)** — inotify/kqueue is a separate product; scope creep.
- **Mobile app (Android/iOS)** — file comparison on mobile is a niche of a niche.
- **SaaS / hosted service** — contradicts BDR-0003 (free, personal tool).
- **Distributed file comparison (p2p)** — no plausible use case.
- **i18n / multi-language UI** — UI strings minimal; translation maintenance is high.

## Suggested batch boundaries

- **Batch 1** (M0–M2, v0.1): MUST 1–6 (panels, walk, hashing, colors, status bar, worker).
- **Batch 2** (M3–M5, v0.1): MUST 7–10 (toolbar, context menu, DnD, diff dialog).
- **Batch 3** (M6, v0.1): MUST 11–13 (ignore patterns, settings, sessions).
- **Batch 4** (M7–M8, v0.2): SHOULD 1–3 (archives, SFTP).
- **Batch 5** (M9–M10, v0.2): SHOULD 4–6, MUST 14–18 (merge, CLI, CI, packaging, polish).
- COULDs scheduled on demand thereafter.
