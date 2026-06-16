# BDR-004: Open Source Strategy & Licensing

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Synk lives on a public GitHub repo. A license must be chosen, and the open-source strategy (accept PRs? manage issues? enforce CLA?) must be defined.

## Decision

- **License:** MIT
- **Repository:** Public on GitHub, issues open, PRs accepted
- **Governance:** Benevolent-dictator model (single maintainer with final say)
- **No CLA requirement** for contributors

## Rationale

### Why MIT
- Compatible with PySide6 (LGPL) — MIT code can be linked into LGPL projects without issue
- Maximal adoption: companies can use Synk in CI without legal review (MIT is universally approved)
- Simple, well-understood, one-page text

### Why open for contributions
- Low risk: the codebase is small (~2000 lines), easy to review
- Community contributions (e.g., a Windows packaging fix, a new hash algorithm) reduce the author's maintenance burden
- Public issue tracker serves as documentation — "I had this error too, and here's the fix"

### Why no CLA
- CLAs create friction for casual contributors. For a project of this scale, the risk of a patent-ambush or copyright dispute is negligible.
- DCO (Developer Certificate of Origin) via `git commit -s` is sufficient.

## Consequences

**Positive:**
- Anyone can fork, modify, and redistribute — maximizes useful life of the code
- Low barrier to contribution encourages bug fixes from the community
- No legal overhead (license review, CLA management)

**Negative:**
- MIT allows a competitor to package and sell Synk with zero compensation to the author
- No way to prevent "bad actor" forks (e.g., adding telemetry)
- Single-maintainer bus factor — if the author disappears, the project dies

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| GPLv3 | Incompatible with some corporate CI environments; creates a "viral" obligation that discourages embedding |
| AGPLv3 | Even stronger network-effects clause; unnecessary for a desktop utility with no network service |
| Apache 2.0 | Good, but adds patent-retaliation clause that is overkill for a diff tool; MIT is simpler |
| No license ("all rights reserved") | Prevents anyone from fixing bugs or packaging for distros — counterproductive for a public repo |
