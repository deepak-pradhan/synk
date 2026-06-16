# BDR-005: Distribution Channels

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Users need to get Synk onto their machines. Options include PyPI (pip install), GitHub Releases (binary downloads), distro packages (apt/pacman), and container images (Docker).

## Decision

- **Primary channel:** PyPI (`synk-diff` package)
- **Secondary channel:** GitHub Releases with automatically-built wheels and source tarballs
- **No distro-specific packaging** in initial scope

## Rationale

### PyPI as primary
- `pip install synk-diff` works on any platform (Linux, macOS, Windows) with zero distro-specific logic
- `pipx install synk-diff` gives isolated installation with a CLI entrypoint — ideal for developer workstations
- CI pipelines already use Python; adding Synk to a workflow is one `pip install` line
- PyPI publishing is automated via GitHub Actions on release tags (already implemented)

### GitHub Releases as secondary
- Useful for users who want a specific version without PyPI
- Wheels include metadata for pip-based installs, but raw tarball is available for manual inspection
- Release notes at https://github.com/deepak-pradhan/synk/releases serve as changelog

### No distro packaging (yet)
- Packaging for APT/Pacman/Homebrew requires per-distro CI, signing keys, and maintenance
- Low demand signal — developers who want Synk are comfortable with `pipx`
- Can be revisited if someone volunteers to maintain a Homebrew formula or AUR package

## Consequences

**Positive:**
- Single distribution mechanism covers all platforms and use cases
- `pip install` is the lowest-friction path for the target audience (developers)
- CI/CD pipeline is simple: tag → `twine upload` → done

**Negative:**
- Requires Python 3.12+ on the target system (most dev workstations already have it)
- Qt6 system libraries must be present (PySide6 wheels bundle the Qt libs on most platforms)
- Not discoverable to non-Python users (no apt-get, no .deb, no .exe installer)

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| PyInstaller single binary | Adds build complexity, anti-virus false positives, larger download; revisit if non-Python users become a significant segment |
| Flatpak/Snap | Heavy sandboxing overhead for a file-system tool; complicated permission model |
| Distro-native packages (deb/rpm) | High maintenance, low demand |
| Docker image | Useful for CI but awkward for GUI use; can be added as a secondary channel later |
