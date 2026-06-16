---
thing_id:        "synk-adr-0006"
thing_type:      "adr"
adr_id:          "0006"
domain:          "synk"
phase:           "p1-core-features"
version:         "1.0"
lifecycle_state: "approved"
deciders:        "Deepak"
reversibility:   "high"
decision_date:   "2026-06-15"
last_updated:    "2026-06-16"
next_review_date: "2026-09-16"
priority:        "medium"
confidentiality: "internal"
tags:            [archive, zip, tar, virtual-folder, lazy-loading]
relations:
  depends_on:    []
  related_to:    ["synk-moscow-0001"]
  enables:       []
---

# ADR-0006: Archive-as-Virtual-Folder Pattern

## Status

**Accepted** (2026-06-15). Implemented in v0.2 M7.

## Context

Users need to compare archive contents (ZIP, TAR.GZ) against folders or other archives — for
example, verifying a backup tarball matches a source directory. Archives should appear as
navigable folders without requiring full extraction.

## Decision

Treat **archives as virtual folders**: detect by extension, lazy-list contents on expand, and
stream-extract individual files on copy-out.

## Rationale

- Archives are fundamentally tree structures — modeling them as virtual folders lets Synk reuse
  the same comparison logic (hash-based matching, status coloring) for physical and virtual files.
- Lazy listing avoids reading the entire archive on startup — critical for large backup tarballs.
- Stdlib `zipfile` and `tarfile` are sufficient — no need for `libarchive-c` (poorly maintained,
  requires C library).
- Stream-extract on copy avoids writing temporary files for every virtual file the user glances at.

## Consequences

**Positive:**
- Archives are first-class citizens — compare ZIP vs folder, TAR vs ZIP, etc.
- No external C dependencies (stdlib zipfile/tarfile only).
- Lazy expansion keeps startup fast for directories with many archives.

**Negative:**
- `tarfile` has no random-access lookup — extracting a single file requires scanning the entire
  archive (acceptable for typical use).
- Writing into archives (creating/modifying entries) is not supported.
- `zipfile` cannot reliably set mtime on extracted files (DOS timestamp resolution).

## Implementation

`src/core/archive.py` — `list_archive_at_depth()`, `extract_file()`, `is_archive()`.
`FilePane._archive_prefix` tracks current virtual path; `..` navigates back out.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| Extract to temp directory on expand | Slow for large archives; disk waste; cleanup complexity |
| FUSE mount (archivemount) | Requires kernel module; no portable Python implementation |
| libarchive-c (C library bindings) | Poorly maintained; C build dependency |
| 7z CLI subprocess | Fragile shell parsing; slower for single-file extraction |
