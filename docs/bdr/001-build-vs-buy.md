# BDR-001: Build vs Buy — Why Build Synk

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

The problem space — file/directory comparison and merging — is well-served by mature tools: Beyond Compare (paid), Meld (free), diff/kdiff3 (CLI), WinMerge, VS Code's built-in diff. The question is why invest engineering time in yet another one.

## Decision

Build Synk from scratch rather than extending or wrapping existing tools.

## Rationale

| Factor | Assessment |
|--------|-----------|
| **License constraints** | Beyond Compare costs \$60/seat, Meld is GTK-only and unmaintained, WinMerge is Windows-only. No single tool covers Linux + archive browsing + SFTP + 3-way merge in a unified package under a permissive license. |
| **Integration surface** | Existing tools expose no programmable Python API. Wrapping them via subprocess (`diff`, `meld --diff`) is fragile, slow, and breaks on version drift. A native Python library chain (diff-match-patch, xxhash, paramiko) gives us reliable, testable primitives. |
| **Skill investment** | Building the engine ourselves builds deep knowledge of diff algorithms, hashing strategies, and Qt patterns — directly applicable to the author's broader career (dev tooling, infrastructure). Buying a tool gives none of that. |
| **Feature control** | Beyond Compare's road map is opaque. Archives, SFTP, 3-way merge, and a headless CLI mode are all "nice to have" for them — we can ship them as core features on day one. |
| **Total cost** | Engineering time is real, but the project is capped at ~3 weeks of part-time work (per implementation plan). At a consulting rate, that's less than 4 Beyond Compare licenses — and the IP stays ours. |

## Consequences

**Positive:**
- Full control over feature set and release cadence
- Permissive license (MIT) allows free redistribution, CI integration, and embedding
- Portable CLI mode enables use in automated pipelines (no X11 required)

**Negative:**
- Upfront time investment before reaching parity with Beyond Compare's polish
- Maintenance burden of Qt/paramiko bindings across Python versions
- No commercial support — user must self-diagnose

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Use Beyond Compare | Paid license, no Linux CLI mode, no programmable API |
| Contribute to Meld | GTK4 migration stalled, maintainer bandwidth limited, roadmap misalignment |
| VS Code extension | Tied to editor runtime, no headless mode, no archive browsing |
| Shell script wrapper around `diff -rq` + `sha256sum` | Works for basic checks but no GUI, no merge, no session save/load |
