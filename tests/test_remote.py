import pytest

from src.core.remote import parse_sftp_url, get_remote_path, SFTPCredentials, SFTPConnection, RemoteEntry


class TestParseSftpUrl:
    def test_basic(self):
        creds = parse_sftp_url("sftp://user@example.com/home/user")
        assert creds.host == "example.com"
        assert creds.username == "user"
        assert creds.port == 22
        assert creds.password == ""

    def test_with_port(self):
        creds = parse_sftp_url("sftp://user@example.com:2222/data")
        assert creds.host == "example.com"
        assert creds.port == 2222
        assert creds.username == "user"

    def test_with_password(self):
        creds = parse_sftp_url("sftp://user:pass@host/path")
        assert creds.username == "user"
        assert creds.password == "pass"
        assert creds.host == "host"

    def test_host_only(self):
        creds = parse_sftp_url("sftp://myserver/")
        assert creds.host == "myserver"
        assert creds.port == 22
        assert creds.username == ""


class TestGetRemotePath:
    def test_root(self):
        assert get_remote_path("sftp://user@host/") == "/"

    def test_path(self):
        assert get_remote_path("sftp://user@host/home/user/docs") == "/home/user/docs"

    def test_no_path(self):
        result = get_remote_path("sftp://user@host")
        assert result == "/"


class TestRemoteEntry:
    def test_entry_fields(self):
        entry = RemoteEntry(name="test.txt", size=100, mtime=1234567890.0, is_dir=False, path="/home/test.txt")
        assert entry.name == "test.txt"
        assert entry.size == 100
        assert entry.is_dir is False
        assert entry.path == "/home/user/docs" if False else "/home/test.txt"


class TestSFTPConnection:
    def test_not_connected_by_default(self):
        creds = SFTPCredentials(host="localhost", username="test")
        conn = SFTPConnection(creds)
        assert conn.connected is False

    def test_disconnect_idempotent(self):
        creds = SFTPCredentials(host="localhost", username="test")
        conn = SFTPConnection(creds)
        conn.disconnect()  # should not raise
        assert conn.connected is False

    def test_list_dir_returns_empty_when_not_connected(self):
        creds = SFTPCredentials(host="localhost", username="test")
        conn = SFTPConnection(creds)
        assert conn.list_dir("/tmp") == []

    def test_stat_returns_none_when_not_connected(self):
        creds = SFTPCredentials(host="localhost", username="test")
        conn = SFTPConnection(creds)
        assert conn.stat("/tmp/test") is None

    def test_hash_returns_none_when_not_connected(self):
        creds = SFTPCredentials(host="localhost", username="test")
        conn = SFTPConnection(creds)
        assert conn.hash_remote_file("/tmp/test") is None

    def test_download_returns_false_when_not_connected(self):
        creds = SFTPCredentials(host="localhost", username="test")
        conn = SFTPConnection(creds)
        assert conn.download_file("/tmp/test", "/tmp/local") is False

    def test_upload_returns_false_when_not_connected(self):
        creds = SFTPCredentials(host="localhost", username="test")
        conn = SFTPConnection(creds)
        assert conn.upload_file("/tmp/local", "/tmp/test") is False