# ADR-007: SFTP Remote via Paramiko

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Synk needs to compare local directories against remote servers over SSH/SFTP. The remote module must support listing files, reading content for hashing/diff, and transferring files (download/upload).

## Decision

Use **paramiko** (pure-Python SSHv2 implementation) for all SFTP operations.

## Rationale

- Paramiko is the de-facto standard Python SSH library, actively maintained, and well-documented.
- No external C dependencies (uses `bcrypt`, `nacl`, `cryptography` but all are pure-Python-available).
- `SFTPClient` provides the full SFTP protocol: `listdir_attr`, `stat`, `open` (read/write), `get`, `put`, `remove`, `mkdir`, `rmdir`, `rename` — every operation Synk needs.
- `AutoAddPolicy` handles unknown host keys (acceptable for a personal tool; a production tool would prompt).
- SSH agent forwarding and key-based auth work out of the box — no password prompt for users with `ssh-agent`.

## Consequences

**Positive:**
- Full remote file operations — list, stat, read, write, delete, rename
- Hash a remote file by streaming its content through SFTP (no shell command needed on the server)
- Can compare local ↔ remote, or even remote ↔ remote (two SFTP connections)

**Negative:**
- Paramiko is a large dependency (~2 MB) with several transitive cryptography dependencies
- SFTP hash computation requires reading the entire file over the network — slow for large files on slow connections
- No server-side hashing (no `md5sum`/`sha256sum` execution on the remote) — the file is streamed to the client for hashing
- `AutoAddPolicy` is a security risk (MITM) in production; acceptable for a personal utility

## Implementation

`src/core/remote.py`:

```python
class SFTPConnection:
    def __init__(self, creds: SFTPCredentials): ...
    def connect(self) -> str: ...         # returns error string or ""
    def disconnect(self): ...
    def list_dir(self, path) -> list[RemoteEntry]: ...
    def stat(self, path) -> Optional[RemoteEntry]: ...
    def hash_remote_file(self, path, algorithm) -> Optional[str]: ...
    def read_text(self, path, encoding) -> Optional[str]: ...
    def download_file(self, remote_path, local_path) -> bool: ...
    def upload_file(self, local_path, remote_path) -> bool: ...
```

URL format: `sftp://user@host:port/path` — parsed by `parse_sftp_url()` using `urllib.parse`.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| `asyncssh` | Asynchronous API doesn't integrate well with Qt's event loop without `qasync` |
| Subprocess `scp`/`sftp` CLI | Fragile, no structured file info, slow for many small files (new connection per command) |
| `fabric` / `invoke` (wraps paramiko) | Adds abstraction layer with no benefit for file-comparison use case; more deps |
| `pysftp` (fork of paramiko wrapper) | Unmaintained since 2020; wraps paramiko with no added value |
