---
thing_id:         "synk-bdr-0006"
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
  depends_on:     ["synk-bdr-0001", "synk-bdr-0002"]
  related_to:     ["synk-moscow-0001"]
  enables:        []
tags:             [business, prioritization, dogfood, philosophy]
---

# BDR-0006: Feature Prioritization Philosophy

## Status

**Accepted** (2026-06-16).

## Context

With limited engineering bandwidth, a principled way to decide what gets built — and what gets
deferred or rejected — is critical. Features compete for time against each other and against other
life/project priorities.

## Decision

Features are prioritized using a **pain-driven, dogfood-first** model:

1. **Does the author need it this week?** → High priority.
2. **Does it unblock a common workflow?** → Medium priority.
3. **Does it look cool but solve no real pain?** → Low / Defer.
4. **Does it introduce ongoing maintenance cost?** → Scrutinize hard.

## Rationale

- The author is the sole user whose pain is directly observable. If it doesn't hurt them, it's
  hard to validate the priority.
- Dogfooding — using Synk for real work (deployment verification, backup checks, config diffing) —
  surfaces genuine gaps. SFTP and archive browsing came from actual server-migration scenarios.
- Engineering time is finite. A feature taking 2 days to build but saving 10 min/month is likely
  never worth it unless it removes a recurring frustration.
- This model converges on a minimal, useful core — the right outcome for a personal utility.

## Consequences

**Positive:**
- Every feature has a concrete use case the author has experienced.
- No "shelfware" features that sound good but never get used.
- Quick iteration cycle: pain → code → relief.

**Negative:**
- Features the author doesn't need (Windows, i18n, theming) may never get built.
- Bias toward the author's workflows may miss valuable community use cases.
- Hard to deprioritize a feature once the author personally wants it.

## Examples Applied

| Feature | Pain Level | Priority | Outcome |
|---------|-----------|----------|---------|
| Side-by-side file diff | High — daily config drift checks | Must | Built by v0.1 |
| Archive browsing | High — verifying backup tarballs | Must | Built by v0.1.5 |
| SFTP remote | Medium — server migrations quarterly | Should | Built by v0.1.8 |
| 3-way merge | Medium — occasional Git conflict resolution | Could | Built in v0.2 |
| Plugin system | None — no concrete pain | Won't | Deferred indefinitely |

## Bug / Security Override

The pain-driven model applies to **features**, not to defects or security issues.

| Category | Rule |
|----------|------|
| Critical bug (data loss, crash, wrong comparison result) | Outranks all feature work; fix immediately. |
| Security issue | Outranks feature work; fix and disclose per `synk-bdr-0004`. |
| Minor bug with no workaround | Treated as "Should" if it blocks a common workflow; otherwise "Could". |
| Cosmetic / nice-to-have | Competes with features under the standard pain model. |

## Escalation Path

1. **Personal pain:** author opens issue, tags it, and schedules it.
2. **External user bug:** triaged within 7 days; if it affects a common workflow, escalated to "Should" or "Must".
3. **Security issue:** handled privately and fixed out-of-band from the public roadmap.

## Mapping to MoSCoW

This philosophy maps to `synk-moscow-0001` as follows:

| Philosophy Bucket | MoSCoW Bucket |
|-------------------|---------------|
| "Does the author need it this week?" | Must |
| "Does it unblock a common workflow?" | Should |
| "Does it look cool but solve no real pain?" | Could |
| "Introduces ongoing maintenance cost" | Won't or deferred until pain justifies it |

## Rejected or Deferred Features Log

| Feature | Pain Level | Decision | Rationale |
|---------|-----------|----------|-----------|
| Plugin system | None | Won't | No concrete use case; API surface would become a maintenance burden. |
| Windows native installer | Low | Won't | Author is not a Windows user; WSL is acceptable for cross-platform users. |
| Built-in cloud sync / account system | None | Won't | Conflicts with personal-utility positioning and adds privacy risk. |

## Related Records

- Operationalizes `synk-bdr-0002` (target audience: only build what the audience needs).
- Constrained by `synk-bdr-0003` (monetization: no paid team to build "nice-to-haves").
- Implemented through `synk-moscow-0001` (core feature build sequence).
