import paramiko
import os
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass
class RemoteEntry:
    name: str
    size: int
    mtime: float
    is_dir: bool
    path: str


@dataclass
class SFTPCredentials:
    host: str
    port: int = 22
    username: str = ""
    password: str = ""
    key_path: str = ""


def parse_sftp_url(url: str) -> SFTPCredentials:
    """Parse sftp://user@host:port/path into SFTPCredentials."""
    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 22
    username = parsed.username or ""
    password = parsed.password or ""
    return SFTPCredentials(host=host, port=port, username=username, password=password)


def get_remote_path(url: str) -> str:
    """Extract the remote path from an sftp:// URL."""
    parsed = urlparse(url)
    path = parsed.path or "/"
    return path


class SFTPConnection:
    """Manages an SSH/SFTP connection to a remote server."""

    def __init__(self, creds: SFTPCredentials):
        self.creds = creds
        self._client: Optional[paramiko.SSHClient] = None
        self._sftp: Optional[paramiko.SFTPClient] = None

    @property
    def connected(self) -> bool:
        if self._client is None:
            return False
        transport = self._client.get_transport()
        return transport is not None and transport.is_active()

    def connect(self) -> str:
        """Connect to the remote server. Returns an error string or empty string on success."""
        try:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            kwargs: dict[str, object] = {
                "hostname": self.creds.host,
                "port": self.creds.port,
                "username": self.creds.username,
            }

            if self.creds.key_path and os.path.exists(os.path.expanduser(self.creds.key_path)):
                kwargs["key_filename"] = os.path.expanduser(self.creds.key_path)
            elif self.creds.password:
                kwargs["password"] = self.creds.password
            else:
                kwargs["allow_agent"] = True
                kwargs["look_for_keys"] = True

            # kwargs assembled dynamically (key vs password vs agent auth); paramiko's
            # connect() is too strictly typed for a **dict splat.
            self._client.connect(**kwargs)  # type: ignore[arg-type]
            self._sftp = self._client.open_sftp()
            return ""
        except Exception as e:
            self.disconnect()
            return str(e)

    def disconnect(self):
        if self._sftp:
            try:
                self._sftp.close()
            except Exception:
                pass
            self._sftp = None
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

    def list_dir(self, remote_path: str) -> list[RemoteEntry]:
        """List contents of a remote directory."""
        if not self._sftp:
            return []

        entries = []
        try:
            for attr in self._sftp.listdir_attr(remote_path):
                entries.append(RemoteEntry(
                    name=attr.filename,
                    size=(attr.st_size or 0) if not ((attr.st_mode or 0) & 0o40000) else 0,
                    mtime=attr.st_mtime if attr.st_mtime else 0.0,
                    is_dir=bool((attr.st_mode or 0) & 0o40000),
                    path=remote_path.rstrip("/") + "/" + attr.filename,
                ))
        except Exception:
            pass
        return entries

    def stat(self, remote_path: str) -> Optional[RemoteEntry]:
        """Get stat info for a single remote path."""
        if not self._sftp:
            return None
        try:
            attr = self._sftp.stat(remote_path)
            return RemoteEntry(
                name=os.path.basename(remote_path),
                size=attr.st_size or 0,
                mtime=attr.st_mtime if attr.st_mtime else 0.0,
                is_dir=bool((attr.st_mode or 0) & 0o40000),
                path=remote_path,
            )
        except Exception:
            return None

    def hash_remote_file(self, remote_path: str, algorithm: str = "xxh3_64") -> Optional[str]:
        """Compute a hash of a remote file by streaming it through SFTP."""
        import xxhash
        if not self._sftp:
            return None

        hasher_map = {
            "xxh3_64": xxhash.xxh3_64(),
            "xxh64": xxhash.xxh64(),
            "md5": __import__("hashlib").md5(),
            "sha1": __import__("hashlib").sha1(),
            "sha256": __import__("hashlib").sha256(),
        }
        h = hasher_map.get(algorithm)
        if h is None:
            return None
        try:
            with self._sftp.open(remote_path, "rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    h.update(chunk)
                return h.hexdigest()
        except Exception:
            return None

    def read_text(self, remote_path: str, encoding: str = "utf-8") -> Optional[str]:
        """Read a remote file as text."""
        if not self._sftp:
            return None
        try:
            with self._sftp.open(remote_path, "rb") as f:
                return f.read().decode(encoding)
        except Exception:
            return None

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download a remote file to a local path."""
        if not self._sftp:
            return False
        try:
            self._sftp.get(remote_path, local_path)
            return True
        except Exception:
            return False

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload a local file to a remote path."""
        if not self._sftp:
            return False
        try:
            self._sftp.put(local_path, remote_path)
            return True
        except Exception:
            return False

    def mkdir(self, remote_path: str) -> bool:
        """Create a remote directory."""
        if not self._sftp:
            return False
        try:
            self._sftp.mkdir(remote_path)
            return True
        except Exception:
            return False

    def remove(self, remote_path: str) -> bool:
        """Remove a remote file."""
        if not self._sftp:
            return False
        try:
            self._sftp.remove(remote_path)
            return True
        except Exception:
            return False

    def rmdir(self, remote_path: str) -> bool:
        """Remove a remote directory."""
        if not self._sftp:
            return False
        try:
            self._sftp.rmdir(remote_path)
            return True
        except Exception:
            return False

    def rename(self, old_path: str, new_path: str) -> bool:
        """Rename a remote file or directory."""
        if not self._sftp:
            return False
        try:
            self._sftp.rename(old_path, new_path)
            return True
        except Exception:
            return False