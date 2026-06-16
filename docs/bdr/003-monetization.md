# BDR-003: Monetization Strategy

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Even for a personal project, there are incidental costs: PyPI hosting, domain registration (if any), CI minutes, and the author's engineering time. A monetization decision is needed to set expectations.

## Decision

Synk is **free of charge, MIT-licensed, and not monetized**.

## Rationale

- The project's primary ROI is skill-building and solving the author's own problems — not revenue.
- Charging money creates expectations (support SLAs, bug-fix velocity, feature requests) that a solo developer cannot sustain.
- An MIT license maximizes adoption and contribution potential. Other developers can use Synk in their CI pipelines, embed it in their tools, or package it for their distro without legal friction.
- PyPI distribution is essentially free; GitHub Actions has a generous free tier. Recurring costs are near zero.

## Consequences

**Positive:**
- Zero pricing friction — anyone can `pip install synk-diff` and use it immediately
- No sales tax, invoicing, payment processing, or refund handling
- MIT license encourages forks, contributions, and derivative use

**Negative:**
- No direct financial return on engineering investment
- No budget for paid dependencies, CI runners, or design work
- Risk of abandonment if author loses interest — no commercial incentive to maintain

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| MIT + "Sponsor" button (GitHub Sponsors) | Worth adding if anyone asks, but not actively pursued — lowers priority over code |
| Open-core (free core, paid merge/archive) | Over-engineered for a single-developer project; adds licensing complexity |
| Paid license ($10–$20) | Creates support expectations, would likely net < \$500 total — not worth the distraction |
