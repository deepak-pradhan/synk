---
thing_id:         "synk-bdr-0001"
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
  depends_on:     []
  related_to:     ["synk-bdr-0002"]
  enables:        ["synk-bdr-0003", "synk-bdr-0004", "synk-bdr-0005", "synk-bdr-0006"]
tags:             [business, build-vs-buy, strategy]
---

# BDR-0001: Build vs Buy — Why Build Synk

## Status

**Accepted** (2026-06-16).

## Context

The problem space — file/directory comparison and merging — is well-served by mature tools:
Beyond Compare (paid), Meld (free), diff/kdiff3 (CLI), WinMerge, VS Code's built-in diff. The
question is why invest engineering time in yet another one.

## Decision

Build Synk from scratch rather than extending or wrapping existing tools.

## Rationale

| Factor | Assessment |
|--------|-----------|
| **License constraints** | Beyond Compare costs $60/seat; Meld is GTK-only and unmaintained; WinMerge is Windows-only. No single tool covers Linux + archives + SFTP + 3-way merge in a unified package under a permissive license. |
| **Integration surface** | Existing tools expose no programmable Python API. Wrapping via subprocess is fragile and version-sensitive. A native Python library chain gives reliable, testable primitives. |
| **Skill investment** | Building the engine builds deep knowledge of diff algorithms, hashing strategies, and Qt patterns — directly applicable to the author's broader career in dev tooling/infrastructure. |
| **Feature control** | Beyond Compare's roadmap is opaque. Archives, SFTP, 3-way merge, and headless CLI are core features here. |
| **Total cost** | ~3 weeks part-time engineering. At a consulting rate, less than 4 Beyond Compare licenses — and the IP stays ours. |

## Consequences

**Positive:**
- Full control over feature set and release cadence.
- Permissive license (MIT) allows free redistribution, CI integration, embedding.
- Portable CLI mode enables use in automated pipelines (no X11 required).

**Negative:**
- Upfront time investment before reaching parity with Beyond Compare's polish.
- Maintenance burden of Qt/paramiko bindings across Python versions.
- No commercial support.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| Use Beyond Compare | Paid license, no Linux CLI mode, no programmable API |
| Contribute to Meld | GTK4 migration stalled; roadmap misalignment |
| VS Code extension | Tied to editor runtime, no headless mode, no archives |
| Shell script wrapper around `diff -rq` + `sha256sum` | No GUI, no merge, no session save/load |

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| Personal weekly usage | ≥ 3 real workflows (config drift, backup verify, merge) | Author log |
| Headless test coverage for core modules | ≥ 70% for `hasher`, `archive`, `merge`, `remote` parsing | `pytest --cov` |
| Feature parity with daily Beyond Compare use cases | Side-by-side diff, hash compare, archive browse, SFTP, 3-way merge | Functional checklist |
| Maintenance burden | ≤ 4 hours/month on Qt/paramiko/bindings | Time tracking |

## Trigger to Revisit

Re-evaluate "build" vs "buy/extend" if any of the following happen:

1. Maintenance burden exceeds 8 hours/month for two consecutive months.
2. Qt6 or paramiko bindings break across two consecutive Python versions and no clean upgrade path exists.
3. A comparable open-source tool (e.g., Meld revival, a well-maintained Python diff library) covers all core features under a permissive license.
4. Author stops using Synk for real work for 90+ days.

## Related Records

- Depends on business context defined in `synk-bdr-0002` (audience).
- Enabled by `synk-adr-0008` (module separation) and `synk-adr-0010` (three-way merge engine).
