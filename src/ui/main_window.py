from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QStatusBar,
    QToolBar,
    QSplitter,
    QFileDialog,
    QInputDialog,
    QMessageBox,
    QApplication,
)
from PySide6.QtCore import Qt, Slot, QThreadPool, QUrl
from PySide6.QtGui import (
    QAction,
    QIcon,
    QBrush,
    QColor,
    QStandardItem,
    QDesktopServices,
)
from src.ui.file_pane import FilePane
from src.ui.diff_dialog import DiffDialog
from src.core.worker import CompareWorker, WorkerSignals
from src.core.hasher import Hasher
from src.ui.settings_dialog import SettingsDialog
from src.utils.config import load_config, save_config
from src.utils.session import save_session, load_session, save_last_session, load_last_session, clear_last_session
import os
import shutil


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beyond Compare Lite")
        self.resize(1200, 700)
        self._config = load_config()
        algo = self._config["comparison"]["hash_algorithm"]
        self.hasher = Hasher(algo)
        self.threadpool = QThreadPool()
        self.action_compare = QAction("Compare", self)
        self.action_compare.setStatusTip("Compare the two directories")
        self.action_copy_left_to_right = QAction("Copy Left → Right", self)
        self.action_copy_left_to_right.setStatusTip(
            "Copy selected item(s) from left to right"
        )
        self.action_copy_right_to_left = QAction("Copy Right → Left", self)
        self.action_copy_right_to_left.setStatusTip(
            "Copy selected item(s) from right to left"
        )
        self.action_delete = QAction("Delete", self)
        self.action_delete.setStatusTip("Delete selected item(s)")
        self.action_new_folder = QAction("New Folder", self)
        self.action_new_folder.setStatusTip("Create new folder in current directory")
        self.action_open_with = QAction("Open With...", self)
        self.action_open_with.setStatusTip(
            "Open selected item with default application"
        )
        self.action_settings = QAction("Settings", self)
        self.action_settings.setStatusTip("Open settings dialog")
        self.action_save_session = QAction("Save Session...", self)
        self.action_save_session.setStatusTip("Save comparison session to file")
        self.action_load_session = QAction("Load Session...", self)
        self.action_load_session.setStatusTip("Load comparison session from file")
        self.setup_ui()
        self.setup_connections()
        self._try_restore_last_session()

    def setup_ui(self):
        # Menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.action_save_session)
        file_menu.addAction(self.action_load_session)
        file_menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.setStatusTip("Exit the application")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Compare action
        self.action_compare = QAction("Compare", self)
        self.action_compare.setStatusTip("Compare the two directories")
        self.action_compare.triggered.connect(self.start_comparison)
        toolbar.addAction(self.action_compare)

        # Copy actions
        toolbar.addAction(self.action_copy_left_to_right)
        toolbar.addAction(self.action_copy_right_to_left)

        # Delete action
        toolbar.addAction(self.action_delete)

        # New folder action
        toolbar.addAction(self.action_new_folder)

        # Open with action
        toolbar.addAction(self.action_open_with)

        toolbar.addSeparator()
        toolbar.addAction(self.action_settings)

        # Splitter for two panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.left_pane = FilePane("Left")
        self.right_pane = FilePane("Right")
        splitter.addWidget(self.left_pane)
        splitter.addWidget(self.right_pane)
        splitter.setSizes([600, 600])

        layout.addWidget(splitter)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label, 1)

    def setup_connections(self):
        # Connect pane signals
        self.left_pane.path_changed.connect(self.on_left_path_changed)
        self.right_pane.path_changed.connect(self.on_right_path_changed)
        self.left_pane.item_double_clicked.connect(self.on_item_double_clicked_left)
        self.right_pane.item_double_clicked.connect(self.on_item_double_clicked_right)

        # Connect context menu signals from both panes
        for pane, other_label in [(self.left_pane, "right"), (self.right_pane, "left")]:
            pane.copy_to_other_requested.connect(self._on_copy_to_other)
            pane.delete_requested.connect(self._on_delete_from_context)
            pane.rename_requested.connect(self._on_rename)
            pane.properties_requested.connect(self._on_properties)
            pane.open_requested.connect(self._on_open_file)
            pane.tree_view.files_dropped.connect(self._on_files_dropped)

        # Connect toolbar actions
        self.action_compare.triggered.connect(self.start_comparison)
        self.action_copy_left_to_right.triggered.connect(self.copy_left_to_right)
        self.action_copy_right_to_left.triggered.connect(self.copy_right_to_left)
        self.action_delete.triggered.connect(self.delete_selected)
        self.action_new_folder.triggered.connect(self.new_folder)
        self.action_open_with.triggered.connect(self.open_with)
        self.action_settings.triggered.connect(self.open_settings)
        self.action_save_session.triggered.connect(self.save_session)
        self.action_load_session.triggered.connect(self.load_session)

    @Slot(str, str)
    def on_item_double_clicked_left(self, pane_id, file_path):
        # Handle file double-click in left pane
        if pane_id == "left":
            self.status_label.setText(f"Double-clicked left: {file_path}")
            # For now, we'll just show in the status bar - we can implement diff dialog later
            # TODO: Implement diff dialog comparing with the right pane if the file exists there
            # We'll try to find the same file in the right pane
            right_path = self.right_pane.get_current_path()
            if right_path and os.path.isdir(right_path):
                # Construct the path in the right pane
                rel_path = os.path.relpath(file_path, self.left_pane.get_current_path())
                candidate = os.path.join(right_path, rel_path)
                if os.path.isfile(candidate):
                    # Show diff dialog
                    dialog = DiffDialog(file_path, candidate, self)
                    dialog.exec()
                else:
                    self.status_label.setText(
                        f"Double-clicked left: {file_path} (no corresponding file in right)"
                    )
            else:
                self.status_label.setText(f"Double-clicked left: {file_path}")

    @Slot(str, str)
    def on_item_double_clicked_right(self, pane_id, file_path):
        # Handle file double-click in right pane
        if pane_id == "right":
            self.status_label.setText(f"Double-clicked right: {file_path}")
            # For now, we'll just show in the status bar - we can implement diff dialog later
            # TODO: Implement diff dialog comparing with the left pane if the file exists there
            left_path = self.left_pane.get_current_path()
            if left_path and os.path.isdir(left_path):
                # Construct the path in the left pane
                rel_path = os.path.relpath(
                    file_path, self.right_pane.get_current_path()
                )
                candidate = os.path.join(left_path, rel_path)
                if os.path.isfile(candidate):
                    # Show diff dialog
                    dialog = DiffDialog(
                        candidate, file_path, self
                    )  # Note: order might matter for diff display
                    dialog.exec()
                else:
                    self.status_label.setText(
                        f"Double-clicked right: {file_path} (no corresponding file in left)"
                    )
            else:
                self.status_label.setText(f"Double-clicked right: {file_path}")

    @Slot()
    def on_left_path_changed(self, path):
        self.status_label.setText(f"Left path: {path}")

    @Slot()
    def on_right_path_changed(self, path):
        self.status_label.setText(f"Right path: {path}")

    @Slot()
    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self._config = dialog.get_config()
            algo = self._config["comparison"]["hash_algorithm"]
            self.hasher = Hasher(algo)
            save_config(self._config)
            self.status_label.setText("Settings saved")

    def closeEvent(self, event):
        left_path = self.left_pane.get_current_path() or ""
        right_path = self.right_pane.get_current_path() or ""
        save_last_session(left_path, right_path, self._config)
        super().closeEvent(event)

    def _try_restore_last_session(self):
        session = load_last_session()
        if not session:
            return
        if not session.get("left_path") and not session.get("right_path"):
            return
        reply = QMessageBox.question(
            self,
            "Restore Session",
            "Restore last comparison session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._apply_session(session)

    def _apply_session(self, session: dict):
        left = session.get("left_path", "")
        right = session.get("right_path", "")
        if left and os.path.exists(left):
            self.left_pane.set_path(left)
        if right and os.path.exists(right):
            self.right_pane.set_path(right)
        algo = session.get("hash_algorithm")
        if algo:
            self.hasher = Hasher(algo)
            self._config["comparison"]["hash_algorithm"] = algo
        patterns = session.get("ignore_patterns")
        if patterns is not None:
            self._config["ignore"]["patterns"] = patterns
        show = session.get("show_identical")
        if show is not None:
            self._config["ignore"]["show_identical"] = show

    @Slot()
    def save_session(self):
        left_path = self.left_pane.get_current_path() or ""
        right_path = self.right_pane.get_current_path() or ""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Session", "", "Beyond Compare Session (*.bc-session)"
        )
        if not file_path:
            return
        data = {
            "left_path": left_path,
            "right_path": right_path,
            "hash_algorithm": self._config["comparison"]["hash_algorithm"],
            "ignore_patterns": self._config["ignore"]["patterns"],
            "show_identical": self._config["ignore"]["show_identical"],
        }
        if save_session(file_path, data):
            self.status_label.setText(f"Session saved: {file_path}")
        else:
            self.status_label.setText("Error saving session")

    @Slot()
    def load_session(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Session", "", "Beyond Compare Session (*.bc-session)"
        )
        if not file_path:
            return
        session = load_session(file_path)
        if session is None:
            self.status_label.setText("Error loading session")
            return
        self._apply_session(session)
        self.status_label.setText(f"Session loaded: {file_path}")

    @Slot()
    def start_comparison(self):
        left_path = self.left_pane.get_current_path()
        right_path = self.right_pane.get_current_path()

        if not left_path or not right_path:
            self.status_label.setText("Please set both paths")
            return

        if not os.path.isdir(left_path) or not os.path.isdir(right_path):
            self.status_label.setText("Both paths must be directories")
            return

        self.status_label.setText("Comparing...")
        ignore_patterns = self._config["ignore"]["patterns"]
        show_identical = self._config["ignore"]["show_identical"]
        worker = CompareWorker(left_path, right_path, self.hasher, ignore_patterns)
        worker.show_identical = show_identical
        worker.signals.update_item.connect(self.update_item_status)
        worker.signals.finished.connect(self.comparison_finished)
        worker.signals.progress.connect(self.update_progress)
        self.threadpool.start(worker)

    @Slot()
    def copy_left_to_right(self):
        """Copy selected items from left pane to right pane"""
        left_path = self.left_pane.get_current_path()
        right_path = self.right_pane.get_current_path()

        if not left_path or not right_path:
            self.status_label.setText("Please set both paths")
            return

        if not os.path.isdir(left_path) or not os.path.isdir(right_path):
            self.status_label.setText("Both paths must be directories")
            return

        # Get selected items from left pane
        selection_model = self.left_pane.tree_view.selectionModel()
        selected_indexes = selection_model.selectedRows(0)  # Column 0 (name)

        if not selected_indexes:
            self.status_label.setText("No items selected")
            return

        copied_count = 0
        for index in selected_indexes:
            item = self.left_pane.model.itemFromIndex(index)
            if item:
                file_info = item.data(Qt.ItemDataRole.UserRole)
                if file_info:
                    source_path = file_info.absoluteFilePath()
                    file_name = file_info.fileName()
                    dest_path = os.path.join(right_path, file_name)

                    try:
                        if file_info.isDir():
                            if os.path.exists(dest_path):
                                reply = QInputDialog.getText(
                                    self,
                                    "Directory Exists",
                                    f"The directory '{file_name}' already exists in the destination.\nEnter a new name or press OK to replace:",
                                    text=file_name,
                                )
                                if not reply[1]:  # User cancelled
                                    continue
                                if reply[0]:  # User provided a new name
                                    dest_path = os.path.join(right_path, reply[0])
                                # If they kept the same name, we'll replace
                            shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                        else:
                            if os.path.exists(dest_path):
                                reply = QInputDialog.getText(
                                    self,
                                    "File Exists",
                                    f"The file '{file_name}' already exists in the destination.\nEnter a new name or press OK to replace:",
                                    text=file_name,
                                )
                                if not reply[1]:  # User cancelled
                                    continue
                                if reply[0]:  # User provided a new name
                                    dest_path = os.path.join(right_path, reply[0])
                                # If they kept the same name, we'll replace
                            shutil.copy2(source_path, dest_path)
                        copied_count += 1
                    except Exception as e:
                        self.status_label.setText(
                            f"Error copying {file_name}: {str(e)}"
                        )

        self.status_label.setText(f"Copied {copied_count} item(s) from left to right")
        # Refresh both panes to show the changes
        self.left_pane.populate_tree(left_path)
        self.right_pane.populate_tree(right_path)

    @Slot()
    def copy_right_to_left(self):
        """Copy selected items from right pane to left pane"""
        left_path = self.left_pane.get_current_path()
        right_path = self.right_pane.get_current_path()

        if not left_path or not right_path:
            self.status_label.setText("Please set both paths")
            return

        if not os.path.isdir(left_path) or not os.path.isdir(right_path):
            self.status_label.setText("Both paths must be directories")
            return

        # Get selected items from right pane
        selection_model = self.right_pane.tree_view.selectionModel()
        selected_indexes = selection_model.selectedRows(0)  # Column 0 (name)

        if not selected_indexes:
            self.status_label.setText("No items selected")
            return

        copied_count = 0
        for index in selected_indexes:
            item = self.right_pane.model.itemFromIndex(index)
            if item:
                file_info = item.data(Qt.ItemDataRole.UserRole)
                if file_info:
                    source_path = file_info.absoluteFilePath()
                    file_name = file_info.fileName()
                    dest_path = os.path.join(left_path, file_name)

                    try:
                        if file_info.isDir():
                            if os.path.exists(dest_path):
                                reply = QInputDialog.getText(
                                    self,
                                    "Directory Exists",
                                    f"The directory '{file_name}' already exists in the destination.\nEnter a new name or press OK to replace:",
                                    text=file_name,
                                )
                                if not reply[1]:  # User cancelled
                                    continue
                                if reply[0]:  # User provided a new name
                                    dest_path = os.path.join(left_path, reply[0])
                                # If they kept the same name, we'll replace
                            shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                        else:
                            if os.path.exists(dest_path):
                                reply = QInputDialog.getText(
                                    self,
                                    "File Exists",
                                    f"The file '{file_name}' already exists in the destination.\nEnter a new name or press OK to replace:",
                                    text=file_name,
                                )
                                if not reply[1]:  # User cancelled
                                    continue
                                if reply[0]:  # User provided a new name
                                    dest_path = os.path.join(left_path, reply[0])
                                # If they kept the same name, we'll replace
                            shutil.copy2(source_path, dest_path)
                        copied_count += 1
                    except Exception as e:
                        self.status_label.setText(
                            f"Error copying {file_name}: {str(e)}"
                        )

        self.status_label.setText(f"Copied {copied_count} item(s) from right to left")
        # Refresh both panes to show the changes
        self.left_pane.populate_tree(left_path)
        self.right_pane.populate_tree(right_path)

    @Slot()
    def delete_selected(self):
        """Delete selected items from both panes"""
        left_path = self.left_pane.get_current_path()
        right_path = self.right_pane.get_current_path()

        total_deleted = 0

        # Delete from left pane
        if left_path and os.path.isdir(left_path):
            selection_model = self.left_pane.tree_view.selectionModel()
            selected_indexes = selection_model.selectedRows(0)  # Column 0 (name)

            if selected_indexes:
                reply = QInputDialog.getText(
                    self,
                    "Confirm Delete",
                    f"Are you sure you want to delete {len(selected_indexes)} item(s) from the left pane?\nType 'DELETE' to confirm:",
                    text="",
                )
                if reply[1] and reply[0] == "DELETE":
                    deleted_count = 0
                    for index in selected_indexes:
                        item = self.left_pane.model.itemFromIndex(index)
                        if item:
                            file_info = item.data(Qt.ItemDataRole.UserRole)
                            if file_info:
                                file_path = file_info.absoluteFilePath()
                                try:
                                    if file_info.isDir():
                                        shutil.rmtree(file_path)
                                    else:
                                        os.remove(file_path)
                                    deleted_count += 1
                                except Exception as e:
                                    self.status_label.setText(
                                        f"Error deleting {file_info.fileName()}: {str(e)}"
                                    )
                    self.status_label.setText(
                        f"Deleted {deleted_count} item(s) from left pane"
                    )
                    total_deleted += deleted_count

        # Delete from right pane
        if right_path and os.path.isdir(right_path):
            selection_model = self.right_pane.tree_view.selectionModel()
            selected_indexes = selection_model.selectedRows(0)  # Column 0 (name)

            if selected_indexes:
                reply = QInputDialog.getText(
                    self,
                    "Confirm Delete",
                    f"Are you sure you want to delete {len(selected_indexes)} item(s) from the right pane?\nType 'DELETE' to confirm:",
                    text="",
                )
                if reply[1] and reply[0] == "DELETE":
                    deleted_count = 0
                    for index in selected_indexes:
                        item = self.right_pane.model.itemFromIndex(index)
                        if item:
                            file_info = item.data(Qt.ItemDataRole.UserRole)
                            if file_info:
                                file_path = file_info.absoluteFilePath()
                                try:
                                    if file_info.isDir():
                                        shutil.rmtree(file_path)
                                    else:
                                        os.remove(file_path)
                                    deleted_count += 1
                                except Exception as e:
                                    self.status_label.setText(
                                        f"Error deleting {file_info.fileName()}: {str(e)}"
                                    )
                    current_status = self.status_label.text()
                    self.status_label.setText(
                        f"{current_status} | Deleted {deleted_count} item(s) from right pane"
                    )
                    total_deleted += deleted_count

        if total_deleted > 0:
            # Refresh both panes
            if left_path and os.path.isdir(left_path):
                self.left_pane.populate_tree(left_path)
            if right_path and os.path.isdir(right_path):
                self.right_pane.populate_tree(right_path)
        elif total_deleted == 0 and (left_path or right_path):
            self.status_label.setText("No items deleted")

    @Slot()
    def new_folder(self):
        """Create a new folder in the current directory of the focused pane"""
        # Determine which pane has focus
        left_has_focus = self.left_pane.hasFocus()
        right_has_focus = self.right_pane.hasFocus()

        if left_has_focus:
            current_path = self.left_pane.get_current_path()
            pane = self.left_pane
        elif right_has_focus:
            current_path = self.right_pane.get_current_path()
            pane = self.right_pane
        else:
            # Default to left pane if neither has focus
            current_path = self.left_pane.get_current_path()
            pane = self.left_pane
            if not current_path or not os.path.isdir(current_path):
                current_path = self.right_pane.get_current_path()
                pane = self.right_pane

        if not current_path or not os.path.isdir(current_path):
            self.status_label.setText("Please select a valid directory first")
            return

        folder_name, ok = QInputDialog.getText(
            self, "New Folder", "Enter folder name:", text="New Folder"
        )

        if ok and folder_name:
            folder_name = folder_name.strip()
            if folder_name:
                new_folder_path = os.path.join(current_path, folder_name)
                try:
                    os.mkdir(new_folder_path)
                    self.status_label.setText(f"Created folder: {folder_name}")
                    # Refresh the pane
                    pane.populate_tree(current_path)
                except Exception as e:
                    self.status_label.setText(f"Error creating folder: {str(e)}")
            else:
                self.status_label.setText("Folder name cannot be empty")
        else:
            self.status_label.setText("Folder creation cancelled")

    @Slot()
    def open_with(self):
        """Open selected item with default application"""
        # Determine which pane has focus
        left_has_focus = self.left_pane.hasFocus()
        right_has_focus = self.right_pane.hasFocus()

        if left_has_focus:
            pane = self.left_pane
        elif right_has_focus:
            pane = self.right_pane
        else:
            # Default to left pane if neither has focus
            pane = self.left_pane
            if not pane.get_current_path():
                pane = self.right_pane

        selection_model = pane.tree_view.selectionModel()
        selected_indexes = selection_model.selectedRows(0)  # Column 0 (name)

        if not selected_indexes:
            self.status_label.setText("No item selected")
            return

        # Open the first selected item
        index = selected_indexes[0]
        item = pane.model.itemFromIndex(index)
        if item:
            file_info = item.data(Qt.ItemDataRole.UserRole)
            if file_info:
                file_path = file_info.absoluteFilePath()
                try:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
                    self.status_label.setText(f"Opened: {file_info.fileName()}")
                except Exception as e:
                    self.status_label.setText(f"Error opening file: {str(e)}")

    @Slot(list)
    def _on_copy_to_other(self, paths):
        pane = self.sender()
        if pane == self.left_pane:
            other_path = self.right_pane.get_current_path()
            direction = "left to right"
        else:
            other_path = self.left_pane.get_current_path()
            direction = "right to left"

        if not other_path or not os.path.isdir(other_path):
            self.status_label.setText("Other pane has no valid directory")
            return

        copied = 0
        for src in paths:
            name = os.path.basename(src)
            dst = os.path.join(other_path, name)
            try:
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
                copied += 1
            except Exception as e:
                self.status_label.setText(f"Error copying {name}: {e}")
                return

        self.status_label.setText(f"Copied {copied} item(s) {direction}")
        self.left_pane.populate_tree(self.left_pane.get_current_path())
        self.right_pane.populate_tree(self.right_pane.get_current_path())

    @Slot(list)
    def _on_delete_from_context(self, paths):
        deleted = 0
        for p in paths:
            try:
                if os.path.isdir(p):
                    shutil.rmtree(p)
                else:
                    os.remove(p)
                deleted += 1
            except Exception as e:
                self.status_label.setText(f"Error deleting {os.path.basename(p)}: {e}")
                return

        self.status_label.setText(f"Deleted {deleted} item(s)")
        left = self.left_pane.get_current_path()
        right = self.right_pane.get_current_path()
        if left and os.path.isdir(left):
            self.left_pane.populate_tree(left)
        if right and os.path.isdir(right):
            self.right_pane.populate_tree(right)

    @Slot(str, str)
    def _on_rename(self, old_path, old_name):
        parent = os.path.dirname(old_path)
        new_name, ok = QInputDialog.getText(
            self, "Rename", "New name:", text=old_name
        )
        if not ok or not new_name or new_name == old_name:
            return
        new_path = os.path.join(parent, new_name)
        try:
            os.rename(old_path, new_path)
            self.status_label.setText(f"Renamed to {new_name}")
            left = self.left_pane.get_current_path()
            right = self.right_pane.get_current_path()
            if left and os.path.isdir(left):
                self.left_pane.populate_tree(left)
            if right and os.path.isdir(right):
                self.right_pane.populate_tree(right)
        except Exception as e:
            self.status_label.setText(f"Error renaming: {e}")

    @Slot(str)
    def _on_properties(self, path):
        try:
            stat = os.stat(path)
            is_dir = os.path.isdir(path)
            size_str = f"{stat.st_size:,} bytes" if not is_dir else "<DIR>"
            import time
            modified = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
            created = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_ctime))
            info = (
                f"Path: {path}\n"
                f"Type: {'Directory' if is_dir else 'File'}\n"
                f"Size: {size_str}\n"
                f"Modified: {modified}\n"
                f"Created: {created}"
            )
        except OSError as e:
            info = f"Path: {path}\nError: {e}"
        QMessageBox.information(self, "Properties", info)

    @Slot(str)
    def _on_open_file(self, path):
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
            self.status_label.setText(f"Opened: {os.path.basename(path)}")
        except Exception as e:
            self.status_label.setText(f"Error opening: {e}")

    @Slot(list)
    def _on_files_dropped(self, paths):
        dest_pane = self.sender().pane
        dest_dir = dest_pane.get_current_path()
        if not dest_dir or not os.path.isdir(dest_dir):
            self.status_label.setText("Drop target has no valid directory")
            return
        copied = 0
        for src in paths:
            name = os.path.basename(src)
            dst = os.path.join(dest_dir, name)
            try:
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
                copied += 1
            except Exception as e:
                self.status_label.setText(f"Error dropping {name}: {e}")
                return
        self.status_label.setText(f"Dropped {copied} item(s)")
        self.left_pane.populate_tree(self.left_pane.get_current_path())
        self.right_pane.populate_tree(self.right_pane.get_current_path())

    @Slot(str, str, str, str, object)
    def update_item_status(self, pane_id, file_name, status_text, color_hex, is_dir):
        # Find the item in the appropriate pane's model and update its status column
        pane = self.left_pane if pane_id == "left" else self.right_pane
        model = pane.model

        # We need to find the row by the file name in the first column
        for row in range(model.rowCount()):
            item = model.item(row, 0)  # Name column
            if item and item.text() == file_name:
                # Update the status column (column 3)
                status_item = QStandardItem(status_text)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if color_hex:
                    status_item.setBackground(QBrush(QColor(color_hex)))
                model.setItem(row, 3, status_item)
                break

    @Slot()
    def comparison_finished(self):
        self.status_label.setText("Comparison complete")

    @Slot(int, int)
    def update_progress(self, current, total):
        if total > 0:
            percent = int((current / total) * 100)
            self.status_label.setText(f"Comparing... {percent}% ({current}/{total})")
        else:
            self.status_label.setText("Comparing...")
