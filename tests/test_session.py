import tempfile
from pathlib import Path

from src.utils.session import (
    save_session,
    load_session,
    save_last_session,
    load_last_session,
    clear_last_session,
    _sanitize_path,
    LAST_SESSION_FILE,
)


class TestSanitizePath:
    def test_local_path_unchanged(self):
        assert _sanitize_path("/home/user/docs") == "/home/user/docs"

    def test_sftp_without_credentials_unchanged(self):
        url = "sftp://user@host:22/path"
        assert _sanitize_path(url) == url

    def test_sftp_with_password_strips_password(self):
        assert _sanitize_path("sftp://user:pass@host/path") == "sftp://user@host/path"

    def test_sftp_with_password_and_port(self):
        assert (
            _sanitize_path("sftp://user:pass@host:2222/path")
            == "sftp://user@host:2222/path"
        )

    def test_sftp_only_password_no_user(self):
        assert _sanitize_path("sftp://:pass@host/path") == "sftp://host/path"


class TestSaveAndLoadSession:
    def test_round_trip(self, tmp_path):
        p = tmp_path / "session.toml"
        data = {"left_path": "/a", "right_path": "/b"}
        assert save_session(str(p), data) is True
        loaded = load_session(str(p))
        assert loaded == data


class TestSaveLastSession:
    def test_strips_sftp_password(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "src.utils.session.LAST_SESSION_FILE", tmp_path / "last_session.toml"
        )
        config = {"comparison": {"hash_algorithm": "xxh3_64"}, "ignore": {"patterns": [], "show_identical": True}}
        result = save_last_session(
            "sftp://user:secret@host:2222/remote",
            "/local",
            config,
        )
        assert result is True
        loaded = load_last_session()
        assert loaded["left_path"] == "sftp://user@host:2222/remote"
        assert loaded["right_path"] == "/local"

    def test_clears_previous_session(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "src.utils.session.LAST_SESSION_FILE", tmp_path / "last_session.toml"
        )
        config = {"comparison": {"hash_algorithm": "xxh3_64"}, "ignore": {"patterns": [], "show_identical": True}}
        save_last_session("/a", "/b", config)
        clear_last_session()
        assert load_last_session() is None
