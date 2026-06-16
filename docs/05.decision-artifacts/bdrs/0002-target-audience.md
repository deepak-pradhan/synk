---
thing_id:         "synk-bdr-0002"
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
  depends_on:     ["synk-bdr-0001"]
  related_to:     ["synk-bdr-0006"]
  enables:        []
tags:             [business, audience, positioning, strategy]
---

# BDR-0002: Target Audience & Positioning

## Status

**Accepted** (2026-06-16).

## Context

Synk could be positioned as a general-purpose commercial competitor to Beyond Compare, a personal
utility, or a developer-focused CLI/GUI hybrid. The positioning drives UX priorities, feature
scope, and distribution.

## Decision

Position Synk as a **personal/casual utility for developers and power users** — not a commercial
product.

## Rationale

- The primary stakeholder is the author, who needs a cross-platform diff tool for deployment
  verification, backup integrity checks, and config drift detection.
- Developer/power-user focus optimizes for keyboard-driven workflows, headless CLI mode, and fast
  hashing — features enterprise users also value, but without the support overhead.
- "Personal utility" eliminates the pressure to match Beyond Compare's 100% feature matrix.
- The name "Synk" (intentionally misspelled) signals it's a pragmatic tool, not a polished retail
  product.

## Consequences

**Positive:**
- No sales, marketing, or support overhead.
- Can ship v0.1 with minimal feature set and iterate based on personal need.
- CLI-first design carries over to CI/automation without extra work.

**Negative:**
- No revenue stream — unrecoverable engineering cost.
- Limited community contributions (no corporate backer).
- Feature decisions are top-down (author's needs), not market-driven.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| Commercial product (paid license) | Creates support burden, tax/compliance overhead, pricing pressure |
| Enterprise-only (bulk licensing) | Requires sales effort far beyond scope |
| Donation-ware / open-core | More complexity than value for single-developer project |

## Target Personas

| Persona | Primary Need | Typical Workflow |
|---------|--------------|------------------|
| Linux developer | Fast, keyboard-friendly diff/merge | `synk diff dirA/ dirB/` from terminal |
| CI/automation maintainer | Headless comparison in pipelines | `synk hash` or `synk compare` in GitHub Actions |
| Backup/server administrator | Verify archive integrity and remote files | Browse `.tar.gz` and compare against SFTP path |

## Explicitly Not the Target Audience

- **Enterprise buyers** needing support SLAs, vendor questionnaires, or dedicated account management.
- **Windows-only users** without WSL or a cross-platform workflow (Windows support is not a v0.x goal).
- **Non-technical end users** who need a wizard-driven setup or cannot install Python/Qt6 dependencies.

## Positioning Statement

> For Linux developers and power users who need a free, scriptable, cross-pane diff and merge tool, Synk is a personal utility that combines GUI convenience with headless CLI automation. Unlike Beyond Compare, Synk is MIT-licensed and includes archive/SFTP/3-way merge support; unlike Meld, it is actively maintained and Qt6-based.

## Adoption Success Metric

100+ PyPI downloads in the first 90 days after v0.2.0 release, measured via PyPI stats, with at least one external issue or PR opened by a non-author user.

## If the Metric Is Missed

No change to positioning or distribution. Synk remains a personal utility, and the author continues
to dogfood it. The metric is a signal, not a threshold for abandonment. A follow-up BDR would only be
opened if external adoption collapses *and* the author stops using the tool personally.

## Related Records

- Informs `synk-bdr-0001` (build vs buy), `synk-bdr-0003` (monetization), and `synk-bdr-0006` (prioritization).
- Operationalized by `synk-moscow-0001` (core feature build sequence).
