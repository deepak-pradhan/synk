# Implementation Plan (Incremental Milestones)

This plan breaks the project into small, deliverable increments. Each milestone should be completable in a few days to a week, produce a working prototype, and allow early feedback.

---

## Milestone 0 – Project Setup & Foundations
**Goal:** Repo initialized, dev environment ready, basic skeleton in place.

**Tasks**
- [ ] Create Git repo (if not already).
- [ ] Add `docs/` with tech stack and specs (already done).
- [ ] Set up `uv` environment with Python 3.12 and install base dependencies:
    - `PySide6`, `diff-match-patch`, `xxhash`, `libarchive-c`, `paramiko`, `tomli-w`.
- [ ] Create project skeleton per `src/` layout.
- [ ] Add a simple `README.md` with build/run instructions.
- [ ] Implement a minimal `main.py` that creates a blank `QMainWindow` and shows it.
- [ ] Write a sanity‑check unit test (e.g., test that the app can start).

**Deliverable:** A launchable GUI shell (empty window) that can be started via `python -m src`.

**Time estimate:** 0.5 day.

---

## Milestone 1 – Path Input & Basic Tree Population
**Goal:** User can type or browse two paths and see a flat list of items in each panel.

**Tasks**
- [ ] Design `FilePane` widget: a `QTreeView` with a custom `QFileSystemModel` (or `QStandardItemModel`) showing columns: Name, Size, Modified, Status.
- [ ] Add two `FilePane` instances side‑by‑side inside a `QSplitter`.
- [ ] Add path entry widgets (`QLineEdit` + browse button) above each pane.
- [ ] Implement browsing dialog (`QFileDialog.getExistingDirectory`).
- [ ] When a path is set and Enter pressed or Browse clicked, spawn a worker thread to:
    - Walk the directory using `pathlib.Path.rglob('*')` (ignore permission errors).
    - For each entry, emit a signal with file info (path, size, mtime).
- [ ] In the GUI thread, populate the model with items; set initial Status to “unknown”.
- [ ] Show a progress bar in the status bar while walking.
- [ ] Add a Refresh button (F5) that repeats the walk.

**Deliverable:** Ability to point at two directories and see a recursive file list with basic metadata (no comparison yet). UI remains responsive during long walks.

**Time estimate:** 1.5 days.

---

## Milestone 2 – Fast Hash Comparison & Status Coloring
**Goal:** Determine if files are identical using xxHash and color‑code rows.

**Tasks**
- [ ] Implement `hasher.xxh3_64(path)` that returns hex digest; handle large files by reading in chunks.
- [ ] Extend worker to compute hash for each regular file (skip dirs).
- [ ] When both sides have a file with same relative path:
    - If hashes match → Status = `Identical`.
    - If hashes differ → Status = `Different`.
    - If exists only on one side → `LeftOnly` / `RightOnly`.
    - If error reading → `Error`.
- [ ] Map Status values to foreground/background colors via Qt item roles or a custom delegate.
- [ ] Show summary counts in status bar (identical, different, left‑only, etc.).
- [ ] Allow user to toggle “Show identical files” via a checkbox (filter).

**Deliverable:** Side‑by‑side panels with colored rows indicating equality/difference based on fast hash; progress reporting; hide/show identical option.

**Time estimate:** 1.5 days.

---

## Milestone 3 – Inline Diff Viewer (Double‑Click)
**Goal:** Open a side‑by‑side diff viewer for text files when the user double‑clicks a “Different” entry.

**Tasks**
- [ ] Create a `DiffDialog` (QDialog) containing two `QPlainTextEdit` (or `QsciScintilla` if syntax highlighting desired) in a horizontal splitter.
- [ ] On double‑click in tree, check if both sides are files and status is Different.
    - Read both files as text (UTF‑8, fallback to latin‑1 with errors replace).
    - Use `diff_match_patch.diff_main` to get diffs.
    - Convert diffs to HTML with `diff_match_patch.diff_prettyHtml` or build a custom side‑by‑side view highlighting insertions/deletions.
- [ ] Set the rich text (or plain text with background colors) into the panes.
- [ ] Make dialog resizable, with OK/Cancel.
- [ ] For binary files, show a message “Binary files differ” and optionally show hex view (stretch goal).

**Deliverable:** Double‑clicking a differing text file opens a readable diff; binary files give a notice.

**Time estimate:** 1 day.

---

## Milestone 4 – Toolbar Actions: Copy, Delete, New Folder
**Goal:** Enable basic file operations between panels.

**Tasks**
- [ ] Design toolbar with actions: Refresh, Compare (re‑run), Copy L→R, Copy R→L, Delete, New Folder, Open With…
- [ ] Implement `Copy Left→Right`:
    - Get selected items in left pane.
    - For each, compute target path = right pane’s current directory / item name.
    - If target exists, ask to overwrite/skip/rename (QMessageBox).
    - Perform copy using `shutil.copy2` (preserve metadata) for files, `shutil.copytree` for dirs.
    - After copy, refresh the right pane (or update incrementally).
- [ ] Implement Delete: send to trash? For simplicity, permanent delete with confirmation using `send2trash` (pip install send2trash) or `shutil.rmtree`/`os.remove`.
- [ ] Implement New Folder: prompt for name, create directory in current pane’s path, refresh.
- [ ] Implement Open With…: use `QDesktopServices.openUrl` with default app, or allow custom command via settings.
- [ ] Ensure UI updates (status, colors) after any mutating action.

**Deliverable:** Basic file manipulation possible between sides; safety checks for overwrites.

**Time estimate:** 1.5 days.

---

## Milestone 5 – Drag‑and‑Drop & Context Menu
**Goal:** Improve usability with DND and right‑click menus.

**Tasks**
- [ ] Enable drag‑and‑drop from tree view to the opposite panel (internal drag‑drop mode).
    - On drop, treat as copy operation (same logic as toolbar Copy).
- [ ] Add a custom context menu (right‑click) on tree items with actions: Open, Copy to Other Side, Delete, Rename, Properties.
- [ ] Implement Rename: prompt for new name, move file/folder, refresh both sides if needed.
- [ ] Implement Properties dialog showing size, dates, attributes, full path.

**Deliverable:** Intuitive DND and right‑click workflow similar to file explorers.

**Time estimate:** 1 day.

---

## Milestone 6 – Ignore Patterns & Settings Dialog
**Goal:** Let users exclude noise (e.g., `.git`, `*.pyc`).

**Tasks**
- [ ] Add a Settings dialog (QDialog) with tabs:
    - General: theme (light/dark), font size.
    - Comparison: hash algorithm (xxh3 default), context lines for diff.
    - Ignore Patterns: multi‑line edit for glob patterns (one per line); also include presets.
- [ ] Persist settings to `~/.config/mycompare/config.toml` using `tomli-w` for writing and `tomllib` for reading.
- [ ] Modify the worker to test each file/dir against ignore list (using `fnmatch`) before adding to results.
- [ ] Provide a “Apply” button that updates the current comparison without restarting (if possible) or at least applies on next Compare.

**Deliverable:** Users can hide unwanted files; settings persist across runs.

**Time estimate:** 1 day.

---

## Milestone 7 – Archive Support (Virtual Folders)
**Goal:** Treat `.zip`, `.tar.gz`, etc., as expandable folders.

**Tasks**
- [ ] In the file‑system model, detect if a file is an archive via extension or libarchive header.
- [ ] If archive, make its children lazy‑loaded:
    - When user expands the node, call libarchive to list entries.
    - For each entry, synthesize a `VirtualFileInfo` (path inside archive, size, mtime).
    - Do NOT extract to disk unless user copies out (see copy action).
- [ ] Implement copy out: if source is a virtual file, extract that single entry to destination using libarchive-extract or streaming read.
- [ ] Implement copy into archive? (stretch) – can be disabled initially.
- [ ] Update status icons for archive nodes (maybe a box icon).
- [ ] Ensure that comparing an archive vs a folder works: hashes of virtual files computed by reading streamed content (can reuse xxhash on the stream).

**Deliverable:** Ability to browse and compare archive contents as if they were folders, extracting files on demand.

**Time estimate:** 2 days (archive handling can be complex; start with zip only).

---

## Milestone 8 – SFTP Remote Panel
**Goal:** Allow one side to point to an `sftp://` URL and browse remote files.

**Tasks**
- [ ] Extend path entry to detect scheme `sftp://`; split into user, host, port, path.
- [ ] Use paramiko `SSHClient` + `SFTPClient` to list directory (`listdir_attr`).
- [ ] Create a remote file model similar to local one but using SFTP stat info.
- [ ] For remote files, compute hash by downloading chunked stream (or, if server supports, use `stat` size+mtime only for quick compare; hash only when needed for diff).
- [ ] Implement copy actions between local and remote (download/upload) using SFTP `get`/`put`.
- [ ] Add authentication: try SSH agent, then prompt for password/passphrase (use `QInputDialog` with password echo).
- [ ] Show connection status and errors in status bar.

**Deliverable:** One pane can be a remote server; basic browsing and file transfer works.

**Time estimate:** 2 days (depends on familiarity with paramiko).

---

## Milestone 9 – Session Save & Load
**Goal:** Save and restore comparison state (paths, filters, options).

**Tasks**
- [ ] Define a session TOML schema:
    ```toml
    left_path = "..."
    right_path = "..."
    ignore_patterns = ["*.pyc", ".git/"]
    show_identical = true
    theme = "light"
    ```
- [ ] Add `Session → Save As…` and `Session → Load…` menu items.
- [ ] On save, write current settings + paths to file.
- [ ] On load, read and apply: set paths, update ignore list, trigger a refresh.
- [ ] Also auto‑save last session on exit and offer to restore on start.

**Deliverable:** Users can preserve their work environments.

**Time estimate:** 0.5 day.

---

## Milestone 10 – Polish, Testing & Packaging
**Goal:** Harden, test, and create distributable binaries.

**Tasks**
- [ ] Run black/ruff for formatting; ensure type hints.
- [ ] Write unit tests for core modules (hasher, diff, archive wrapper, remote wrapper) aiming for ≥70% coverage.
- [ ] Test on a few real scenarios: large dir, archives, SFTP (if available).
- [ ] Create a `requirements.txt` via `uv export`.
- [ ] Build a standalone executable with `PyInstaller` (one‑file, windowed).
    - Test on clean Ubuntu VM.
- [ ] Optionally create a Debian package (`debhelper` or `stdeb`) for easy apt install.
- [ ] Write final `README` with usage examples and troubleshooting.

**Deliverable:** Reliable, tested application that can be shared as a single file or package.

**Time estimate:** 2 days.

---

### Timeline Overview (approximate)

| Milestone | Target Duration |
|-----------|-----------------|
| 0 – Setup | 0.5 day |
| 1 – Path/Tree | 1.5 day |
| 2 – Hash & Color | 1.5 day |
| 3 – Diff Viewer | 1 day |
| 4 – Toolbar Actions | 1.5 day |
| 5 – DND/Context | 1 day |
| 6 – Ignore/Settings | 1 day |
| 7 – Archives | 2 day |
| 8 – SFTP | 2 day |
| 9 – Sessions | 0.5 day |
| 10 – Polish/Pack | 2 day |
| **Total** | **~14 days** (≈3 weeks part‑time) |

Each milestone ends with a runnable prototype, making it easy to demo progress, adjust scope, or ship early versions.

--- 

*Feel free to reorder or merge milestones based on your available time and interest (e.g., if remote SFTP isn’t needed, skip Milestone 8).*