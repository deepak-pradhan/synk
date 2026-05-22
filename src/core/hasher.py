import xxhash
import hashlib
from pathlib import Path
from typing import Optional, Tuple
import os


class Hasher:
    """Handles file hashing for quick comparison."""

    def __init__(self, algorithm: str = "xxh3_64"):
        self.algorithm = algorithm.lower()
        self._hash_funcs = {
            "xxh3_64": self._xxh3_64,
            "xxh64": self._xxh64,
            "md5": self._md5,
            "sha1": self._sha1,
            "sha256": self._sha256,
        }

        if self.algorithm not in self._hash_funcs:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    def hash_file(self, file_path: str | Path) -> Optional[str]:
        """
        Compute hash of a file.

        Returns:
            Hex digest string or None if file cannot be read
        """
        try:
            return self._hash_funcs[self.algorithm](file_path)
        except (OSError, IOError, PermissionError):
            return None

    def _xxh3_64(self, file_path: str | Path) -> str:
        """Compute xxh3_64 hash of a file."""
        h = xxhash.xxh3_64()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def _xxh64(self, file_path: str | Path) -> str:
        """Compute xxh64 hash of a file."""
        h = xxhash.xxh64()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def _md5(self, file_path: str | Path) -> str:
        """Compute MD5 hash of a file."""
        h = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def _sha1(self, file_path: str | Path) -> str:
        """Compute SHA1 hash of a file."""
        h = hashlib.sha1()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def _sha256(self, file_path: str | Path) -> str:
        """Compute SHA256 hash of a file."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()


def quick_compare(
    file1: str | Path, file2: str | Path, hasher: Hasher
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Quickly compare two files by size and hash.

    Returns:
        Tuple of (are_equal, hash1, hash2)
        are_equal is True if files are identical (same size and hash)
        If files cannot be read, hash will be None
    """
    try:
        stat1 = os.stat(file1)
        stat2 = os.stat(file2)

        # Quick size check first
        if stat1.st_size != stat2.st_size:
            hash1 = hasher.hash_file(file1) if stat1.st_size > 0 else ""
            hash2 = hasher.hash_file(file2) if stat2.st_size > 0 else ""
            return False, hash1, hash2

        # If sizes are equal, check hash
        hash1 = hasher.hash_file(file1)
        hash2 = hasher.hash_file(file2)

        if hash1 is None or hash2 is None:
            return False, hash1, hash2

        return hash1 == hash2, hash1, hash2

    except (OSError, IOError, PermissionError):
        return False, None, None


if __name__ == "__main__":
    # Simple test
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "test1.txt")
        file2 = os.path.join(tmpdir, "test2.txt")

        with open(file1, "w") as f:
            f.write("Hello, World!")
        with open(file2, "w") as f:
            f.write("Hello, World!")

        hasher = Hasher("xxh3_64")
        equal, h1, h2 = quick_compare(file1, file2, hasher)
        print(f"Files equal: {equal}")
        print(f"Hash1: {h1}")
        print(f"Hash2: {h2}")

        # Test different files
        with open(file2, "w") as f:
            f.write("Hello, Universe!")

        equal, h1, h2 = quick_compare(file1, file2, hasher)
        print(f"Different files equal: {equal}")
        print(f"Hash1: {h1}")
        print(f"Hash2: {h2}")
