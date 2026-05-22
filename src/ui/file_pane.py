from PySide6.QtWidgets import (
    QTreeView,
    QHeaderView,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
)
from PySide6.QtCore import Qt, Signal, Slot, QDir, QFileInfo, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
import os
from pathlib import Path


class FilePane(QWidget):
    """A pane showing filesystem contents with path input controls."""

    # Signals
    path_changed = Signal(str)  # Emitted when the path is changed
    item_double_clicked = Signal(
        str, object
    )  # Emitted when an item is double-clicked: (pane_id, index)

    def __init__(self, title="Pane"):
        super().__init__()
        self.title = title
        self.current_path = ""
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Path input controls
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Enter path or browse...")
        self.browse_btn = QPushButton("Browse...")

        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)

        # Tree view
        self.tree_view = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Size", "Modified", "Status"])
        self.tree_view.setModel(self.model)
        # Fix for Qt6 enum access - use QHeaderView.ResizeMode
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree_view.header().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.tree_view.header().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.tree_view.header().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSortingEnabled(True)

        # TODO: Implement drag and drop between panes
        # For now, we rely on toolbar actions for copy/move

        # Connect signals
        self.path_edit.returnPressed.connect(self._on_path_entered)
        self.browse_btn.clicked.connect(self._on_browse_clicked)
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)

        # Add to layout
        layout.addLayout(path_layout)
        layout.addWidget(self.tree_view)

    def _on_path_entered(self):
        path = self.path_edit.text().strip()
        if path and os.path.exists(path):
            self.set_path(path)
        else:
            self.path_edit.setStyleSheet("border: 1px solid red;")

    def _on_browse_clicked(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec():
            selected_files = dialog.selectedFiles()
            if selected_files:
                self.set_path(selected_files[0])

    def _on_item_double_clicked(self, index):
        # Get the item from the model (column 0, UserRole) which is a QFileInfo
        item = self.model.itemFromIndex(index.siblingAtColumn(0))
        if item:
            file_info = item.data(Qt.ItemDataRole.UserRole)
            if file_info and file_info.isDir():
                # If it's a directory, navigate into it
                self.set_path(file_info.absoluteFilePath())
            elif file_info and not file_info.isDir():
                # If it's a file, emit the signal for the main window to handle
                self.item_double_clicked.emit(
                    "left" if self.title == "Left" else "right", file_info
                )

    def set_path(self, path):
        """Set the current path and populate the tree view."""
        if not os.path.exists(path):
            return

        self.current_path = path
        self.path_edit.setText(path)
        self.path_edit.setStyleSheet("")  # Clear error styling
        self.populate_tree(path)
        self.path_changed.emit(path)

    def populate_tree(self, path):
        """Populate the tree view with contents of the given path."""
        self.model.removeRows(0, self.model.rowCount())

        if not os.path.isdir(path):
            # Show single file
            self._add_file_to_model(path)
            return

        try:
            # Add parent directory entry (..) if not at root
            parent_dir = os.path.dirname(path)
            if path != parent_dir:  # Not root
                parent_item = QStandardItem("..")
                parent_item.setData(QFileInfo(parent_dir), Qt.ItemDataRole.UserRole)
                parent_item.setEditable(False)
                # Create empty items for other columns
                size_item = QStandardItem("<DIR>")
                size_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                modified_item = QStandardItem("")
                modified_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                status_item = QStandardItem("")
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.model.appendRow(
                    [parent_item, size_item, modified_item, status_item]
                )

            # Collect directories and files
            dirs = []
            files = []

            with os.scandir(path) as it:
                for entry in it:
                    if entry.name.startswith(".") and entry.name not in [".", ".."]:
                        continue  # Skip hidden files by default

                    if entry.is_dir():
                        dirs.append(entry)
                    else:
                        files.append(entry)

            # Sort directories and files by name (case-insensitive)
            dirs.sort(key=lambda e: e.name.lower())
            files.sort(key=lambda e: e.name.lower())

            # Add directories
            for entry in dirs:
                self._add_file_to_model(entry.path)

            # Add files
            for entry in files:
                self._add_file_to_model(entry.path)

        except PermissionError:
            # Show error in tree
            error_item = QStandardItem("Access Denied")
            error_item.setData(QFileInfo(path), Qt.ItemDataRole.UserRole)
            size_item = QStandardItem("")
            size_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            modified_item = QStandardItem("")
            modified_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            status_item = QStandardItem("ERROR")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.model.appendRow([error_item, size_item, modified_item, status_item])

    def _add_file_to_model(self, file_path):
        """Add a single file or directory to the model."""
        file_info = QFileInfo(file_path)
        name = file_info.fileName()

        # Determine if it's a directory
        is_dir = file_info.isDir()

        # Create items for each column
        name_item = QStandardItem(name)
        name_item.setData(file_info, Qt.ItemDataRole.UserRole)
        name_item.setEditable(False)

        if is_dir:
            size_item = QStandardItem("<DIR>")
        else:
            size_item = QStandardItem(str(file_info.size()))
        size_item.setTextAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        modified_time = file_info.lastModified().toString("yyyy-MM-dd hh:mm")
        modified_item = QStandardItem(modified_time)
        modified_item.setTextAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        status_item = QStandardItem("unknown")
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the row to the model
        self.model.appendRow([name_item, size_item, modified_item, status_item])

    def set_item_status(self, index, status_text, color=None):
        """Set the status and background color for an item in the status column."""
        if index.isValid():
            # Set the text in the status column (column 3)
            status_item = QStandardItem(status_text)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if color:
                status_item.setBackground(QBrush(QColor(color)))
            # Replace the item in the model
            self.model.setItem(index.row(), 3, status_item)

    def get_current_path(self):
        """Get the current path being displayed."""
        return self.current_path

    def clear(self):
        """Clear the tree view."""
        self.model.removeRows(0, self.model.rowCount())
        self.path_edit.clear()
        self.current_path = ""
