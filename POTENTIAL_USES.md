# POTENTIAL_USES.md — Beyond Compare Clone

## Business

| Use Case | Problem It Solves |
|---|---|
| **Deployment verification** | After deploying code, compare deployed files against the release artifact. Catches truncated uploads, missing files, or corrupted transfers before they become production incidents. |
| **Config drift detection** | Compare config files across dev/staging/production environments. Surfaces accidental divergence (timeouts, feature flags, secrets) that causes hard-to-debug failures. |
| **Backup integrity checks** | Verify backup archives match source directories via content hashing. Catches silent bit-rot and incomplete copies — neither `rsync` nor `cp` can prove fidelity after the fact. |
| **Server migration audit** | When migrating services between servers (SFTP), confirm the destination matches the source exactly. Avoids "it looked fine" situations that surface as 404s later. |
| **Vendor/client data handoff** | When receiving or delivering large datasets, confirm file count and content integrity. One hash mismatch can mean hours of re-transferring — this catches it in seconds. |
| **Compliance/audit trail** | Compare directory snapshots over time. Prove exactly which files changed and when, without trusting timestamps alone (which are trivially altered). |
| **Build artifact regression** | Compare build outputs between CI runs. Diff a folder of generated assets to pinpoint which commit introduced an unexpected change. |

## Personal

| Use Case | Problem It Solves |
|---|---|
| **Photo/media library sync** | Copying photos from SD card to archive drives? Verify every file landed correctly — no truncated JPEGs, no missed RAWs. A single corrupted vacation photo hurts. |
| **Pre-wipe backup validation** | Before reformatting a computer, confirm backup completeness against the original home directory. The "I think I got everything" feeling is replaced with certainty. |
| **Duplicate file cleanup** | Find true duplicates by content hash across scattered media folders, external drives, and old backups. Reclaim disk space without guessing whether files are identical. |
| **Dotfile/config migration** | Moving to a new machine? Compare old `~/.config` against the new one to catch forgotten app settings, SSH keys, or shell aliases. |
| **Document archive verification** | Verify that all tax, legal, or financial documents made it into an encrypted backup before deleting originals. One missing PDF during an audit is a problem you don't want. |
| **Game/mod troubleshooting** | Compare a modded game directory against a clean install to isolate which files a mod touched — resolves crashes and conflicts without reinstalling. |
| **Family photo sharing** | Burn a USB stick or cloud share for family? Verify they received the complete set with no missing or zero-byte files before marking it done. |
