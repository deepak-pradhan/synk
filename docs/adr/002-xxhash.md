# ADR-002: xxHash for Fast Content Comparison

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Determining whether two files are identical is the core operation. Doing this via byte-by-byte comparison is O(n) but slow for large files. A content hash pre-filter avoids loading file contents into memory for every comparison.

## Decision

Use **xxHash** (`xxh3_64`) as the default hash algorithm, with SHA-256 as a configurable alternative.

## Rationale

- xxHash is 10–50× faster than SHA-256 for large files (CPU-bound at ~10 GB/s on modern hardware vs ~0.5 GB/s for SHA-256).
- A 64-bit hash (`xxh3_64`) has a collision probability of ~2^-64 per pair — negligible for a file comparison tool. False positives (treating different files as identical) are caught at the diff stage or by a secondary hash check.
- The `xxhash` Python package provides native bindings with no external dependencies.
- A dual-hash strategy is available: use xxh3_64 for the initial pass, and fall back to SHA-256 for verification before destructive operations (e.g., before deleting a "duplicate").

## Consequences

**Positive:**
- Near-instant comparison of large files (multi-GB ISOs, disk images)
- CPU-bound hashing is trivially parallelizable across multiple cores
- Configurable algorithm lets users trade speed for collision resistance

**Negative:**
- xxh3_64 is non-cryptographic — not suitable for security-critical integrity verification
- Collision probability, while negligible, is non-zero — may surprise users familiar only with SHA
- Requires the `xxhash` PyPI dependency (not in stdlib)

## Implementation

`src/core/hasher.py:13` — `Hasher` class with pluggable algorithm dispatch:

```python
_hash_funcs = {
    "xxh3_64": ...  # default, ~10 GB/s
    "xxh64": ...    # ~8 GB/s
    "md5": ...      # ~1 GB/s
    "sha1": ...     # ~0.8 GB/s
    "sha256": ...   # ~0.5 GB/s
}
```

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| SHA-256 default | 10–50× slower; no benefit for a desktop diff tool where collision risk is near zero |
| MD5 default | Faster than SHA but vulnerable to collision attacks; similar speed to xxh64 |
| File size + mtime only | Insufficient — mtime changes without content change (git checkout, cp --preserve) or identical mtimes with different content |
| Byte-by-byte comparison | Reads entire file into memory; no streaming; no ability to cache comparison results |
