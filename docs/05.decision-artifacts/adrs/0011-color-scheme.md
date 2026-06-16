---
thing_id:        "synk-adr-0011"
thing_type:      "adr"
adr_id:          "0011"
domain:          "synk"
phase:           "p0-foundations"
version:         "1.0"
lifecycle_state: "approved"
deciders:        "Deepak"
reversibility:   "high"
decision_date:   "2026-06-14"
last_updated:    "2026-06-16"
next_review_date: "2026-09-16"
priority:        "low"
confidentiality: "internal"
tags:            [ui, color, accessibility, theming]
relations:
  depends_on:    ["synk-adr-0001"]
  related_to:    []
  enables:       []
---

# ADR-0011: Color Scheme — Status-to-Color Mapping

## Status

**Accepted** (2026-06-14). Implemented in v0.1 M2.

## Context

The side-by-side comparison view needs color-coded rows so the user can instantly distinguish
identical, different, and one-sided files. The scheme must be accessible and consistent across
tree view, status bar, and diff dialog.

## Decision

Map file status to a fixed set of pastel colors:

| Status | Color | Hex | Meaning |
|--------|-------|-----|---------|
| Identical | Light green | `#90EE90` | Same content (hash match) |
| Different | Light salmon | `#FFA07A` | Content differs |
| Left-only | Light pink | `#FFB6C1` | Exists only on left panel |
| Right-only | Light blue | `#ADD8E6` | Exists only on right panel |

## Rationale

- Green/red is the universal convention for same/different. Salmon (soft red) avoids "error"
  connotation of bright red.
- Pink/blue for one-sided items uses a separate hue axis — distinguishable even for red-green
  colorblind users.
- Light pastel shades are non-distracting — user focuses on file names, not background.
- Matches Beyond Compare's defaults (familiarity transfer).

## Consequences

**Positive:**
- Instant visual scanning — 100ms glance identifies all differences.
- Familiar to Beyond Compare users.
- Colors are configurable via `QStyleSheet` theming for light/dark mode.

**Negative:**
- Red-green coding is not fully colorblind-safe (works for most deuteranopia, not protanopia).
- No distinction between "newer" and "older" versions.
- Bright themes may wash out pastel colors.

## Implementation

`src/core/worker.py:119` — `_get_status_and_color()` returns status text + hex color per file.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| Icon-only (no color) | Slower visual parsing |
| Text labels only | Requires reading each status column |
| Traffic-light icons | More complex; yellow adds little information for binary diff status |
