---
thing_id:         "synk-bdr-0005"
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
  depends_on:     ["synk-bdr-0003", "synk-bdr-0004"]
  related_to:     []
  enables:        []
tags:             [business, distribution, pypi, packaging]
---

# BDR-0005: Distribution Channels

## Status

**Accepted** (2026-06-16).

## Context

Users need to get Synk onto their machines. Options include PyPI (pip install), GitHub Releases
(binary downloads), distro packages (apt/pacman), and container images (Docker).

## Decision

- **Primary channel:** PyPI (`synk-diff` package).
- **Secondary channel:** GitHub Releases with automatically-built wheels and source tarballs.
- **No distro-specific packaging** in initial scope.

## Rationale

### PyPI as primary
- `pip install synk-diff` works on any platform (Linux, macOS, Windows).
- `pipx install synk-diff` gives isolated installation with CLI entrypoint.
- CI pipelines already use Python; adding Synk is one `pip install` line.
- PyPI publishing is automated via GitHub Actions on release tags.

### GitHub Releases as secondary
- Useful for users who want a specific version without PyPI.
- Release notes serve as changelog.

### No distro packaging (yet)
- Packaging for APT/Pacman/Homebrew requires per-distro CI, signing keys, maintenance.
- Low demand signal — target audience (developers) is comfortable with `pipx`.

## Consequences

**Positive:**
- Single distribution mechanism covers all platforms.
- `pip install` is the lowest-friction path for developers.
- CI/CD pipeline is simple: tag → `twine upload` → done.

**Negative:**
- Requires Python 3.12+ on target system.
- Qt6 system libraries must be present.
- Not discoverable to non-Python users.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| PyInstaller single binary | Build complexity, anti-virus false positives, larger download |
| Flatpak/Snap | Heavy sandboxing overhead for filesystem tool |
| Distro-native packages (deb/rpm) | High maintenance, low demand |
| Docker image | Useful for CI but awkward for GUI use |
