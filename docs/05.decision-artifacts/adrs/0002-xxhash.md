---
thing_id:        "synk-adr-0002"
thing_type:      "adr"
adr_id:          "0002"
domain:          "synk"
phase:           "p0-foundations"
version:         "1.0"
lifecycle_state: "approved"
deciders:        "Deepak"
reversibility:   "high"
decision_date:   "2026-06-14"
last_updated:    "2026-06-16"
next_review_date: "2026-09-16"
priority:        "high"
confidentiality: "internal"
tags:            [hashing, xxhash, performance, comparison-engine]
relations:
  depends_on:    []
  related_to:    ["synk-moscow-0001"]
  enables:       []
---

# ADR-0002: xxHash for Fast Content Comparison

## Status

**Accepted** (2026-06-14). Default algorithm is `xxh3_64`; SHA-256 available as configurable
alternative.

## Context

Determining whether two files are identical is the core operation. Byte-by-byte comparison is O(n)
but slow for large files. A content hash pre-filter avoids loading file contents into memory for
every comparison pair.

## Decision

Use **xxHash** (`xxh3_64`) as the default hash algorithm, with SHA-256 as a configurable
alternative. Support multiple algorithms via pluggable dispatch.

## Rationale

- xxHash is 10–50× faster than SHA-256 for large files (~10 GB/s vs ~0.5 GB/s).
- 64-bit hash (`xxh3_64`) collision probability is ~2^-64 per pair — negligible for a file
  comparison tool. False positives (treating different files as identical) are caught at the diff
  stage or by a secondary hash check.
- The `xxhash` Python package provides native bindings with no external dependencies.
- Dual-hash strategy: use xxh3_64 for the initial pass, fall back to SHA-256 for verification
  before destructive operations (e.g., before deleting a "duplicate").

## Consequences

**Positive:**
- Near-instant comparison of large files (multi-GB ISOs, disk images).
- CPU-bound hashing is trivially parallelizable across multiple cores.
- Configurable algorithm lets users trade speed for collision resistance.

**Negative:**
- xxh3_64 is non-cryptographic — not suitable for security-critical integrity verification.
- Collision probability, while negligible, is non-zero.
- Requires the `xxhash` PyPI dependency (not in stdlib).

## Implementation

`src/core/hasher.py:13` — `Hasher` class with pluggable algorithm dispatch.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| SHA-256 default | 10–50× slower; no benefit for desktop diff tool |
| File size + mtime only | Insufficient — mtime changes without content change, or identical mtimes with different content |
| Byte-by-byte comparison | Reads entire file into memory; no streaming; no ability to cache results |
