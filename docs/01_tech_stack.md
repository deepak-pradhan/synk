# Tech Stack for a Personal Beyond Compare‑Like Tool (Ubuntu)

## Overview
This document outlines a suggested technology stack for building a file‑ and folder‑comparison utility similar to Beyond Compare, targeting personal use on an Ubuntu workstation. The stack balances development speed, maintainability, and performance while remaining cross‑platform friendly.

---

## 1. Core Engine

| Concern                          | Recommended Choice                                                                     | Rationale                                                                                                                                                               | Version 0.01                                             |
| -------------------------------- | -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Programming Language**         | **Python 3.12+** (or **Rust 1.70+** for performance‑critical paths)                    | Python offers rapid prototyping, rich ecosystem, and easy bindings to GUI/toolkits. Rust can be used for the diff algorithm or file‑hashing if maximum speed is needed. | Phython 3.12                                             |
| **Diff Algorithm**               | Myers O(ND) algorithm (via `diff-match-patch` for Python or the `diff` crate for Rust) | Well‑studied, efficient for text files, and produces minimal edit scripts.                                                                                              | Myers O(ND) algorithm (via `diff-match-patch` for Python |
| **File‑System Traversal**        | `pathlib` + `os.walk` (Python) or `walkdir` (Rust)                                     | Simple, reliable recursive directory walking.                                                                                                                           | pathlib.Path.walk()                                      |
| **Content Hashing (pre‑filter)** | xxHash or SHA‑256 (via `xxhash` Python package or `rust-crypto`/`xxhash-rust`)         | Quickly detect identical files without full diff, speeding up large folder comparisons.                                                                                 | SHA-256, xxhash.xxh3_64                                  |
| **Archive Support**              | libarchive bindings (`pyarchivee` for Python, `libarchive-rs` for Rust)                | Transparent handling of ZIP, JAR, TAR, GZ, etc., allowing them to be treated as virtual folders.                                                                        | libarchive-c                                             |
| **Remote/FTP‑SFTP Access**       | `paramiko` (Python) or `ssh2-rs` (Rust)                                                | Enables comparison against remote servers without leaving the app.                                                                                                      | `paramiko` (Python)                                      |
| **Configuration Persistence**    | TOML files (via `toml` Python package or `serde` + `toml` crate)                       | Human‑readable, easy to edit, supports nested structures.                                                                                                               |                                                          |

|Concern|Recommended Choice|Rationale|Version 0.01|
|---|---|---|---|
|**Configuration Persistence**|TOML files (via `tomllib` in Python 3.11+)|TOML is the modern standard for Python (PEP 621). It is more readable than JSON and safer than YAML.|**`tomllib`** (Standard Library)|

Why `tomllib` for Version 0.01?

- **Zero Dependencies**: Since you are using **Python 3.12**, `tomllib` is already in the standard library for parsing. You only need the `tomli-w` package if you need to _write_ config files programmatically.
- **Strong Typing**: Unlike JSON, TOML has native support for datetime objects and distinct integer/float types, which is great for sync timestamps or file size thresholds.
- **Consistency**: It aligns perfectly with `pyproject.toml`, making your project structure feel cohesive.

---

## 2. User Interface Layer

| Use | Option                   | Stack                                      | Pros                                                                                                          | Cons                                                        |
| --- | ------------------------ | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Y   | **Qt (PyQt6 / PySide6)** | Python + Qt 6 bindings                     | Mature, native‑look widgets, excellent tree/table views, drag‑and‑drop, good documentation. Slightly heavier. | Requires Qt libraries; licensing (LGPL for PySide6).        |
| -   | **Dear ImGui**           | `imgui` bindings (`pyimgui` or `imgui-rs`) | Extremely fast, immediate‑mode GUI, easy to customize, low overhead.                                          | Custom look‑and‑feel; requires more manual widget creation. |
| -   | **Tauri + Svelte/React** | Rust backend (Tauri) + web front‑end       | Modern web technologies, single binary, easy styling, decent performance.                                     | Web‑based UI may feel less native; extra build step.        |
| -   | **TUI (Terminal UI)**    | `curses` (Python) or `ratatui` (Rust)      | Lightweight, runs in any terminal, great for keyboard‑driven workflows.                                       | Limited visual richness compared to GUI.                    |

**Recommendation for a first usable prototype:** Start with **PySide6** (LGPL) to get a functional side‑by‑side file pane quickly. If later you need lower latency or want to experiment, you can replace the UI layer with Dear ImGui or Tauri without changing the core diff library.

---

## 3. Project Structure (suggested)

```
├── docs/                 # Documentation (this file, design notes, etc.)
├── src/
│   ├── core/             # Diff engine, hashing, archive/remote handling
│   │   ├── __init__.py
│   │   ├── diff.py
│   │   ├── hasher.py
│   │   ├── archive.py
│   │   └── remote.py
│   ├── ui/               # GUI implementation (Qt, ImGui, etc.)
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── file_pane.py
│   │   └── settings_dialog.py
│   └── utils/            # Helpers, logging, config
│       ├── config.py
│       └── logger.py
├── tests/                # Unit/integration tests (pytest)
├── requirements.txt      # Python dependencies
├── Cargo.toml            # (if using Rust components)
└── README.md
```
### Refined Component Details for Version 0.01

To match your specific tech stack (**Python 3.12**, **PySide6**, **xxHash**, **libarchive-c**), here is how those files should be populated:

- **`core/hasher.py`**: Implementation of the "Dual-Hash" strategy. Use **xxh3_64** for the initial pass (fast file matching) and optionally **SHA-256** for a final "verification" bit before a destructive sync action.
- **`core/archive.py`**: Wrap **libarchive-c** to treat `.zip` or `.tar.gz` files as `VirtualPath` objects. This allows `pathlib.Path.walk()` to theoretically recurse into archives as if they were folders.
- **`ui/main_window.py`**: This should hold the **QSplitter** logic we discussed. It will act as the "Controller," coordinating between the `core/diff.py` results and the visual updates.
- **`utils/config.py`**: Use **`tomllib`** here to load your `config.toml`. Since you’re on 3.12, remember that `tomllib` is read-only; if you want the UI to _save_ settings, you'll need to add `tomli-w` to your `requirements.txt`.

### Integration Tip: The "Worker" Pattern

Since you have an **A4000**, you likely want this tool to be fast. In `ui/main_window.py`, don't run the `hasher.py` or `diff.py` logic on the main thread.

1. Create a `QRunnable` or `QThread` in `utils/`.
2. Emit **Signals** from the `core/` back to the `ui/` to update progress bars or "match" status icons in real-time.
3. 
---

## 4. Build & Dependencies (Ubuntu)

```bash
4. Build & Dependencies (Ubuntu + uv)
# First, ensure the system-level libraries for Qt6, libarchive, and SSL are present:
sudo apt-get update && sudo apt-get install -y \
    libqt6gui6 libqt6widgets6 qt6-base-dev \
    libarchive-dev libssl-dev

# Initialize and pin to Python 3.12
uv init --python 3.12
uv venv

# Core Engine Dependencies
uv add diff-match-patch xxhash libarchive-c paramiko

# UI & Config Dependencies 
# (tomli-w is added because tomllib is read-only in the stdlib)
uv add PySide6 tomli-w 

# Development Dependencies
uv add --dev pytest black

# Use code with caution.
# Why this setup works for your A4000:
# uv Speed: Installing PySide6 and paramiko via uv is near-instant compared to pip, which is great for iterating on your Qwen3-4B experiments.

# To keep your Project Structure clean, you can generate a locked file at any time:
uv export --format requirements-txt > requirements.txt
```

---

## 5. Next Steps

1. **Implement the core diff/hash module** and write unit tests against known file pairs.
2. **Create a simple CLI/TUI prototype** (using `curses` or `ratatui`) to verify traversal and hashing logic.
3. **Build the Qt‑based side‑by‑side pane** with two `QTreeView` widgets fed by a `QFileSystemModel` (or custom model for virtual folders).
4. **Add archive and remote handling** as plug‑in back‑ends.
5. **Iterate on UI polish**: coloring differences, sync/scroll linking, merge actions, session save/load.
6. **Package** the application (e.g., using `PyInstaller` or creating a Debian `.deb`) for easy distribution on Ubuntu.

---

*This stack is deliberately modular—feel free to swap Python for Rust in any layer as performance needs evolve.* 