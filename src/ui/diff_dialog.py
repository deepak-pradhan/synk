from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QApplication,
)
from PySide6.QtGui import QFont, QTextCharFormat, QColor
from diff_match_patch import diff_match_patch
import os


class DiffDialog(QDialog):
    """A dialog showing side-by-side differences between two files."""

    def __init__(self, file1_path, file2_path, parent=None):
        super().__init__(parent)
        self.file1_path = file1_path
        self.file2_path = file2_path
        self.setWindowTitle(
            f"Diff: {os.path.basename(file1_path)} ↔ {os.path.basename(file2_path)}"
        )
        self.resize(1000, 600)
        self.setup_ui()
        self.load_and_diff_files()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # File labels
        labels_layout = QHBoxLayout()
        self.file1_label = QLabel(os.path.basename(self.file1_path))
        self.file2_label = QLabel(os.path.basename(self.file2_path))
        labels_layout.addWidget(self.file1_label)
        labels_layout.addStretch()
        labels_layout.addWidget(self.file2_label)
        layout.addLayout(labels_layout)

        # Text editors
        editors_layout = QHBoxLayout()
        self.text_edit1 = QTextEdit()
        self.text_edit2 = QTextEdit()

        # Make them read-only and use monospace font
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.text_edit1.setFont(font)
        self.text_edit2.setFont(font)
        self.text_edit1.setReadOnly(True)
        self.text_edit2.setReadOnly(True)

        editors_layout.addWidget(self.text_edit1)
        editors_layout.addWidget(self.text_edit2)
        layout.addLayout(editors_layout)

        # Button box
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

    def load_and_diff_files(self):
        """Load both files, compute diff, and display with highlighting."""
        try:
            # Try to read as text files
            with open(self.file1_path, "r", encoding="utf-8", errors="replace") as f:
                text1 = f.read()
            with open(self.file2_path, "r", encoding="utf-8", errors="replace") as f:
                text2 = f.read()

            # Compute diff
            dmp = diff_match_patch()
            diffs = dmp.diff_main(text1, text2)
            dmp.diff_cleanupSemantic(diffs)

            # Display first file with deletions highlighted
            self.text_edit1.clear()
            cursor1 = self.text_edit1.textCursor()
            for op, data in diffs:
                if op == dmp.DIFF_EQUAL:
                    cursor1.insertText(data)
                elif op == dmp.DIFF_DELETE:
                    # Highlight deletions in red
                    format = QTextCharFormat()
                    format.setBackground(QColor("#ffcccc"))  # Light red
                    cursor1.insertText(data, format)
                # DIFF_INSERT is ignored for first file

            # Display second file with insertions highlighted
            self.text_edit2.clear()
            cursor2 = self.text_edit2.textCursor()
            for op, data in diffs:
                if op == dmp.DIFF_EQUAL:
                    cursor2.insertText(data)
                elif op == dmp.DIFF_INSERT:
                    # Highlight insertions in green
                    format = QTextCharFormat()
                    format.setBackground(QColor("#ccffcc"))  # Light green
                    cursor2.insertText(data, format)
                # DIFF_DELETE is ignored for second file

        except UnicodeDecodeError:
            # Handle binary files
            self.text_edit1.setPlainText(
                f"Binary file: {self.file1_path}\nCannot display as text."
            )
            self.text_edit2.setPlainText(
                f"Binary file: {self.file2_path}\nCannot display as text."
            )
        except Exception as e:
            self.text_edit1.setPlainText(f"Error reading file: {e}")
            self.text_edit2.setPlainText(f"Error reading file: {e}")


if __name__ == "__main__":
    # Simple test
    import sys
    import tempfile
    import os

    app = QApplication(sys.argv)

    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "file1.txt")
        file2 = os.path.join(tmpdir, "file2.txt")

        with open(file1, "w") as f:
            f.write("Hello World\nThis is a test.\nLine 3\n")
        with open(file2, "w") as f:
            f.write("Hello World\nThis is a modified test.\nLine 3\nLine 4 added\n")

        dialog = DiffDialog(file1, file2)
        dialog.show()
        sys.exit(app.exec())
