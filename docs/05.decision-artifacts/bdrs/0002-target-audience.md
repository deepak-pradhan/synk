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
