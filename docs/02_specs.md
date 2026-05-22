# Specs for Personal Beyond Compare‑Like Tool

## 1. Vision
Provide a lightweight, fast, and extensible file and folder comparison utility for personal use on Ubuntu (with cross‑platform potential). The tool should enable users to:
- Visually compare two directories or files side‑by‑side.
- See differences highlighted (content, size, timestamps).
- Perform actions such as copy, delete, or synchronize selected items.
- Optionally compare archive contents and remote (SFTP) locations.
- Save and load comparison sessions.

## 2. Scope
**In‑Scope**
- Local filesystem comparison (two panels).
- Support for common text files (code, config, logs) and binary files (size/hash compare).
- Archive browsing (`.zip`, `.tar.gz`, `.tar.bz2`, `.xz`) as virtual folders.
- SFTP remote panel (read‑only browsing, download/upload via actions).
- Basic three‑way merge view (optional, later).
- Session persistence (paths, filters, compare options).
- Theming (light/dark) via Qt stylesheet.
- Configurable ignore patterns (e.g., `.git`, `*.pyc`).

**Out of Scope (Initial Release)**
- Real‑time collaborative editing.
- Integration with version control as a difftool (git difftool) – can be added later via external script.
- Cloud storage (S3, Google Drive) – requires additional APIs.
- Advanced features like folder‑sync scheduling.

## 3.1. Functional Requirements - Browse Folder and View Codes & Configs

| ID | Description | Priority |
|----|-------------|----------|
| FR1 | Launch with two empty panels; user can set left/right path via textbox or browse dialog. | High |
| FR2 | Display a tree view of files/folders in each panel with columns: Name, Size, Modified, Status (identical, different, left‑only, right‑only, error). | High |
| FR3 | When a path is set, recursively scan and compute a quick hash (xxh3_64) for each file; compare hashes to decide if files are identical. | High |
| FR5 | Color‑code rows: green = identical, red = different, blue = left‑only, magenta = right‑only, gray = error/unreadable. | High |
| FR14| Status bar shows: number of items compared, number of differences, progress during scan. | High |

## 3.2. Functional Requirements

| ID | Description | Priority |
|----|-------------|----------|
| FR4 | For files flagged as "different" (hash mismatch), optionally run a full diff (Myers) and display inline differences in a side‑by‑side diff viewer on double‑click. | Medium |
| FR6 | Provide toolbar actions: Refresh, Compare, Copy Left→Right, Copy Right→Left, Delete, New Folder, Open With… | High |
| FR7 | Support drag‑and‑drop between panels to copy files. | Medium |
| FR8 | Allow user to set ignore patterns (glob) via Settings dialog; ignored items are omitted from comparison. | Medium |
| FR9 | When encountering an archive file, show it as expandable node; its virtual children are listed on‑the‑fly via libarchive bindings. | Low |
| FR10| Support SFTP panel: user can enter `sftp://user@host:port/path` and browse remote filesystem (list, stat). Enable download/upload via copy actions. | Low |
| FR11| Allow saving current comparison state (paths, filters, options) to a `.bc-session` file (TOML) and loading it later. | Medium |
| FR12| Provide a Settings dialog to tweak: hash algorithm, diff context lines, theme, font, default ignore patterns. | Low |
| FR13| Provide keyboard shortcuts: F5 (refresh), Enter (open/double‑copy), Del (delete), Ctrl+C/V (copy). | Low |

## 4. Non‑Functional Requirements

| ID | Description | Priority |
|----|-------------|----------|
| NFR1 | UI must remain responsive during long scans; use worker threads/QThreadPool. | High |
| NFR2 | Memory usage should stay < 200 MB for trees up to ~100k files (store only metadata, not file contents). | Medium |
| NFR3 | Startup time < 2 s on a typical Ubuntu workstation (no heavy imports). | Medium |
| NFR4 | Code must be modular: core logic (diff, hash, archive, remote) independent of UI layer. | High |
| NFR5 | Follow PEP‑8 (Python) and use type hints where practical. | Low |
| NFR6 | Unit test coverage ≥ 70 % for core modules (diff, hasher, archive, remote). | Medium |
| NFR7 | Provide a portable single‑file distribution via PyInstaller (optional). | Low |

## 5. User Stories (condensed)

1. As a user, I want to select two folders and instantly see which files are the same or different so I can identify changes quickly.
2. As a user, I want to view a side‑by‑side diff of a text file when I double‑click it, to understand exact changes.
3. As a user, I want to copy a file from one side to the other with a toolbar button or drag‑and‑drop, to synchronize folders.
4. As a user, I want to ignore certain file types (e.g., compiled binaries) so they do not clutter the comparison view.
5. As a user, I want to compare the contents of a ZIP file against a folder, to verify a backup.
6. As a user, I want to save my comparison setup and reopen it later to continue work.
7. As a user, I want the UI to stay responsive while scanning large directories.

## 6. Acceptance Criteria (examples)

- **FR1/FR2**: When the user enters two valid paths and presses Compare, the tree views populate within 5 s for a directory of 10k files, showing correct status icons.
- **FR3**: Identical files (same size & xxhash) are marked identical without invoking full diff.
- **FR4**: Double‑clicking a file marked different opens a diff viewer with left/right panes showing line‑by‑line changes, with syntax highlighting if available.
- **FR6**: Clicking "Copy Left→Right" copies the selected file/folder to the right panel’s current directory, overwriting if confirmed.
- **FR9**: Expanding a `.zip` node lists its internal folders/files; navigating into them works like a regular directory.
- **FR10**: Entering `sftp://user@host` prompts for password (key‑agent supported) and displays remote file list; copy actions transfer files via SFTP.
- **NFR1**: During a scan of 100k files, the UI remains usable (can cancel, interact with toolbar) and shows a progress bar.

## 7. Open Questions / Risks
- Performance of recursive scanning with libarchive for deep archives; mitigate by lazy expansion only when node expanded.
- Handling of symbolic links: decide to follow or treat as separate items (initial: treat as links, show target path).
- Conflict resolution during copy: implement overwrite/skip/rename prompts.
- Licensing: PySide6 LGPL is acceptable for proprietary or open-source personal tool.

---