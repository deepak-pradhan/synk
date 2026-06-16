# ADR-006: Archive-as-Virtual-Folder Pattern

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Users need to compare archive contents (ZIP, TAR.GZ) against folders or other archives — for example, verifying a backup tarball matches a source directory. Archives should appear as navigable folders without requiring full extraction.

## Decision

Treat **archives as virtual folders**: detect by extension, lazy-list contents on expand, and stream-extract individual files on copy-out.

## Rationale

- Archives are fundamentally tree structures — modeling them as virtual folders lets Synk reuse the same comparison logic (hash-based matching, status coloring) for both physical and virtual files.
- Lazy listing (only expand when the user clicks the node) avoids reading the entire archive on startup — critical for large backup tarballs (multi-GB).
- stdlib `zipfile` and `tarfile` are sufficient for reading — no need for `libarchive-c` (which is poorly maintained and requires a C library).
- Stream-extract on copy avoids writing temporary files for every virtual file the user glances at.

## Consequences

**Positive:**
- Archives are first-class citizens — compare ZIP vs folder, TAR vs ZIP, etc.
- No external C dependencies (stdlib zipfile/tarfile only)
- Lazy expansion keeps startup fast for directories with many archives

**Negative:**
- stdlib `tarfile` has no random-access lookup for individual entries — extracting a single file requires scanning the entire archive (acceptable for typical use)
- Writing into archives (creating/modifying archive entries) is not supported — would require a rewrite of the archive layer
- `zipfile` cannot reliably set mtime on extracted files (uses DOS timestamp resolution of 2 seconds); `tarfile` preserves mtime

## Implementation

`src/core/archive.py`:

```python
ARCHIVE_EXTENSIONS = {".zip": "zip", ".tar.gz": "tar", ".tgz": "tar", ...}

def list_archive_at_depth(path: str, prefix: str = "") -> list[ArchiveEntry]:
    """Lazy-list entries at a given depth inside the archive."""

def extract_file(archive_path: str, entry_name: str, dest_dir: str) -> Optional[str]:
    """Stream-extract a single entry to disk."""

def is_archive(path: str) -> bool:
    """Check by extension."""
```

In `FilePane`, `_archive_prefix` tracks the current virtual path within an archive; `..` navigates back out.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Extract to temp directory on expand | Slow for large archives; wastes disk space; cleanup complexity |
| FUSE mount (archivemount) | Requires FUSE kernel module; no portable Python implementation |
| libarchive-c (C library bindings) | Poorly maintained packaging (many Linux distros don't ship it); adds C build dependency |
| 7z CLI subprocess | Fragile shell parsing; loss of structured error handling; slower for single-file extraction |
