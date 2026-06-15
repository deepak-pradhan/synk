"""
Synk 3-Way Merge Engine

Line-based three-way merge using Myers diff algorithm.
Produces a merged result with conflict markers for overlapping changes.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, NamedTuple
import difflib


class MergeOp(Enum):
    BASE = auto()      # unchanged from base
    LOCAL = auto()     # local changed, remote didn't
    REMOTE = auto()    # remote changed, local didn't
    CONFLICT = auto()  # both changed same region


@dataclass(frozen=True)
class MergeHunk:
    """A single hunk in the merged output."""
    op: MergeOp
    base_lines: tuple[str, ...]
    local_lines: tuple[str, ...]
    remote_lines: tuple[str, ...]
    merged_lines: tuple[str, ...]

    @property
    def is_conflict(self) -> bool:
        return self.op == MergeOp.CONFLICT


@dataclass
class MergeResult:
    """Result of a 3-way merge."""
    hunks: List[MergeHunk]
    conflict_count: int

    @property
    def has_conflicts(self) -> bool:
        return self.conflict_count > 0

    def to_text(self) -> str:
        """Serialize merge result to text with conflict markers."""
        lines: list[str] = []
        for hunk in self.hunks:
            if hunk.op == MergeOp.CONFLICT:
                lines.append("<<<<<<< BASE")
                lines.extend(hunk.base_lines)
                lines.append("======= LOCAL")
                lines.extend(hunk.local_lines)
                lines.append("======= REMOTE")
                lines.extend(hunk.remote_lines)
                lines.append(">>>>>>>")
            else:
                lines.extend(hunk.merged_lines)
        return "\n".join(lines)


class _Change(NamedTuple):
    """Internal change descriptor from a diff."""
    start: int   # start position in base (inclusive)
    end: int     # end position in base (exclusive); may equal start for insertions
    replacement: list[str]
    side: str    # 'local' or 'remote'


def _lines(text: str) -> list[str]:
    if not text:
        return []
    if text.endswith("\n"):
        text = text[:-1]
    return text.split("\n")


def _compute_changes(base: list[str], other: list[str], side: str) -> list[_Change]:
    """Build change descriptors from base→other diff opcodes."""
    sm = difflib.SequenceMatcher(None, base, other)
    changes: list[_Change] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        replacement = other[j1:j2] if tag in ("replace", "insert") else []
        changes.append(_Change(i1, i2, replacement, side))
    return changes


def three_way_merge(base_text: str, local_text: str, remote_text: str) -> MergeResult:
    """
    Perform a line-based 3-way merge of BASE, LOCAL, and REMOTE.

    Algorithm:
      1. Myers-diff base→local and base→remote to get change sets.
      2. Sort all changes by start position in base.
      3. Walk through base left-to-right, applying changes in order.
      4. If changes from local and remote overlap in base range → CONFLICT.
      5. If changes are disjoint → apply both independently.
    """
    base = _lines(base_text)
    local = _lines(local_text)
    remote = _lines(remote_text)

    local_changes = _compute_changes(base, local, "local")
    remote_changes = _compute_changes(base, remote, "remote")

    # Sort by start position; stable for local before remote when same start
    all_changes = sorted(local_changes + remote_changes, key=lambda c: (c.start, 0 if c.side == "local" else 1))

    hunks: List[MergeHunk] = []
    conflicts = 0
    pos = 0  # current position in base
    ci = 0   # change index

    def emit_base_lines(start: int, end: int) -> None:
        """Emit unchanged base lines [start, end)."""
        for i in range(start, end):
            hunks.append(MergeHunk(
                op=MergeOp.BASE,
                base_lines=(base[i],),
                local_lines=(base[i],),
                remote_lines=(base[i],),
                merged_lines=(base[i],),
            ))

    while ci < len(all_changes):
        change = all_changes[ci]

        # Emit unchanged base lines before this change
        if pos < change.start:
            emit_base_lines(pos, change.start)
            pos = change.start

        # Look ahead for overlapping changes at this position
        # Two changes overlap if they share any base line or if one is an insertion
        # at a position covered by the other change.
        overlapping = [change]
        region_end = change.end

        for next_change in all_changes[ci + 1:]:
            # Determine if next_change overlaps with current region
            # Overlap: next_change.start < region_end OR
            #          next_change is an insert at region_end (adjacent inserts)
            if next_change.start < region_end:
                overlapping.append(next_change)
                region_end = max(region_end, next_change.end)
            elif next_change.start == region_end and next_change.start == next_change.end:
                # Adjacent pure insertion — part of same region
                overlapping.append(next_change)
                # region_end stays same (insert doesn't consume base lines)
            else:
                break

        if len(overlapping) == 1:
            # Single change — apply it cleanly
            c = overlapping[0]
            if c.side == "local":
                hunks.append(MergeHunk(
                    op=MergeOp.LOCAL,
                    base_lines=tuple(base[c.start:c.end]),
                    local_lines=tuple(c.replacement),
                    remote_lines=tuple(base[c.start:c.end]),
                    merged_lines=tuple(c.replacement),
                ))
            else:
                hunks.append(MergeHunk(
                    op=MergeOp.REMOTE,
                    base_lines=tuple(base[c.start:c.end]),
                    local_lines=tuple(base[c.start:c.end]),
                    remote_lines=tuple(c.replacement),
                    merged_lines=tuple(c.replacement),
                ))
            pos = c.end
            ci += 1
        else:
            # Multiple overlapping changes — check sides
            sides = {c.side for c in overlapping}
            if len(sides) == 1:
                # Same side — shouldn't happen in a clean diff, but apply the first
                c = overlapping[0]
                op = MergeOp.LOCAL if c.side == "local" else MergeOp.REMOTE
                hunks.append(MergeHunk(
                    op=op,
                    base_lines=tuple(base[c.start:region_end]),
                    local_lines=tuple(c.replacement) if c.side == "local" else tuple(base[c.start:region_end]),
                    remote_lines=tuple(c.replacement) if c.side == "remote" else tuple(base[c.start:region_end]),
                    merged_lines=tuple(c.replacement),
                ))
                pos = region_end
                ci += len(overlapping)
            else:
                # Different sides overlapping → CONFLICT
                region_start = min(c.start for c in overlapping)

                # Build local and remote versions of the region
                # Start with base region, then apply each side's changes
                local_version = base[region_start:region_end].copy()
                remote_version = base[region_start:region_end].copy()

                for c in overlapping:
                    if c.start >= region_start and c.end <= region_end:
                        # Change fully inside region
                        rel_start = c.start - region_start
                        rel_end = c.end - region_start
                        if c.side == "local":
                            local_version[rel_start:rel_end] = c.replacement
                        else:
                            remote_version[rel_start:rel_end] = c.replacement
                    elif c.start == region_end and c.start == c.end:
                        # Insertion at end of region
                        if c.side == "local":
                            local_version.extend(c.replacement)
                        else:
                            remote_version.extend(c.replacement)

                hunks.append(MergeHunk(
                    op=MergeOp.CONFLICT,
                    base_lines=tuple(base[region_start:region_end]),
                    local_lines=tuple(local_version),
                    remote_lines=tuple(remote_version),
                    merged_lines=tuple(),
                ))
                conflicts += 1
                pos = region_end
                ci += len(overlapping)

    # Emit remaining base lines
    if pos < len(base):
        emit_base_lines(pos, len(base))

    return MergeResult(hunks=hunks, conflict_count=conflicts)
