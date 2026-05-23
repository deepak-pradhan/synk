from PySide6.QtCore import QRunnable, QObject, Signal, Slot
from ..core.hasher import Hasher, quick_compare
import os
import fnmatch
from pathlib import Path
from typing import Optional, Tuple, Dict, List


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """

    # Signal for updating a single item's status
    update_item = Signal(
        str, str, str, str, object
    )  # pane_id, file_name, status_text, color_hex, is_dir
    # Signal for when the worker is done
    finished = Signal()
    # Signal for progress (optional)
    progress = Signal(int, int)  # current, total


class CompareWorker(QRunnable):
    """
    Worker thread for comparing two directories (immediate children) and updating the UI.
    """

    def __init__(self, left_path: str, right_path: str, hasher: Hasher, ignore_patterns: Optional[List[str]] = None):
        super().__init__()
        self.left_path = left_path
        self.right_path = right_path
        self.hasher = hasher
        self.ignore_patterns = ignore_patterns or []
        self.show_identical = True
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

    @Slot()
    def run(self):
        """
        Compare the two directories and emit signals for each item.
        """
        try:
            # Get the list of items in each directory
            left_items = self._scan_directory(self.left_path)
            right_items = self._scan_directory(self.right_path)

            # Get the union of item names
            all_names = set(left_items.keys()) | set(right_items.keys())
            total = len(all_names)
            processed = 0

            for name in sorted(all_names):
                left_info = left_items.get(name)
                right_info = right_items.get(name)

                left_status, left_color = self._get_status_and_color(
                    left_info, right_info, is_left=True
                )
                right_status, right_color = self._get_status_and_color(
                    right_info, left_info, is_left=False
                )

                if not self.show_identical and left_status == "identical":
                    continue

                if left_info is not None:
                    is_dir = left_info["is_dir"]
                    self.signals.update_item.emit(
                        "left", name, left_status, left_color, is_dir
                    )
                if right_info is not None:
                    is_dir = right_info["is_dir"]
                    self.signals.update_item.emit(
                        "right", name, right_status, right_color, is_dir
                    )

                processed += 1
                if processed % 10 == 0:
                    self.signals.progress.emit(processed, total)

            # Emit final progress
            self.signals.progress.emit(total, total)
        except Exception as e:
            print(f"Error in worker: {e}")
        finally:
            self.signals.finished.emit()

    def _scan_directory(self, path: str) -> Dict[str, dict]:
        """
        Scan a directory and return a dict mapping item name to a dict with:
            - 'is_dir': bool
            - 'size': int (for files)
            - 'mtime': float (modification time)
        Returns empty dict if directory cannot be accessed.
        """
        items = {}
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.name.startswith(".") and entry.name not in [".", ".."]:
                        continue
                    if any(fnmatch.fnmatch(entry.name, p) for p in self.ignore_patterns):
                        continue
                    info = entry.stat()
                    items[entry.name] = {
                        "is_dir": entry.is_dir(),
                        "size": info.st_size,
                        "mtime": info.st_mtime,
                    }
        except (OSError, IOError, PermissionError):
            pass
        return items

    def _get_status_and_color(
        self, info: Optional[dict], other_info: Optional[dict], is_left: bool
    ) -> Tuple[str, str]:
        """
        Determine the status text and color (hex) for an item based on its presence and the other side's info.
        Returns (status_text, color_hex).
        """
        if info is None:
            # Item does not exist on this side
            if is_left:
                return ("left-only", "#FFB6C1")  # Light pink
            else:
                return ("right-only", "#ADD8E6")  # Light blue
        else:
            # Item exists on this side
            if other_info is None:
                # Item exists only on this side
                if is_left:
                    return ("left-only", "#FFB6C1")
                else:
                    return ("right-only", "#ADD8E6")
            else:
                # Item exists on both sides
                if info["is_dir"] and other_info["is_dir"]:
                    # Both are directories
                    return ("identical", "#90EE90")  # Light green
                elif not info["is_dir"] and not other_info["is_dir"]:
                    # Both are files
                    # Quick size check
                    if info["size"] != other_info["size"]:
                        return ("different", "#FFA07A")  # Light salmon
                    # Size is same, check hash
                    # We need to compute the hash for both files
                    left_path = (
                        os.path.join(self.left_path, info["name"])
                        if is_left
                        else os.path.join(self.right_path, info["name"])
                    )
                    right_path = (
                        os.path.join(self.left_path, other_info["name"])
                        if not is_left
                        else os.path.join(self.right_path, other_info["name"])
                    )
                    # Actually, we have the info dicts but not the full path. We need to reconstruct.
                    # Let's change the _scan_directory to also store the full path? Or we can pass the base path.
                    # We'll change the method to return the full path as well.
                    # For now, let's recompute the path.
                    # We have the base paths: self.left_path and self.right_path
                    if is_left:
                        left_file = os.path.join(self.left_path, info["name"])
                        right_file = os.path.join(self.right_path, other_info["name"])
                    else:
                        left_file = os.path.join(self.left_path, other_info["name"])
                        right_file = os.path.join(self.right_path, info["name"])
                    equal, hash1, hash2 = quick_compare(
                        left_file, right_file, self.hasher
                    )
                    if equal:
                        return ("identical", "#90EE90")
                    else:
                        return ("different", "#FFA07A")
                else:
                    # One is a file and the other is a directory
                    return ("different", "#FFA07A")  # Light salmon
