# BDR-002: Target Audience & Positioning

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Synk could be positioned as a general-purpose commercial competitor to Beyond Compare, a personal utility, or a developer-focused CLI/GUI hybrid. The positioning drives UX priorities, feature scope, and distribution.

## Decision

Position Synk as a **personal/casual utility for developers and power users** — not a commercial product.

## Rationale

- The primary stakeholder is the author, who needs a cross-platform diff tool for deployment verification, backup integrity checks, and config drift detection.
- Developer/power-user focus means we optimize for keyboard-driven workflows, headless CI/CLI mode, and fast hashing — features that enterprise users also value, but without the support overhead.
- "Personal utility" eliminates the pressure to match Beyond Compare's 100% feature matrix. We ship what we need, when it's ready.
- The name "Synk" (intentionally misspelled) signals it's a pragmatic tool, not a polished retail product.

## Consequences

**Positive:**
- No sales, marketing, or support overhead
- Can ship v0.1 with a minimal feature set and iterate based on personal need
- CLI-first design carries over to CI/automation use cases without extra work

**Negative:**
- No revenue stream — all engineering time is unrecoverable cost
- Limited community contributions (no corporate backer)
- Feature decisions are top-down (author's needs), not market-driven

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Commercial product (paid license) | Creates support burden, tax/compliance overhead, pricing pressure |
| Enterprise-only (bulk licensing) | Requires sales effort far beyond the scope of a 3-week build |
| Donation-ware / open-core | More complexity than value for a single-developer project |
