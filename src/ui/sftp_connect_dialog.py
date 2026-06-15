from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QHBoxLayout,
    QCheckBox,
    QLabel,
)
from PySide6.QtCore import Qt
from src.core.remote import SFTPCredentials


class SFTPConnectDialog(QDialog):
    def __init__(self, parent=None, initial_url: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Connect to SFTP Server")
        self.setMinimumWidth(400)
        self._creds = None
        self._remote_path = "/"
        self.setup_ui(initial_url)

    def setup_ui(self, initial_url: str):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("e.g. example.com")
        form.addRow("Host:", self.host_edit)

        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(22)
        form.addRow("Port:", self.port_spin)

        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("Username")
        form.addRow("Username:", self.user_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Password (leave blank for key auth)")
        form.addRow("Password:", self.password_edit)

        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("~/.ssh/id_rsa (leave blank for agent)")
        form.addRow("SSH Key:", self.key_edit)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("/remote/path")
        self.path_edit.setText("/")
        form.addRow("Remote Path:", self.path_edit)

        layout.addLayout(form)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        buttons = QHBoxLayout()
        buttons.addStretch()
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self._on_connect)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(connect_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

        if initial_url:
            self._parse_url(initial_url)

    def _parse_url(self, url: str):
        from src.core.remote import parse_sftp_url, get_remote_path
        if not url.startswith("sftp://"):
            return
        creds = parse_sftp_url(url)
        self.host_edit.setText(creds.host)
        self.port_spin.setValue(creds.port)
        self.user_edit.setText(creds.username)
        if creds.password:
            self.password_edit.setText(creds.password)
        self.path_edit.setText(get_remote_path(url))

    def _on_connect(self):
        host = self.host_edit.text().strip()
        if not host:
            self.error_label.setText("Host is required")
            return
        user = self.user_edit.text().strip()
        if not user:
            self.error_label.setText("Username is required")
            return

        self._creds = SFTPCredentials(
            host=host,
            port=self.port_spin.value(),
            username=user,
            password=self.password_edit.text(),
            key_path=self.key_edit.text().strip(),
        )
        self._remote_path = self.path_edit.text().strip() or "/"
        self.accept()

    def get_credentials(self) -> SFTPCredentials:
        return self._creds

    def get_remote_path(self) -> str:
        return self._remote_path