# MoSCoW Prioritization — Synk

**Status:** Living document  
**Date:** 2026-06-16  
**Version:** v0.2.0 snapshot

Categories: **M**ust (v1.0 non-negotiable), **S**hould (important but not critical), **C**ould (nice to have), **W**on't (explicitly out of scope).

---

## Must Have (M)

| ID | Feature | Shipped In | Notes |
|----|---------|-----------|-------|
| M1 | Side-by-side directory tree panes | v0.1 | QSplitter + two QTreeView instances |
| M2 | Recursive file walk with metadata (size, mtime) | v0.1 | pathlib + worker thread |
| M3 | Fast content hashing (xxh3_64 default) | v0.1 | Multi-algo: xxh64, md5, sha1, sha256 |
| M4 | Color-coded status per file (identical/different/left-only/right-only) | v0.1 | Green, salmon, pink, light blue |
| M5 | Status bar with summary counts | v0.1 | Progress during scan, item counts |
| M6 | Worker thread for non-blocking UI | v0.1 | QRunnable + QThreadPool |
| M7 | Toolbar: Compare, Copy L↔R, Delete, New Folder, Open With | v0.1 | |
| M8 | Context menu (right-click): Open, Copy, Delete, Rename, Properties | v0.1 | |
| M9 | Drag-and-drop between panes | v0.1 | |
| M10 | Diff dialog on double-click (Myers algorithm) | v0.1 | Inline diff view for text files |
| M11 | Ignore patterns (glob filtering) | v0.1 | Settings dialog |
| M12 | Settings persistence (TOML) | v0.1 | `~/.config/beyondcomp/config.toml` |
| M13 | Session save/load with auto-restore | v0.1 | `.bc-session` files |
| M14 | Package on PyPI, installable via pip | v0.1 | `synk-diff` |
| M15 | CLI mode (headless diff) | v0.1 | `synk diff file1 file2` |
| M16 | CI (GitHub Actions) | v0.1 | |
| M17 | Hide identical files toggle | v0.1 | |
| M18 | Refresh (F5) | v0.1 | |

## Should Have (S)

| ID | Feature | Shipped In | Notes |
|----|---------|-----------|-------|
| S1 | Archive browsing (ZIP, TAR, GZ, BZ2, XZ) | v0.2 | Virtual folder pattern |
| S2 | SFTP remote panel | v0.2 | Browse, download, upload via paramiko |
| S3 | SFTP connection dialog | v0.2 | `sftp://user@host:port/path` |
| S4 | 3-way merge engine (base/local/remote) | v0.2 | `core/merge.py` — Myers-based |
| S5 | 3-way merge dialog with conflict navigation | v0.2 | `ui/merge_dialog.py` |
| S6 | Light/dark theme toggle | v0.1 | |

## Could Have (C)

| ID | Feature | Shipped In | Notes |
|----|---------|-----------|-------|
| C1 | Syntax highlighting in diff view | — | Would require QsciScintilla or custom highlighting |
| C2 | Hex view for binary files | — | |
| C3 | Folder sync wizard (two-way sync) | — | Beyond Compare's "Synchronize" action |
| C4 | Git difftool/mergetool integration | — | Script to invoke Synk from Git |
| C5 | Archive creation (pack folders into ZIP/TAR) | — | |
| C6 | Keyboard shortcut customization | — | Beyond hardcoded F5/Enter/Del |
| C7 | Command palette (VS Code-style) | — | |
| C8 | Portable Windows build (.exe) | — | PyInstaller or Nuitka |
| C9 | macOS .dmg package | — | |
| C10 | Folder-compare report (HTML/CSV export) | — | |

## Won't Have (W)

| ID | Feature | Rationale |
|----|---------|-----------|
| W1 | Real-time collaborative editing | Requires server infrastructure, out of scope |
| W2 | Cloud storage integration (S3, GDrive, OneDrive) | API surface is massive; low personal need |
| W3 | Plugin system / scriptable API | No concrete use case yet; would introduce ABI stability burden |
| W4 | Watch-mode (live file monitoring) | inotify/kqueue is a separate product; scope creep |
| W5 | Mobile app (Android/iOS) | File comparison on mobile is a niche of a niche |
| W6 | SaaS / hosted service | Directly conflicts with BDR-003 (free, personal tool) |
| W7 | Distributed file comparison (p2p) | No plausible use case for a desktop diff tool |
| W8 | i18n / multi-language UI | UI strings are minimal; translation maintenance is high |
