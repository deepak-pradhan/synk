import tempfile
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.hasher import Hasher, quick_compare


def test_hasher_xxh3_64():
    hasher = Hasher("xxh3_64")
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("Hello, World!")
        fname = f.name
    try:
        hash_val = hasher.hash_file(fname)
        assert isinstance(hash_val, str)
        assert len(hash_val) == 16  # xxh3_64 is 16 hex chars (64 bits)
        # Hash the same content again
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f2:
            f2.write("Hello, World!")
            fname2 = f2.name
        try:
            hash_val2 = hasher.hash_file(fname2)
            assert hash_val == hash_val2
        finally:
            os.unlink(fname2)
        # Different content
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f3:
            f3.write("Hello, Universe!")
            fname3 = f3.name
        try:
            hash_val3 = hasher.hash_file(fname3)
            assert hash_val != hash_val3
        finally:
            os.unlink(fname3)
    finally:
        os.unlink(fname)


def test_quick_compare_equal():
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "test1.txt")
        file2 = os.path.join(tmpdir, "test2.txt")
        with open(file1, "w") as f:
            f.write("Hello, World!")
        with open(file2, "w") as f:
            f.write("Hello, World!")

        hasher = Hasher("xxh3_64")
        equal, h1, h2 = quick_compare(file1, file2, hasher)
        assert equal == True
        assert h1 is not None and h2 is not None
        assert h1 == h2


def test_quick_compare_different_size():
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "test1.txt")
        file2 = os.path.join(tmpdir, "test2.txt")
        with open(file1, "w") as f:
            f.write("Hello")
        with open(file2, "w") as f:
            f.write("Hello, World!")

        hasher = Hasher("xxh3_64")
        equal, h1, h2 = quick_compare(file1, file2, hasher)
        assert equal == False
        # Since sizes differ, we still compute hashes (if size>0)
        assert h1 is not None and h2 is not None
        assert h1 != h2


def test_quick_compare_same_size_different_content():
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "test1.txt")
        file2 = os.path.join(tmpdir, "test2.txt")
        with open(file1, "w") as f:
            f.write("Hello")
        with open(file2, "w") as f:
            f.write("World!")

        hasher = Hasher("xxh3_64")
        equal, h1, h2 = quick_compare(file1, file2, hasher)
        assert equal == False
        assert h1 is not None and h2 is not None
        assert h1 != h2


def test_quick_compare_empty_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "empty1.txt")
        file2 = os.path.join(tmpdir, "empty2.txt")
        open(file1, "w").close()
        open(file2, "w").close()

        hasher = Hasher("xxh3_64")
        equal, h1, h2 = quick_compare(file1, file2, hasher)
        assert equal == True
        # For empty files, hash should be empty string? Actually our hasher will hash empty bytes.
        # xxh3_64 of empty bytes is a constant.
        assert h1 == h2


if __name__ == "__main__":
    test_hasher_xxh3_64()
    test_quick_compare_equal()
    test_quick_compare_different_size()
    test_quick_compare_same_size_different_content()
    test_quick_compare_empty_files()
    print("All tests passed!")
