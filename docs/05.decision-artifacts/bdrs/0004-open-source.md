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

### Sign-off / DCO
- No formal Developer Certificate of Origin (DCO) requirement is currently enforced.
- Contributors grant rights implicitly by submitting a PR under the MIT license.
- If the project later needs signed commits, a DCO check will be added to CI and documented here.

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

## Security Response

- **Reporting channel:** Security-sensitive issues should be reported via GitHub private vulnerability report or direct email to the author; public issues for undisclosed vulnerabilities are discouraged.
- **Acknowledgment:** Reporter will be acknowledged within 7 days; a fix or public disclosure plan will be shared within 30 days for confirmed vulnerabilities.
- **Disclosure policy:** Coordinated disclosure; details kept private until a patch is released and users have a reasonable upgrade window.

## Contribution Triage SLA

| Item | Target |
|------|--------|
| Bug reports triaged and labeled | 7 days |
| Pull requests reviewed | 14 days |
| Feature requests | No SLA; evaluated against `synk-bdr-0006` prioritization philosophy |
| Author's own issues/PRs | Same targets to avoid self-bias |

## Bus Factor & Succession

- Current bus factor is 1 (single maintainer).
- Mitigation: keep the codebase small and well-documented; use standard Python packaging; store decision artifacts in-repo; publish to PyPI so the package can outlive the repo if necessary.
- If the author steps away for > 6 months, the README will be updated to mark the project as "maintenance mode" and invite new maintainers.

## Related Records

- Enabled by `synk-bdr-0001` (build vs buy) and `synk-bdr-0003` (monetization).
- Enables `synk-bdr-0005` (distribution).
- Governance operates alongside `synk-bdr-0006` (prioritization) when accepting contributions.
