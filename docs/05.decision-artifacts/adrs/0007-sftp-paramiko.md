---
thing_id:        "synk-adr-0007"
thing_type:      "adr"
adr_id:          "0007"
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
tags:            [sftp, remote, paramiko, ssh, file-transfer]
relations:
  depends_on:    []
  related_to:    ["synk-moscow-0001"]
  enables:       []
---

# ADR-0007: SFTP Remote via Paramiko

## Status

**Accepted** (2026-06-15). Implemented in v0.2 M8.

## Context

Synk needs to compare local directories against remote servers over SSH/SFTP. The remote module
must support listing files, reading content for hashing/diff, and transferring files (download/upload).

## Decision

Use **paramiko** (pure-Python SSHv2 implementation) for all SFTP operations.

## Rationale

- Paramiko is the de-facto standard Python SSH library, actively maintained, well-documented.
- No external C dependencies.
- `SFTPClient` provides the full SFTP protocol: `listdir_attr`, `stat`, `open` (read/write),
  `get`, `put`, `remove`, `mkdir`, `rmdir`, `rename` — every operation Synk needs.
- `AutoAddPolicy` handles unknown host keys (acceptable for personal tool).
- SSH agent forwarding and key-based auth work out of the box.

## Consequences

**Positive:**
- Full remote file operations — list, stat, read, write, delete, rename.
- Hash a remote file by streaming its content through SFTP.
- Can compare local ↔ remote, or remote ↔ remote (two SFTP connections).

**Negative:**
- Paramiko is a large dependency (~2 MB) with several transitive cryptography dependencies.
- SFTP hash computation requires reading the entire file over the network.
- No server-side hashing — file is streamed to client for hashing.
- `AutoAddPolicy` is a security risk (MITM) in production; accepted for personal utility.

## Implementation

`src/core/remote.py` — `SFTPConnection` class wrapping paramiko.
URL format: `sftp://user@host:port/path` — parsed by `parse_sftp_url()`.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| `asyncssh` | Async API doesn't integrate with Qt event loop without `qasync` |
| Subprocess `scp`/`sftp` CLI | Fragile, no structured file info, slow for many small files |
| `fabric` / `invoke` | Adds abstraction layer with no benefit for comparison use case |
| `pysftp` | Unmaintained since 2020 |
