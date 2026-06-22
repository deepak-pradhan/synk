from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QPlainTextEdit,
    QCheckBox,
    QPushButton,
    QLabel,
)
from src.utils.config import load_config, save_config

HASH_ALGORITHMS = ["xxh3_64", "xxh64", "md5", "sha1", "sha256"]
THEMES = ["light", "dark"]


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(500, 400)
        self._config = load_config()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.general_tab = self._build_general_tab()
        self.comparison_tab = self._build_comparison_tab()
        self.ignore_tab = self._build_ignore_tab()
        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.comparison_tab, "Comparison")
        self.tabs.addTab(self.ignore_tab, "Ignore Patterns")
        layout.addWidget(self.tabs)

        buttons = QHBoxLayout()
        buttons.addStretch()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._on_save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def _build_general_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES)
        self.theme_combo.setCurrentText(self._config.get("general", {}).get("theme", "light"))
        form.addRow("Theme:", self.theme_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self._config.get("general", {}).get("font_size", 10))
        form.addRow("Font size:", self.font_size_spin)

        return tab

    def _build_comparison_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)

        self.hash_combo = QComboBox()
        self.hash_combo.addItems(HASH_ALGORITHMS)
        self.hash_combo.setCurrentText(
            self._config.get("comparison", {}).get("hash_algorithm", "xxh3_64")
        )
        form.addRow("Hash algorithm:", self.hash_combo)

        self.context_spin = QSpinBox()
        self.context_spin.setRange(0, 20)
        self.context_spin.setValue(
            self._config.get("comparison", {}).get("context_lines", 3)
        )
        form.addRow("Diff context lines:", self.context_spin)

        return tab

    def _build_ignore_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("One glob pattern per line:"))

        self.ignore_edit = QPlainTextEdit()
        patterns = self._config.get("ignore", {}).get("patterns", [])
        self.ignore_edit.setPlainText("\n".join(patterns))
        layout.addWidget(self.ignore_edit)

        self.show_identical_cb = QCheckBox("Show identical files")
        self.show_identical_cb.setChecked(
            self._config.get("ignore", {}).get("show_identical", True)
        )
        layout.addWidget(self.show_identical_cb)

        return tab

    def _on_save(self):
        self._config["general"]["theme"] = self.theme_combo.currentText()
        self._config["general"]["font_size"] = self.font_size_spin.value()
        self._config["comparison"]["hash_algorithm"] = self.hash_combo.currentText()
        self._config["comparison"]["context_lines"] = self.context_spin.value()
        raw = self.ignore_edit.toPlainText()
        self._config["ignore"]["patterns"] = [
            p.strip() for p in raw.split("\n") if p.strip()
        ]
        self._config["ignore"]["show_identical"] = self.show_identical_cb.isChecked()
        if save_config(self._config):
            self.accept()

    def get_config(self) -> dict:
        return self._config
