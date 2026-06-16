# BDR-006: Feature Prioritization Philosophy

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

With limited engineering bandwidth, a principled way to decide what gets built — and what gets deferred or rejected — is critical. Features compete for time against each other and against other life/project priorities.

## Decision

Features are prioritized using a **pain-driven, dogfood-first** model:

1. **Does the author need it this week?** → High priority
2. **Does it unblock a common workflow?** → Medium priority
3. **Does it look cool but solve no real pain?** → Low / Defer
4. **Does it introduce ongoing maintenance cost?** → Scrutinize hard

## Rationale

- The author is the sole user whose pain is directly observable. If it doesn't hurt them, it's hard to validate the priority.
- "Dogfooding" — using Synk for real work (deployment verification, backup checks, config diffing) — surfaces genuine gaps. Features like SFTP and archive browsing came from actual server-migration and backup-verification scenarios.
- Engineering time is finite. A feature that takes 2 days to build and saves 10 minutes per month is likely never worth it unless it removes a recurring frustration.
- This model naturally converges on a minimal, useful core — exactly the right outcome for a personal utility.

## Consequences

**Positive:**
- Every feature in the product has a concrete use case the author has experienced
- No "shelfware" features that sound good but never get used
- Quick iteration cycle: pain → code → relief, repeat

**Negative:**
- Features the author doesn't need (Windows support, non-English i18n, theming beyond dark/light) may never get built, limiting broader adoption
- Bias toward the author's workflows may miss valuable community use cases
- Hard to deprioritize a feature once the author personally wants it, even if it's technically risky

## Examples Applied

| Feature | Pain Level | Priority | Outcome |
|---------|-----------|----------|---------|
| Side-by-side file diff | High — needed for daily config drift checks | Must | Built in M1–2 |
| Archive browsing | High — verifying backup tarballs | Must | Built in M7 |
| SFTP remote | Medium — server migrations happen quarterly | Should | Built in M8 |
| 3-way merge | Medium — occasional Git conflict resolution | Could | Built in v0.2 |
| Theming (light/dark) | Low — cosmetic | Could | Built |
| Plugin system | None — no concrete pain yet | Won't | Deferred indefinitely |
| Windows packaging | Low — author uses Linux | Won't | Open to community PR |
