---
thing_id:         "synk-bdr-0003"
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
  depends_on:     ["synk-bdr-0001", "synk-bdr-0002"]
  related_to:     ["synk-bdr-0004", "synk-bdr-0005"]
  enables:        []
tags:             [business, monetization, pricing, strategy]
---

# BDR-0003: Monetization Strategy

## Status

**Accepted** (2026-06-16).

## Context

Even for a personal project, there are incidental costs: PyPI hosting, CI minutes, and the
author's engineering time. A monetization decision is needed to set expectations.

## Decision

Synk is **free of charge, MIT-licensed, and not monetized**.

## Rationale

- The project's primary ROI is skill-building and solving the author's own problems — not revenue.
- Charging creates expectations (support SLAs, bug-fix velocity, feature requests) a solo developer
  cannot sustain.
- MIT license maximizes adoption and contribution potential. Others can use Synk in CI pipelines,
  embed it in tools, or package for their distro without legal friction.
- PyPI distribution is essentially free; GitHub Actions has a generous free tier.

## Consequences

**Positive:**
- Zero pricing friction — `pip install synk-diff` works immediately.
- No sales tax, invoicing, payment processing, or refund handling.
- MIT license encourages forks, contributions, and derivative use.

**Negative:**
- No direct financial return on engineering investment.
- No budget for paid dependencies, CI runners, or design work.
- Risk of abandonment if author loses interest — no commercial incentive to maintain.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| MIT + "Sponsor" button (GitHub Sponsors) | Worth adding if asked, but not actively pursued |
| Open-core (free core, paid merge/archive) | Over-engineered for single-developer project |
| Paid license ($10–$20) | Creates support expectations; would net < $500 total |

## Sustainability Threshold

Synk remains free unless the **annual incidental cost** exceeds the following bands:

| Band | Annual Cost | Action |
|------|-------------|--------|
| Green | ≤ $50 | Absorb personally; no change. |
| Yellow | $50–$200 | Enable GitHub Sponsors link and mention it in README; donations optional. |
| Red | > $200 | Revisit monetization decision in a new BDR; consider accepting sponsorships or adding a paid tier only if support burden can be managed. |

Current incidental costs are limited to PyPI hosting (free) and GitHub Actions free-tier minutes.

## Financial Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| No revenue, project abandoned | Medium | High | Keep scope small; dogfood daily; document clearly |
| CI minutes exceed free tier | Low | Low | Move heavy jobs to scheduled runs; cache aggressively |
| Unexpected paid dependency needed | Low | Medium | Prefer stdlib/MIT dependencies; audit before adding |

## Related Records

- Enabled by `synk-bdr-0001` (build vs buy) and `synk-bdr-0002` (target audience).
- Enables `synk-bdr-0004` (open-source licensing) and `synk-bdr-0005` (distribution).
