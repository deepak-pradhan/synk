import os
import tempfile

import pytest

pytestmark = pytest.mark.gui


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_imports(qapp):
    from src.ui.main_window import MainWindow
    from src.core.hasher import Hasher, quick_compare
    from src.ui.file_pane import FilePane
    from src.ui.diff_dialog import DiffDialog
    from src.core.worker import CompareWorker, WorkerSignals


def test_hasher_in_app(qapp):
    from src.core.hasher import Hasher

    hasher = Hasher("xxh3_64")
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Hello, World!")
        fname = f.name
    try:
        hash_val = hasher.hash_file(fname)
        assert isinstance(hash_val, str) and len(hash_val) == 16
    finally:
        os.unlink(fname)


def test_main_window_creation(qapp):
    from src.ui.main_window import MainWindow

    window = MainWindow()
    assert window.windowTitle() == "Beyond Compare Lite"


def test_file_panes_exist(qapp):
    from src.ui.main_window import MainWindow

    window = MainWindow()
    assert window.left_pane is not None
    assert window.right_pane is not None


def test_toolbar_actions_exist(qapp):
    from src.ui.main_window import MainWindow

    window = MainWindow()
    assert hasattr(window, "action_compare")
    assert hasattr(window, "action_copy_left_to_right")
    assert hasattr(window, "action_copy_right_to_left")
    assert hasattr(window, "action_delete")
    assert hasattr(window, "action_new_folder")
    assert hasattr(window, "action_open_with")


def test_hasher_initialized(qapp):
    from src.ui.main_window import MainWindow

    window = MainWindow()
    assert window.hasher is not None


def test_threadpool_initialized(qapp):
    from src.ui.main_window import MainWindow

    window = MainWindow()
    assert window.threadpool is not None