---
thing_id:         "synk-bdr-0007"
thing_type:       "bdr"
domain:           "synk"
lifecycle_state:  "approved"
priority:         "high"
confidentiality:  "internal"
owner:            "Deepak"
version:          "1.0"
last_updated:     "2026-06-16"
next_review_date: "2026-09-16"
relations:
  depends_on:     ["synk-bdr-0002", "synk-bdr-0004"]
  related_to:     ["synk-adr-0007"]
  enables:        []
tags:             [business, privacy, telemetry, security, data-handling]
---

# BDR-0007: Data Privacy & Telemetry

## Status

**Accepted** (2026-06-16).

## Context

Synk is a file/directory comparison tool that inherently accesses sensitive user data: local file
paths, file contents, archive contents, and SFTP credentials. Users, especially in CI or server-admin
contexts, need to know what the tool transmits, stores, or logs.

## Decision

Synk operates under a **local-first, no-telemetry, no-analytics** policy:

1. **No telemetry, analytics, or crash reporting** is collected or transmitted by the application.
2. **File contents and paths are processed locally** and are never uploaded to any third-party service.
3. **SFTP credentials** are held in memory only while a connection is active; they are not written to
the config file, session files, or logs.
4. **Session and config files** are stored locally on disk; the user is responsible for their host
security.
5. **Logs and error output** must not include passwords, key file contents, or full file contents.
6. **No network calls** are made except explicit user-initiated SFTP/SSH connections and package-manager
operations (`pip install`) outside the application.

## Rationale

- A diff/merge tool processes user data by definition. Any transmission would violate user trust and
  create compliance risk (GDPR, CCPA, SOC 2).
- A solo-maintainer project cannot operate a telemetry backend responsibly (security, retention,
  access controls).
- Local-first operation keeps the attack surface minimal and aligns with the personal-utility
  positioning.
- CI/automation users need deterministic, offline-capable behavior.

## Consequences

**Positive:**
- No privacy policy, cookie banner, or data-processing agreement is required.
- No backend infrastructure to secure or pay for.
- Users can audit the claim by inspecting the source code.
- Works fully offline (GUI excepted for Qt platform plugins).

**Negative:**
- No usage data to inform feature prioritization beyond direct feedback.
- No automatic crash reports; users must open issues manually.
- Author cannot detect abuse or unusual usage patterns.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|--------------|
| Optional opt-in telemetry | Adds code, UI, and policy complexity for marginal insight |
| Crash reporter (e.g., Sentry) | Sends stack traces and paths to a third party; privacy risk |
| Cloud-backed sync for sessions | Conflicts with local-first principle; adds storage and security burden |

## Data Inventory

| Data Type | Where Stored | Transmitted? | Notes |
|-----------|--------------|--------------|-------|
| Local file contents | Memory only | No | Hashed or diffed locally |
| Local file/directory paths | Memory, session TOML | No | User controls session file location |
| SFTP host/username | Memory, optionally session TOML | No | Password stripped before persistence |
| SFTP password / key passphrase | Memory only | No | Never persisted or logged |
| SFTP private key path | Memory, session TOML | No | Path only; key file never read by Synk for logging |
| Hash values | Memory only | No | Used for comparison |
| Config preferences (theme, hash algo, ignore patterns) | `~/.config/beyondcomp/config.toml` | No | Local only |
| Last session | `~/.config/beyondcomp/last_session.toml` | No | Local only |

## Incident Response

If a future code change is discovered to have transmitted or logged user data contrary to this policy:

1. Revert or patch the offending change immediately.
2. Publish a security advisory via GitHub.
3. Notify users in the release notes with mitigation steps.
4. Update this BDR to capture root cause and new safeguards.

## Related Records

- Informed by `synk-bdr-0002` (target audience: CI/automation users need offline, trustworthy tools).
- Governance and disclosure tied to `synk-bdr-0004` (open-source security response).
- Technical implementation constrained by `synk-adr-0007` (SFTP/paramiko module design).
