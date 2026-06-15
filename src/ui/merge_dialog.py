from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QSplitter,
    QApplication,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor

from src.core.merge import three_way_merge, MergeOp


class MergeDialog(QDialog):
    """
    A 3-way merge dialog showing BASE, LOCAL, REMOTE panels
    with a merged output and conflict-resolution actions.
    """

    def __init__(self, base_text, local_text, remote_text, base_label="BASE",
                 local_label="LOCAL", remote_label="REMOTE", parent=None):
        super().__init__(parent)
        self.setWindowTitle("3-Way Merge")
        self.resize(1400, 900)

        self.base_text = base_text
        self.local_text = local_text
        self.remote_text = remote_text
        self.base_label = base_label
        self.local_label = local_label
        self.remote_label = remote_label

        self.result = None  # filled on accept
        self.setup_ui()
        self.run_merge()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Top row: BASE | LOCAL | REMOTE
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.base_edit = self._create_readonly_editor()
        self.local_edit = self._create_readonly_editor()
        self.remote_edit = self._create_readonly_editor()

        top_splitter.addWidget(self._wrap_editor(self.base_edit, self.base_label))
        top_splitter.addWidget(self._wrap_editor(self.local_edit, self.local_label))
        top_splitter.addWidget(self._wrap_editor(self.remote_edit, self.remote_label))
        top_splitter.setSizes([400, 400, 400])

        # Bottom row: merged output with conflict navigation
        bottom_layout = QHBoxLayout()

        self.merged_edit = QTextEdit()
        self.merged_edit.setFont(QFont("Courier New", 10))
        self.merged_edit.setFixedPitch(True)
        self.merged_edit.setPlaceholderText("Merged result will appear here...")

        # Conflict navigation buttons
        nav_layout = QVBoxLayout()
        self.prev_conflict_btn = QPushButton("← Previous Conflict")
        self.next_conflict_btn = QPushButton("Next Conflict →")
        self.take_local_btn = QPushButton("Take LOCAL")
        self.take_remote_btn = QPushButton("Take REMOTE")
        self.take_both_btn = QPushButton("Take Both")
        self.take_base_btn = QPushButton("Take BASE")

        self.prev_conflict_btn.clicked.connect(self._goto_prev_conflict)
        self.next_conflict_btn.clicked.connect(self._goto_next_conflict)
        self.take_local_btn.clicked.connect(lambda: self._resolve_conflict("local"))
        self.take_remote_btn.clicked.connect(lambda: self._resolve_conflict("remote"))
        self.take_both_btn.clicked.connect(lambda: self._resolve_conflict("both"))
        self.take_base_btn.clicked.connect(lambda: self._resolve_conflict("base"))

        nav_layout.addWidget(self.prev_conflict_btn)
        nav_layout.addWidget(self.next_conflict_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(QLabel("Resolution:"))
        nav_layout.addWidget(self.take_local_btn)
        nav_layout.addWidget(self.take_remote_btn)
        nav_layout.addWidget(self.take_both_btn)
        nav_layout.addWidget(self.take_base_btn)
        nav_layout.addStretch()

        bottom_layout.addWidget(self.merged_edit, stretch=3)
        bottom_layout.addLayout(nav_layout, stretch=0)

        # Buttons
        button_layout = QHBoxLayout()
        self.accept_btn = QPushButton("Accept Merge")
        self.cancel_btn = QPushButton("Cancel")
        self.accept_btn.clicked.connect(self._on_accept)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.accept_btn)
        button_layout.addWidget(self.cancel_btn)

        # Status label
        self.status_label = QLabel("Ready")

        layout.addWidget(top_splitter, stretch=2)
        layout.addLayout(bottom_layout, stretch=3)
        layout.addWidget(self.status_label)
        layout.addLayout(button_layout)

    def _create_readonly_editor(self):
        edit = QTextEdit()
        edit.setReadOnly(True)
        edit.setFont(QFont("Courier New", 10))
        edit.setFixedPitch(True)
        return edit

    def _wrap_editor(self, editor, title):
        widget = QVBoxLayout()
        widget.addWidget(QLabel(f"<b>{title}</b>"))
        widget.addWidget(editor)
        container = QDialog()
        container.setLayout(widget)
        return container

    def run_merge(self):
        """Run the 3-way merge engine and populate the merged editor."""
        self.merge_result = three_way_merge(
            self.base_text, self.local_text, self.remote_text
        )

        self.base_edit.setPlainText(self.base_text)
        self.local_edit.setPlainText(self.local_text)
        self.remote_edit.setPlainText(self.remote_text)

        self._populate_merged_editor()
        self._update_status()

    def _populate_merged_editor(self):
        """Populate merged editor with styled text, highlighting conflicts."""
        self.merged_edit.clear()
        cursor = self.merged_edit.textCursor()

        red_format = QTextCharFormat()
        red_format.setBackground(QColor(255, 200, 200))
        green_format = QTextCharFormat()
        green_format.setBackground(QColor(200, 255, 200))
        yellow_format = QTextCharFormat()
        yellow_format.setBackground(QColor(255, 255, 200))

        for hunk in self.merge_result.hunks:
            if hunk.op == MergeOp.CONFLICT:
                cursor.setCharFormat(red_format)
                cursor.insertText("<<<<<<< BASE\n")
                for line in hunk.base_lines:
                    cursor.insertText(line + "\n")
                cursor.insertText("======= LOCAL\n")
                for line in hunk.local_lines:
                    cursor.insertText(line + "\n")
                cursor.insertText("======= REMOTE\n")
                for line in hunk.remote_lines:
                    cursor.insertText(line + "\n")
                cursor.insertText(">>>>>>>\n")
            elif hunk.op == MergeOp.LOCAL:
                cursor.setCharFormat(green_format)
                for line in hunk.merged_lines:
                    cursor.insertText(line + "\n")
            elif hunk.op == MergeOp.REMOTE:
                cursor.setCharFormat(green_format)
                for line in hunk.merged_lines:
                    cursor.insertText(line + "\n")
            else:
                cursor.setCharFormat(yellow_format if hunk.op == MergeOp.BASE else QTextCharFormat())
                for line in hunk.merged_lines:
                    cursor.insertText(line + "\n")

        self.merged_edit.setTextCursor(cursor)

    def _update_status(self):
        if self.merge_result.has_conflicts:
            self.status_label.setText(
                f"<b style='color:red'>{self.merge_result.conflict_count} conflict(s) remaining</b>"
            )
            self.accept_btn.setEnabled(False)
        else:
            self.status_label.setText("<b style='color:green'>No conflicts — ready to accept</b>")
            self.accept_btn.setEnabled(True)

    def _goto_next_conflict(self):
        cursor = self.merged_edit.textCursor()
        text = self.merged_edit.toPlainText()
        pos = cursor.position()
        idx = text.find("<<<<<<< BASE", pos)
        if idx == -1:
            idx = text.find("<<<<<<< BASE", 0)
        if idx != -1:
            cursor.setPosition(idx)
            self.merged_edit.setTextCursor(cursor)
            self.merged_edit.ensureCursorVisible()

    def _goto_prev_conflict(self):
        cursor = self.merged_edit.textCursor()
        text = self.merged_edit.toPlainText()
        pos = cursor.position()
        idx = text.rfind("<<<<<<< BASE", 0, pos)
        if idx == -1:
            idx = text.rfind("<<<<<<< BASE")
        if idx != -1:
            cursor.setPosition(idx)
            self.merged_edit.setTextCursor(cursor)
            self.merged_edit.ensureCursorVisible()

    def _resolve_conflict(self, choice):
        """Resolve the conflict at cursor by replacing conflict markers."""
        cursor = self.merged_edit.textCursor()
        text = self.merged_edit.toPlainText()
        pos = cursor.position()

        # Find conflict block containing cursor
        block_start = text.rfind("<<<<<<< BASE", 0, pos)
        if block_start == -1:
            return
        block_end = text.find(">>>>>>>", block_start)
        if block_end == -1:
            return
        block_end += len(">>>>>>>")

        # Extract sections
        block = text[block_start:block_end]
        local_start = block.find("======= LOCAL")
        remote_start = block.find("======= REMOTE")
        base_end = block.find("======= LOCAL")
        local_end = block.find("======= REMOTE")
        remote_end = block.find(">>>>>>>")

        base_lines = block[len("<<<<<<< BASE"):base_end].strip().split("\n") if base_end != -1 else []
        local_lines = block[local_start + len("======= LOCAL"):local_end].strip().split("\n") if local_start != -1 else []
        remote_lines = block[remote_start + len("======= REMOTE"):remote_end].strip().split("\n") if remote_start != -1 else []

        if choice == "local":
            replacement = "\n".join(local_lines)
        elif choice == "remote":
            replacement = "\n".join(remote_lines)
        elif choice == "both":
            replacement = "\n".join(local_lines + remote_lines)
        else:
            replacement = "\n".join(base_lines)

        # Replace in editor
        cursor.setPosition(block_start)
        cursor.setPosition(block_end, QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(replacement + "\n")

        # Re-check for conflicts
        self._update_status_from_editor()

    def _update_status_from_editor(self):
        text = self.merged_edit.toPlainText()
        count = text.count("<<<<<<< BASE")
        if count > 0:
            self.status_label.setText(f"<b style='color:red'>{count} conflict(s) remaining</b>")
            self.accept_btn.setEnabled(False)
        else:
            self.status_label.setText("<b style='color:green'>No conflicts — ready to accept</b>")
            self.accept_btn.setEnabled(True)

    def _on_accept(self):
        self.result = self.merged_edit.toPlainText()
        self.accept()

    def get_result(self):
        return self.result
