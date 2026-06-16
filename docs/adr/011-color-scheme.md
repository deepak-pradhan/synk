# ADR-011: Color Scheme — Status-to-Color Mapping

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

The side-by-side comparison view needs color-coded rows so the user can instantly distinguish identical, different, and one-sided files. The scheme must be accessible (colorblind-safe where possible) and consistent across tree view, status bar, and diff dialog.

## Decision

Map file status to a fixed set of colors:

| Status | Color | Hex | Meaning |
|--------|-------|-----|---------|
| Identical | Light green | `#90EE90` | Same content (hash match) |
| Different | Light salmon | `#FFA07A` | Content differs |
| Left-only | Light pink | `#FFB6C1` | Exists only on the left panel |
| Right-only | Light blue | `#ADD8E6` | Exists only on the right panel |

## Rationale

- **Green/red** is the universal convention for same/different. Salmon (soft red) prevents the "error" connotation of bright red.
- **Pink/blue** for one-sided items uses a separate axis (hue) that is distinguishable even for red-green colorblind users.
- Light pastel shades are non-distracting — the user focuses on the file names, not the background.
- The scheme matches Beyond Compare's defaults (familiarity transfer).
- Implemented via Qt item role background colors — no custom delegate needed for basic coloring.

## Consequences

**Positive:**
- Instant visual scanning — 100ms glance identifies all differences
- Familiar to Beyond Compare users
- Colors are configurable via `QStyleSheet` theming for light/dark mode

**Negative:**
- Red-green coding is not fully colorblind-safe — salmon/green works for most deuteranopia but not protanopia
- No distinction between "newer" and "older" versions — just same/different/only
- Bright themes may wash out pastel colors

## Extension (Dark Mode)

When the user switches to dark theme, colors shift to deeper/darker variants:

| Status | Dark Hex |
|--------|----------|
| Identical | `#2E7D32` |
| Different | `#C62828` |
| Left-only | `#AD1457` |
| Right-only | `#1565C0` |

## Implementation

`src/core/worker.py:119` — `_get_status_and_color()`:

```python
def _get_status_and_color(self, info, other_info, is_left):
    if info is None:
        return ("left-only", "#FFB6C1") if is_left else ("right-only", "#ADD8E6")
    ...
    elif hash matches:
        return ("identical", "#90EE90")
    else:
        return ("different", "#FFA07A")
```

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Icon-only (no color) | Slower visual parsing; no at-a-glance difference detection |
| Text labels only | Requires reading each status column — defeats the purpose of a visual diff tool |
| Traffic-light icons (green/yellow/red) | More complex to implement; yellow adds little information over green/red for binary diff status |
| Full row background + icon column | Icon column duplicates information; adds visual noise |
