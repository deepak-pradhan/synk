"""Tests for the directory-comparison engine (CompareWorker).

Regression coverage for the bug where `_scan_directory` omitted the "name" key
while `_get_status_and_color` read `info["name"]` on the equal-size hash path —
raising KeyError 'name', which `run()` swallowed, leaving every row "unknown".

Uses QCoreApplication (headless) for the signal machinery, so it runs under the
non-gui CI selection. `run()` is invoked directly (synchronous), so no thread
pool / event loop is involved.
"""
import sys

import pytest

from src.core.hasher import Hasher
from src.core.worker import CompareWorker


@pytest.fixture(scope="module")
def qcore():
    from PySide6.QtCore import QCoreApplication

    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    yield app


def _make_tree(tmp_path):
    left = tmp_path / "left"
    right = tmp_path / "right"
    (left / "sub").mkdir(parents=True)
    (right / "sub").mkdir(parents=True)

    # identical (same size + content) -> exercises the hash-compare path
    (left / "same.txt").write_text("hello world\n")
    (right / "same.txt").write_text("hello world\n")

    # same size, different content -> hash path must return "different"
    (left / "samesize.txt").write_text("AAAA\n")
    (right / "samesize.txt").write_text("BBBB\n")

    # different size -> caught by the quick size check
    (left / "changed.txt").write_text("version = A\n")
    (right / "changed.txt").write_text("version = BBBBBB\n")

    # one-sided files
    (left / "only_left.txt").write_text("L\n")
    (right / "only_right.txt").write_text("R\n")

    # identical subdirectory
    (left / "sub" / "a.txt").write_text("shared\n")
    (right / "sub" / "a.txt").write_text("shared\n")

    return str(left), str(right)


def _run(left, right):
    worker = CompareWorker(left, right, Hasher())
    events = []
    worker.signals.update_item.connect(
        lambda pane, name, status, color, is_dir: events.append((pane, name, status))
    )
    worker.run()  # synchronous; no QThreadPool
    return events


def test_compare_assigns_real_statuses(qcore, tmp_path):
    by = {(pane, name): status for pane, name, status in _run(*_make_tree(tmp_path))}

    # the regression: these used to be absent (worker aborted) / "unknown"
    assert by[("left", "same.txt")] == "identical"
    assert by[("right", "same.txt")] == "identical"
    assert by[("left", "samesize.txt")] == "different"
    assert by[("right", "samesize.txt")] == "different"
    assert by[("left", "changed.txt")] == "different"
    assert by[("right", "changed.txt")] == "different"
    assert by[("left", "sub")] == "identical"

    # one-sided items are emitted only for the side they exist on
    assert by[("left", "only_left.txt")] == "left-only"
    assert by[("right", "only_right.txt")] == "right-only"
    assert ("right", "only_left.txt") not in by
    assert ("left", "only_right.txt") not in by


def test_no_unknown_status(qcore, tmp_path):
    """Every present item gets a status emitted; nothing is silently dropped."""
    events = _run(*_make_tree(tmp_path))
    assert events, "worker emitted nothing (it aborted before the fix)"
    assert all(status and status != "unknown" for _, _, status in events)
