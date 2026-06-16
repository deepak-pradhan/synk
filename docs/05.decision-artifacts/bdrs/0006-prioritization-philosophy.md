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
| Side-by-side file diff | High — daily config drift checks | Must | Built M1–2 |
| Archive browsing | High — verifying backup tarballs | Must | Built M7 |
| SFTP remote | Medium — server migrations quarterly | Should | Built M8 |
| 3-way merge | Medium — occasional Git conflict resolution | Could | Built v0.2 |
| Plugin system | None — no concrete pain | Won't | Deferred indefinitely |
