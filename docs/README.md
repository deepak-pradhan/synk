---
thing_id:         "synk-docs-index"
thing_type:       "technical_documentation"
domain:           "synk"
lifecycle_state:  "active"
priority:         "medium"
confidentiality:  "internal"
owner:            "Deepak"
version:          "1.0"
last_updated:     "2026-06-16"
next_review_date: "2026-09-16"
relations:
  related_to:     ["synk-bdr-0001", "synk-bdr-0002", "synk-bdr-0003", "synk-bdr-0004", "synk-bdr-0005", "synk-bdr-0006"]
tags:             [index, docs, taxonomy]
---

# Synk Docs Index

Navigable map of the Synk project's documentation. Synk is a cross-platform diff and merge
tool (Beyond Compare clone) for Linux, built with Python/PySide6.

## BDRs (`05.decision-artifacts/bdrs/`)

| Doc | `thing_id` | What |
|-----|-----------|------|
| [0001](05.decision-artifacts/bdrs/0001-build-vs-buy.md) | `synk-bdr-0001` | Build vs Buy — why build Synk |
| [0002](05.decision-artifacts/bdrs/0002-target-audience.md) | `synk-bdr-0002` | Target audience & positioning |
| [0003](05.decision-artifacts/bdrs/0003-monetization.md) | `synk-bdr-0003` | Monetization strategy |
| [0004](05.decision-artifacts/bdrs/0004-open-source.md) | `synk-bdr-0004` | Open source strategy & licensing |
| [0005](05.decision-artifacts/bdrs/0005-distribution.md) | `synk-bdr-0005` | Distribution channels |
| [0006](05.decision-artifacts/bdrs/0006-prioritization-philosophy.md) | `synk-bdr-0006` | Feature prioritization philosophy |

## MoSCoW (`05.decision-artifacts/moscows/`)

| Doc | `thing_id` | What |
|-----|-----------|------|
| [0001](05.decision-artifacts/moscows/0001-core-feature-build-sequence.md) | `synk-moscow-0001` | Core feature build sequence (v0.1–v0.2) |

## ADRs (`05.decision-artifacts/adrs/`)

| Doc | `thing_id` | What |
|-----|-----------|------|
| [0001](05.decision-artifacts/adrs/0001-python-pyside6.md) | `synk-adr-0001` | Python + PySide6 (Qt6) as UI framework |
| [0002](05.decision-artifacts/adrs/0002-xxhash.md) | `synk-adr-0002` | xxHash for fast content comparison |
| [0003](05.decision-artifacts/adrs/0003-worker-pattern.md) | `synk-adr-0003` | QRunnable + QThreadPool worker pattern |
| [0004](05.decision-artifacts/adrs/0004-toml-persistence.md) | `synk-adr-0004` | TOML for config and session persistence |
| [0005](05.decision-artifacts/adrs/0005-myers-diff.md) | `synk-adr-0005` | Myers diff algorithm via diff-match-patch |
| [0006](05.decision-artifacts/adrs/0006-archive-virtual-folder.md) | `synk-adr-0006` | Archive-as-virtual-folder pattern |
| [0007](05.decision-artifacts/adrs/0007-sftp-paramiko.md) | `synk-adr-0007` | SFTP remote via paramiko |
| [0008](05.decision-artifacts/adrs/0008-module-separation.md) | `synk-adr-0008` | Strict module separation: core / ui / utils |
| [0009](05.decision-artifacts/adrs/0009-dual-entrypoint.md) | `synk-adr-0009` | CLI + GUI dual entrypoint |
| [0010](05.decision-artifacts/adrs/0010-three-way-merge.md) | `synk-adr-0010` | 3-way merge engine — line-based Myers |
| [0011](05.decision-artifacts/adrs/0011-color-scheme.md) | `synk-adr-0011` | Color scheme — status-to-color mapping |
| [0012](05.decision-artifacts/adrs/0012-session-schema.md) | `synk-adr-0012` | Session schema design |
