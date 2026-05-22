import sys
import os
import tempfile

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer


def test_app_creation():
    """Test that the application can be created without errors."""
    app = QApplication(sys.argv)

    # Test imports
    from src.ui.main_window import MainWindow
    from src.core.hasher import Hasher, quick_compare
    from src.ui.file_pane import FilePane
    from src.ui.diff_dialog import DiffDialog
    from src.core.worker import CompareWorker, WorkerSignals

    print("✓ All imports successful")

    # Test hasher
    hasher = Hasher("xxh3_64")
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Hello, World!")
        fname = f.name

    hash_val = hasher.hash_file(fname)
    assert isinstance(hash_val, str) and len(hash_val) == 16
    print(f"✓ Hasher working: {hash_val}")

    os.unlink(fname)

    # Test MainWindow creation
    window = MainWindow()
    assert window.windowTitle() == "Beyond Compare Lite"
    print("✓ MainWindow created successfully")

    # Test FilePane creation
    left_pane = window.left_pane
    right_pane = window.right_pane
    assert left_pane is not None
    assert right_pane is not None
    print("✓ FilePanes created successfully")

    # Test that toolbar actions exist
    assert hasattr(window, "action_compare")
    assert hasattr(window, "action_copy_left_to_right")
    assert hasattr(window, "action_copy_right_to_left")
    assert hasattr(window, "action_delete")
    assert hasattr(window, "action_new_folder")
    assert hasattr(window, "action_open_with")
    print("✓ Toolbar actions exist")

    # Test that the hasher is initialized
    assert window.hasher is not None
    print("✓ Hasher initialized in MainWindow")

    # Test that the threadpool is initialized
    assert window.threadpool is not None
    print("✓ Threadpool initialized")

    print("\n✅ All tests passed! The prototype is ready.")
    print("\nTo run the GUI application:")
    print("  cd /data/projects/3it.services.beyondcompare")
    print("  source .venv/bin/activate")
    print("  python -m src.main")
    print("\nNote: You'll need X11/Wayland display support to see the GUI.")

    # Clean exit
    QTimer.singleShot(100, app.quit)
    sys.exit(app.exec())


if __name__ == "__main__":
    test_app_creation()
