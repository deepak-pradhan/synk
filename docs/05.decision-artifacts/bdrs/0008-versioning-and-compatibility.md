---
thing_id:         "synk-bdr-0008"
thing_type:       "bdr"
domain:           "synk"
lifecycle_state:  "approved"
priority:         "medium"
confidentiality:  "internal"
owner:            "Deepak"
version:          "1.0"
last_updated:     "2026-06-16"
next_review_date: "2026-09-16"
relations:
  depends_on:     ["synk-bdr-0001", "synk-bdr-0005"]
  related_to:     ["synk-moscow-0001"]
  enables:        []
tags:             [business, versioning, compatibility, releases, support]
---

# BDR-0008: Versioning & Compatibility

## Status

**Accepted** (2026-06-16).

## Context

As Synk ships releases and users begin to depend on CLI flags, config files, and session files, the
project needs a predictable versioning and compatibility policy. Without one, every dependency bump
or config schema change risks surprising users or breaking automation.

## Decision

- **Versioning scheme:** Semantic Versioning 2.0.0 (`MAJOR.MINOR.PATCH`).
- **Release cadence:** As-needed; no fixed schedule. Tags follow the `v*.*.*` pattern.
- **Supported Python versions:** Current release line supports Python 3.12+. Future minor releases may
  add support for newer Python versions; they will not drop support within a major version unless
  unavoidable.
- **Backward compatibility:**
  - **CLI commands and flags:** Breaking changes require a major version bump.
  - **Config file (`config.toml`):** New minor versions remain backward-compatible with existing
    config files; unknown keys are ignored.
  - **Session files (`.bc-session`, `last_session.toml`):** Best-effort backward compatibility for
    one minor version; older sessions may be loaded with defaults for missing fields.
  - **PySide6 / paramiko / xxhash dependencies:** Patch updates may bump dependency minimums to
    address security issues; such bumps are documented in release notes and do not require a major
    version bump unless they force a breaking public API change.
- **Deprecation process:** Features intended for removal are marked deprecated in at least one
  minor release before removal in a subsequent major or minor release, with a note in `README.md`
  and release notes.
- **LTS / support windows:** No long-term support lines. Only the latest release is actively
  maintained.

## Rationale

- SemVer is the de facto standard in the Python ecosystem and is expected by CI/automation users.
- A single active release line keeps maintenance burden low for a solo maintainer.
- Best-effort session compatibility is sufficient for a personal utility; strict schema migrations
  would be over-engineering at this stage.
- Dependency minimum bumps for security are treated as patches or minors because they do not change
  Synk's own public API.

## Consequences

**Positive:**
- Users can pin `synk-diff~=0.2` and expect non-breaking additions.
- Release notes communicate risk clearly.
- Low maintenance overhead.

**Negative:**
- No LTS means users who cannot upgrade frequently may be stranded on an unmaintained version.
- Dropping a Python version requires a major or clearly-communicated minor bump.
- Third-party packagers (distros) may want longer support windows than offered.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|--------------|
| Calendar versioning (CalVer) | Less useful for dependency pinning and automation users |
| ZeroVer (0.x forever) | Makes it hard to signal breaking CLI changes |
| Multiple LTS branches | Too much maintenance for a solo project |
| Strict semver for dependencies too | Dependency minimum bumps are not public API changes; would force major bumps for security patches |

## Compatibility Matrix

| Version | Python | Status |
|---------|--------|--------|
| 0.2.x | 3.12+ | Active |

## Deprecation Log

No deprecated features as of v0.2.0.

## Related Records

- Enabled by `synk-bdr-0001` (build vs buy: the project must maintain what it builds).
- Implemented through `synk-bdr-0005` (distribution: release tags trigger PyPI publish).
- Operationalized by `synk-moscow-0001` (core feature build sequence).
