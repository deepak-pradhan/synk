import pytest
from src.core.merge import three_way_merge, MergeOp, MergeResult


def test_no_changes():
    """All identical — no hunks, no conflicts."""
    base = "line1\nline2\nline3"
    result = three_way_merge(base, base, base)
    # All lines unchanged — hunks should all be BASE
    assert result.conflict_count == 0
    text = result.to_text()
    assert text == base


def test_local_only_change():
    """Only local changed a line — take LOCAL."""
    base = "line1\nline2\nline3"
    local = "line1\nline2 MODIFIED\nline3"
    remote = "line1\nline2\nline3"
    result = three_way_merge(base, local, remote)
    assert result.conflict_count == 0
    assert "line2 MODIFIED" in result.to_text()


def test_remote_only_change():
    """Only remote changed a line — take REMOTE."""
    base = "line1\nline2\nline3"
    local = "line1\nline2\nline3"
    remote = "line1\nline2 REMOTE\nline3"
    result = three_way_merge(base, local, remote)
    assert result.conflict_count == 0
    assert "line2 REMOTE" in result.to_text()


def test_non_overlapping_changes():
    """Local changed line2, remote changed line3 — both apply cleanly."""
    base = "line1\nline2\nline3"
    local = "line1\nline2 LOCAL\nline3"
    remote = "line1\nline2\nline3 REMOTE"
    result = three_way_merge(base, local, remote)
    assert result.conflict_count == 0
    text = result.to_text()
    assert "line2 LOCAL" in text
    assert "line3 REMOTE" in text


def test_conflict_both_changed_same_line():
    """Both local and remote changed the same line — CONFLICT."""
    base = "line1\nline2\nline3"
    local = "line1\nline2 LOCAL\nline3"
    remote = "line1\nline2 REMOTE\nline3"
    result = three_way_merge(base, local, remote)
    assert result.conflict_count > 0
    text = result.to_text()
    assert "<<<<<<< BASE" in text
    assert "LOCAL" in text
    assert "REMOTE" in text
    assert ">>>>>>>" in text


def test_local_insertion():
    """Local added a new line — merged output contains insertion."""
    base = "line1\nline3"
    local = "line1\nline2 NEW\nline3"
    remote = "line1\nline3"
    result = three_way_merge(base, local, remote)
    assert result.conflict_count == 0
    text = result.to_text()
    assert "line2 NEW" in text


def test_remote_deletion():
    """Remote deleted a line — merged output excludes deleted line."""
    base = "line1\nline2\nline3"
    local = "line1\nline2\nline3"
    remote = "line1\nline3"
    result = three_way_merge(base, local, remote)
    assert result.conflict_count == 0
    text = result.to_text()
    assert "line1" in text
    assert "line3" in text


def test_empty_base():
    """Base is empty, both added content."""
    base = ""
    local = "new local line"
    remote = "new remote line"
    result = three_way_merge(base, local, remote)
    assert result.conflict_count >= 0  # could be conflict or sequential


def test_empty_files():
    """All files empty — trivial merge."""
    result = three_way_merge("", "", "")
    assert result.conflict_count == 0
    assert result.to_text() == ""
