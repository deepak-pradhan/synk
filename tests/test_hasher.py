import tempfile
import os

import pytest

from src.core.hasher import Hasher, quick_compare


class TestHasher:
    def test_xxh3_64_same_content(self, tmp_path):
        file1 = tmp_path / "a.txt"
        file2 = tmp_path / "b.txt"
        file1.write_text("Hello, World!")
        file2.write_text("Hello, World!")

        hasher = Hasher("xxh3_64")
        h1 = hasher.hash_file(str(file1))
        h2 = hasher.hash_file(str(file2))
        assert isinstance(h1, str)
        assert len(h1) == 16
        assert h1 == h2

    def test_xxh3_64_different_content(self, tmp_path):
        file1 = tmp_path / "a.txt"
        file2 = tmp_path / "b.txt"
        file1.write_text("Hello, World!")
        file2.write_text("Hello, Universe!")

        hasher = Hasher("xxh3_64")
        h1 = hasher.hash_file(str(file1))
        h2 = hasher.hash_file(str(file2))
        assert h1 != h2

    def test_unsupported_algorithm(self):
        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            Hasher("bad_algo")

    @pytest.mark.parametrize("algo", ["xxh3_64", "xxh64", "md5", "sha1", "sha256"])
    def test_all_algorithms_return_string(self, tmp_path, algo):
        f = tmp_path / "test.txt"
        f.write_text("payload")
        hasher = Hasher(algo)
        result = hasher.hash_file(str(f))
        assert isinstance(result, str)
        assert len(result) > 0


class TestQuickCompare:
    def test_equal_files(self, tmp_path):
        file1 = tmp_path / "a.txt"
        file2 = tmp_path / "b.txt"
        file1.write_text("Hello, World!")
        file2.write_text("Hello, World!")

        hasher = Hasher("xxh3_64")
        equal, h1, h2 = quick_compare(str(file1), str(file2), hasher)
        assert equal is True
        assert h1 is not None and h2 is not None
        assert h1 == h2

    def test_different_size(self, tmp_path):
        file1 = tmp_path / "a.txt"
        file2 = tmp_path / "b.txt"
        file1.write_text("Hello")
        file2.write_text("Hello, World!")

        hasher = Hasher("xxh3_64")
        equal, h1, h2 = quick_compare(str(file1), str(file2), hasher)
        assert equal is False
        assert h1 is not None and h2 is not None
        assert h1 != h2

    def test_same_size_different_content(self, tmp_path):
        file1 = tmp_path / "a.txt"
        file2 = tmp_path / "b.txt"
        file1.write_text("Hello")
        file2.write_text("World!")

        hasher = Hasher("xxh3_64")
        equal, h1, h2 = quick_compare(str(file1), str(file2), hasher)
        assert equal is False
        assert h1 is not None and h2 is not None
        assert h1 != h2

    def test_empty_files(self, tmp_path):
        file1 = tmp_path / "empty1.txt"
        file2 = tmp_path / "empty2.txt"
        file1.write_text("")
        file2.write_text("")

        hasher = Hasher("xxh3_64")
        equal, h1, h2 = quick_compare(str(file1), str(file2), hasher)
        assert equal is True
        assert h1 == h2

    def test_nonexistent_file(self, tmp_path):
        hasher = Hasher("xxh3_64")
        equal, h1, h2 = quick_compare(str(tmp_path / "nope"), str(tmp_path / "nope2"), hasher)
        assert equal is False
        assert h1 is None
        assert h2 is None