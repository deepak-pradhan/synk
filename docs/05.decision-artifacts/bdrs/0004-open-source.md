---
thing_id:         "synk-bdr-0004"
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
  depends_on:     ["synk-bdr-0001", "synk-bdr-0003"]
  related_to:     []
  enables:        ["synk-bdr-0005"]
tags:             [business, open-source, licensing, governance]
---

# BDR-0004: Open Source Strategy & Licensing

## Status

**Accepted** (2026-06-16).

## Context

Synk lives on a public GitHub repo. A license must be chosen, and the open-source strategy
(accept PRs? manage issues? enforce CLA?) must be defined.

## Decision

- **License:** MIT.
- **Repository:** Public on GitHub, issues open, PRs accepted.
- **Governance:** Benevolent-dictator model (single maintainer with final say).
- **No CLA requirement** for contributors.

## Rationale

### Why MIT
- Compatible with PySide6 (LGPL) — MIT code can be linked into LGPL projects without issue.
- Maximal adoption: companies use Synk in CI without legal review.
- Simple, well-understood, one-page text.

### Why open for contributions
- Low risk: the codebase is small (~2000 lines), easy to review.
- Community contributions reduce the author's maintenance burden.
- Public issue tracker serves as documentation.

### Why no CLA
- CLAs create friction for casual contributors. Risk of patent-ambush or copyright dispute is
  negligible for a project this scale.
- DCO (Developer Certificate of Origin) via `git commit -s` is sufficient.

## Consequences

**Positive:**
- Anyone can fork, modify, and redistribute.
- Low barrier to contribution encourages bug fixes.
- No legal overhead (license review, CLA management).

**Negative:**
- MIT allows a competitor to package and sell Synk with zero compensation.
- No way to prevent "bad actor" forks.
- Single-maintainer bus factor.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| GPLv3 | Incompatible with some corporate CI environments; viral obligation |
| AGPLv3 | Unnecessary for desktop utility with no network service |
| Apache 2.0 | Adds patent-retaliation clause; MIT is simpler |
| No license ("all rights reserved") | Prevents anyone from fixing bugs or packaging for distros |
