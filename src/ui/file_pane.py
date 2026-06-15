from PySide6.QtWidgets import (
    QTreeView,
    QHeaderView,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
    QMenu,
)
from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
    QDir,
    QFileInfo,
    QModelIndex,
    QMimeData,
    QByteArray,
)
from PySide6.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QBrush,
    QColor,
    QDrag,
)
import os
from pathlib import Path
from src.core.archive import is_archive, list_archive_at_depth, extract_file
from src.core.remote import SFTPConnection, SFTPCredentials, parse_sftp_url, get_remote_path

MIME_TYPE = "application/x-beyondcomp-filepaths"
ARCHIVE_PREFIX = "archive:"


class DropTreeView(QTreeView):
    """QTreeView subclass that supports drag-out and drop-in of file paths."""

    files_dropped = Signal(list)

    def __init__(self, pane, parent=None):
        super().__init__(parent)
        self.pane = pane
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QTreeView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.setDropIndicatorShown(True)

    def startDrag(self, supportedActions):
        selected = self.selectionModel().selectedRows(0)
        if not selected:
            return
        paths = []
        for idx in selected:
            item = self.model().itemFromIndex(idx)
            if item:
                fi = item.data(Qt.ItemDataRole.UserRole)
                if fi:
                    paths.append(fi.absoluteFilePath())
        if not paths:
            return
        mime = QMimeData()
        mime.setData(MIME_TYPE, QByteArray("\n".join(paths).encode("utf-8")))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.CopyAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasFormat(MIME_TYPE):
            data = event.mimeData().data(MIME_TYPE).data().decode("utf-8")
            paths = [p for p in data.split("\n") if p]
            self.files_dropped.emit(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class FilePane(QWidget):
    """A pane showing filesystem contents with path input controls."""

    path_changed = Signal(str)
    item_double_clicked = Signal(str, object)
    copy_to_other_requested = Signal(list)
    delete_requested = Signal(list)
    rename_requested = Signal(str, str)
    properties_requested = Signal(str)
    open_requested = Signal(str)

    def __init__(self, title="Pane"):
        super().__init__()
        self.title = title
        self.current_path = ""
        self._archive_path = None
        self._archive_prefix = ""
        self._sftp_conn: SFTPConnection | None = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Enter path or sftp://user@host/path...")
        self.browse_btn = QPushButton("Browse...")
        self.sftp_btn = QPushButton("Connect SFTP...")

        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)
        path_layout.addWidget(self.sftp_btn)

        self.tree_view = DropTreeView(self)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Size", "Modified", "Status"])
        self.tree_view.setModel(self.model)
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
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.path_edit.returnPressed.connect(self._on_path_entered)
        self.browse_btn.clicked.connect(self._on_browse_clicked)
        self.sftp_btn.clicked.connect(self._on_sftp_clicked)
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        self.tree_view.customContextMenuRequested.connect(self._on_context_menu)

        layout.addLayout(path_layout)
        layout.addWidget(self.tree_view)

    def _on_path_entered(self):
        path = self.path_edit.text().strip()
        if not path:
            return
        if path.startswith(SFTP_PREFIX):
            from src.ui.sftp_connect_dialog import SFTPConnectDialog
            creds = parse_sftp_url(path)
            remote_path = get_remote_path(path)
            conn = SFTPConnection(creds)
            error = conn.connect()
            if error:
                self.path_edit.setStyleSheet("border: 1px solid red;")
                return
            self._sftp_conn = conn
            display = f"sftp://{creds.username}@{creds.host}:{creds.port}{remote_path}"
            self.current_path = display
            self.path_edit.setText(display)
            self.path_edit.setStyleSheet("")
            self._populate_remote(remote_path)
            self.path_changed.emit(display)
        elif path and os.path.exists(path):
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

    def _on_sftp_clicked(self):
        from src.ui.sftp_connect_dialog import SFTPConnectDialog
        dialog = SFTPConnectDialog(self)
        if dialog.exec():
            creds = dialog.get_credentials()
            remote_path = dialog.get_remote_path()
            conn = SFTPConnection(creds)
            error = conn.connect()
            if error:
                self.path_edit.setStyleSheet("border: 1px solid red;")
                return
            self._sftp_conn = conn
            display = f"sftp://{creds.username}@{creds.host}:{creds.port}{remote_path}"
            self.current_path = display
            self.path_edit.setText(display)
            self.path_edit.setStyleSheet("")
            self._populate_remote(remote_path)
            self.path_changed.emit(display)

    def _populate_remote(self, remote_path: str):
        """Populate tree view with remote SFTP directory contents."""
        if not self._sftp_conn or not self._sftp_conn.connected:
            return
        self.model.removeRows(0, self.model.rowCount())
        entries = self._sftp_conn.list_dir(remote_path)
        if not entries:
            empty_item = QStandardItem("(empty or unreadable directory)")
            empty_item.setEditable(False)
            self.model.appendRow([empty_item, QStandardItem(""), QStandardItem(""), QStandardItem("")])
            return

        if remote_path != "/":
            parent = remote_path.rsplit("/", 1)[0] or "/"
            parent_item = QStandardItem("..")
            parent_item.setData(None, Qt.ItemDataRole.UserRole)
            parent_item.setData(f"sftp_parent:{parent}", Qt.ItemDataRole.UserRole + 1)
            parent_item.setEditable(False)
            dir_size = QStandardItem("<DIR>")
            dir_size.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.model.appendRow([parent_item, dir_size, QStandardItem(""), QStandardItem("")])

        dirs = [e for e in entries if e.is_dir]
        files = [e for e in entries if not e.is_dir]
        dirs.sort(key=lambda e: e.name.lower())
        files.sort(key=lambda e: e.name.lower())

        for entry in dirs + files:
            display = entry.name + "/" if entry.is_dir else entry.name
            name_item = QStandardItem(display)
            name_item.setEditable(False)
            name_item.setData(QFileInfo(entry.path), Qt.ItemDataRole.UserRole)
            nav_key = f"sftp_nav:{entry.path}" if entry.is_dir else None
            name_item.setData(nav_key, Qt.ItemDataRole.UserRole + 1) if nav_key else None

            size_item = QStandardItem("<DIR>" if entry.is_dir else str(entry.size))
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            from datetime import datetime
            try:
                mod_str = datetime.fromtimestamp(entry.mtime).strftime("%Y-%m-%d %H:%M")
            except (OSError, ValueError):
                mod_str = ""
            modified_item = QStandardItem(mod_str)
            modified_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            status_item = QStandardItem("remote")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.model.appendRow([name_item, size_item, modified_item, status_item])

    def _on_context_menu(self, pos):
        index = self.tree_view.indexAt(pos)
        if not index.isValid():
            return
        item = self.model.itemFromIndex(index.siblingAtColumn(0))
        if not item:
            return
        file_info = item.data(Qt.ItemDataRole.UserRole)
        if not file_info:
            return

        menu = QMenu(self)
        open_action = menu.addAction("Open")
        copy_action = menu.addAction("Copy to Other Side")
        delete_action = menu.addAction("Delete")
        rename_action = menu.addAction("Rename")
        menu.addSeparator()
        properties_action = menu.addAction("Properties")

        chosen = menu.exec(self.tree_view.viewport().mapToGlobal(pos))
        if chosen == open_action:
            self.open_requested.emit(file_info.absoluteFilePath())
        elif chosen == copy_action:
            selected = self.tree_view.selectionModel().selectedRows(0)
            paths = []
            for idx in selected:
                it = self.model.itemFromIndex(idx)
                if it:
                    fi = it.data(Qt.ItemDataRole.UserRole)
                    if fi:
                        paths.append(fi.absoluteFilePath())
            self.copy_to_other_requested.emit(paths)
        elif chosen == delete_action:
            selected = self.tree_view.selectionModel().selectedRows(0)
            paths = []
            for idx in selected:
                it = self.model.itemFromIndex(idx)
                if it:
                    fi = it.data(Qt.ItemDataRole.UserRole)
                    if fi:
                        paths.append(fi.absoluteFilePath())
            self.delete_requested.emit(paths)
        elif chosen == rename_action:
            old_path = file_info.absoluteFilePath()
            old_name = file_info.fileName()
            self.rename_requested.emit(old_path, old_name)
        elif chosen == properties_action:
            self.properties_requested.emit(file_info.absoluteFilePath())

    def _on_item_double_clicked(self, index):
        item = self.model.itemFromIndex(index.siblingAtColumn(0))
        if not item:
            return

        # Check if this is a "navigate back" entry
        nav_path = item.data(Qt.ItemDataRole.UserRole + 1)
        if nav_path and isinstance(nav_path, str):
            if nav_path == "..exit_archive":
                self._exit_archive()
                return
            elif nav_path.startswith(ARCHIVE_PREFIX):
                self.set_path(nav_path)
                return
            elif nav_path == "..parent":
                parent = os.path.dirname(self.current_path)
                if parent and parent != self.current_path:
                    self.set_path(parent)
                return
            elif nav_path.startswith("sftp_parent:"):
                new_path = nav_path[len("sftp_parent:"):]
                self.current_path = f"sftp://{self._sftp_conn.creds.username}@{self._sftp_conn.creds.host}:{self._sftp_conn.creds.port}{new_path}"
                self.path_edit.setText(self.current_path)
                self._populate_remote(new_path)
                self.path_changed.emit(self.current_path)
                return
            elif nav_path.startswith("sftp_nav:"):
                remote_path = nav_path[len("sftp_nav:"):]
                self.current_path = f"sftp://{self._sftp_conn.creds.username}@{self._sftp_conn.creds.host}:{self._sftp_conn.creds.port}{remote_path}"
                self.path_edit.setText(self.current_path)
                self._populate_remote(remote_path)
                self.path_changed.emit(self.current_path)
                return

        file_info = item.data(Qt.ItemDataRole.UserRole)
        if not file_info:
            return

        # Check if clicking on an archive file in normal filesystem mode
        if not self._archive_path and file_info.isFile() and is_archive(file_info.absoluteFilePath()):
            self._enter_archive(file_info.absoluteFilePath())
            return

        if file_info.isDir():
            self.set_path(file_info.absoluteFilePath())
        else:
            self.item_double_clicked.emit(
                "left" if self.title == "Left" else "right", file_info
            )

    def _enter_archive(self, archive_path: str):
        """Navigate into an archive file."""
        self._archive_path = archive_path
        self._archive_prefix = ""
        display = f"{ARCHIVE_PREFIX}{archive_path}"
        self.current_path = display
        self.path_edit.setText(display)
        self.path_edit.setStyleSheet("")
        self._populate_archive_contents()
        self.path_changed.emit(display)

    def _exit_archive(self):
        """Exit archive browsing mode, return to the archive's parent directory."""
        if self._archive_path:
            parent = os.path.dirname(self._archive_path)
            self._archive_path = None
            self._archive_prefix = ""
            if parent and os.path.isdir(parent):
                self.set_path(parent)

    def _navigate_archive_up(self):
        """Navigate up one level inside the archive, or exit if at top."""
        if not self._archive_prefix:
            self._exit_archive()
            return
        parts = self._archive_prefix.rstrip("/").rsplit("/", 1)
        self._archive_prefix = parts[0] if len(parts) > 1 else ""
        self._populate_archive_contents()

    def _populate_archive_contents(self):
        """Populate tree view with archive entries at the current prefix depth."""
        from src.core.archive import list_archive_at_depth as list_entries

        self.model.removeRows(0, self.model.rowCount())

        entries = list_entries(self._archive_path, self._archive_prefix)
        if not entries:
            error_item = QStandardItem("(empty or unreadable archive)")
            error_item.setEditable(False)
            self.model.appendRow([error_item, QStandardItem(""), QStandardItem(""), QStandardItem("")])
            return

        # Add ".." entry to go back
        if self._archive_prefix:
            parent_key = "..archive_up"
        else:
            parent_key = "..exit_archive"
        dot_item = QStandardItem("..")
        dot_item.setData(QFileInfo(self._archive_path), Qt.ItemDataRole.UserRole)
        dot_item.setData(parent_key, Qt.ItemDataRole.UserRole + 1)
        dot_item.setEditable(False)
        dir_size = QStandardItem("<DIR>")
        dir_size.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.model.appendRow([dot_item, dir_size, QStandardItem(""), QStandardItem("")])

        for entry in entries:
            display_name = entry.name.split("/")[-1] if "/" in entry.name else entry.name
            name_item = QStandardItem(display_name if not entry.is_dir else display_name + "/")
            name_item.setEditable(False)

            if entry.is_dir:
                size_item = QStandardItem("<DIR>")
                full_nav = f"{ARCHIVE_PREFIX}{self._archive_path}/{entry.name}"
                name_item.setData(full_nav, Qt.ItemDataRole.UserRole + 1)
            else:
                size_item = QStandardItem(str(entry.size))
                name_item.setData(None, Qt.ItemDataRole.UserRole + 1)

            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            modified_item = QStandardItem("")
            modified_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            status_item = QStandardItem("in-archive")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Store QFileInfo pointing to the archive itself for context menu ops
            name_item.setData(QFileInfo(self._archive_path), Qt.ItemDataRole.UserRole)

            self.model.appendRow([name_item, size_item, modified_item, status_item])

    def set_path(self, path):
        """Set the current path and populate the tree view."""
        # Handle SFTP URLs
        if isinstance(path, str) and path.startswith(SFTP_PREFIX):
            if not self._sftp_conn or not self._sftp_conn.connected:
                return
            remote_path = get_remote_path(path)
            self.current_path = path
            self.path_edit.setText(path)
            self.path_edit.setStyleSheet("")
            self._populate_remote(remote_path)
            self.path_changed.emit(path)
            return

        # Handle archive-prefixed paths
        if isinstance(path, str) and path.startswith(ARCHIVE_PREFIX):
            rest = path[len(ARCHIVE_PREFIX):]
            # Split: first segment is the archive file, rest is the prefix
            # Find the archive file - try longest match that is an existing file
            archive_file = None
            inner = ""
            parts = rest.split("/")
            for i in range(len(parts), 0, -1):
                candidate = "/".join(parts[:i])
                if os.path.isfile(candidate):
                    archive_file = candidate
                    inner = "/".join(parts[i:])
                    break
            if archive_file and is_archive(archive_file):
                self._archive_path = archive_file
                self._archive_prefix = inner
                self.current_path = path
                self.path_edit.setText(path)
                self.path_edit.setStyleSheet("")
                self._populate_archive_contents()
                self.path_changed.emit(path)
                return
            # If not an archive path, fall through to normal handling

        if not os.path.exists(path):
            return

        self._archive_path = None
        self._archive_prefix = ""
        self.current_path = path
        self.path_edit.setText(path)
        self.path_edit.setStyleSheet("")
        self.populate_tree(path)
        self.path_changed.emit(path)

    def populate_tree(self, path):
        """Populate the tree view with contents of the given path."""
        self.model.removeRows(0, self.model.rowCount())

        if not os.path.isdir(path):
            if os.path.isfile(path) and is_archive(path):
                self._enter_archive(path)
                return
            self._add_file_to_model(path)
            return

        try:
            parent_dir = os.path.dirname(path)
            if path != parent_dir:
                parent_item = QStandardItem("..")
                parent_item.setData(QFileInfo(parent_dir), Qt.ItemDataRole.UserRole)
                parent_item.setData("..parent", Qt.ItemDataRole.UserRole + 1)
                parent_item.setEditable(False)
                size_item = QStandardItem("<DIR>")
                size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                modified_item = QStandardItem("")
                modified_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                status_item = QStandardItem("")
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.model.appendRow([parent_item, size_item, modified_item, status_item])

            dirs = []
            files = []

            with os.scandir(path) as it:
                for entry in it:
                    if entry.name.startswith(".") and entry.name not in [".", ".."]:
                        continue
                    if entry.is_dir():
                        dirs.append(entry)
                    else:
                        files.append(entry)

            dirs.sort(key=lambda e: e.name.lower())
            files.sort(key=lambda e: e.name.lower())

            for entry in dirs:
                self._add_file_to_model(entry.path)
            for entry in files:
                self._add_file_to_model(entry.path)

        except PermissionError:
            error_item = QStandardItem("Access Denied")
            error_item.setData(QFileInfo(path), Qt.ItemDataRole.UserRole)
            size_item = QStandardItem("")
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            modified_item = QStandardItem("")
            modified_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            status_item = QStandardItem("ERROR")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.model.appendRow([error_item, size_item, modified_item, status_item])

    def _add_file_to_model(self, file_path):
        """Add a single file or directory to the model."""
        from src.core.archive import is_archive as is_arch

        file_info = QFileInfo(file_path)
        name = file_info.fileName()

        is_dir = file_info.isDir()
        is_arch_file = not is_dir and file_info.isFile() and is_arch(file_path)

        name_text = name + " 📦" if is_arch_file else name
        name_item = QStandardItem(name_text)
        name_item.setData(file_info, Qt.ItemDataRole.UserRole)
        name_item.setEditable(False)

        if is_dir:
            size_item = QStandardItem("<DIR>")
        else:
            size_item = QStandardItem(str(file_info.size()))
        size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        modified_time = file_info.lastModified().toString("yyyy-MM-dd hh:mm")
        modified_item = QStandardItem(modified_time)
        modified_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        status_item = QStandardItem("archive" if is_arch_file else "unknown")
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self.model.appendRow([name_item, size_item, modified_item, status_item])

    def set_item_status(self, index, status_text, color=None):
        """Set the status and background color for an item in the status column."""
        if index.isValid():
            status_item = QStandardItem(status_text)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if color:
                status_item.setBackground(QBrush(QColor(color)))
            self.model.setItem(index.row(), 3, status_item)

    def get_current_path(self):
        """Get the current path being displayed."""
        return self.current_path

    def disconnect_sftp(self):
        """Disconnect SFTP if connected."""
        if self._sftp_conn:
            self._sftp_conn.disconnect()
            self._sftp_conn = None

    def clear(self):
        """Clear the tree view."""
        self.model.removeRows(0, self.model.rowCount())
        self.path_edit.clear()
        self.current_path = ""
        self._archive_path = None
        self._archive_prefix = ""
        if self._sftp_conn:
            self._sftp_conn.disconnect()
            self._sftp_conn = None

    def is_in_archive(self) -> bool:
        """Return True if currently browsing inside an archive."""
        return self._archive_path is not None

    def get_archive_info(self):
        """Return (archive_path, inner_prefix) if in archive mode, else (None, '')."""
        return self._archive_path, self._archive_prefix
