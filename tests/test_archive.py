import os
import zipfile
import tarfile

import pytest

from src.core.archive import (
    detect_archive_type,
    is_archive,
    list_archive,
    extract_file,
    get_archive_top_dirs,
    list_archive_at_depth,
    ArchiveEntry,
)


class TestDetectArchiveType:
    def test_zip(self):
        assert detect_archive_type("file.zip") == "zip"

    def test_tar(self):
        assert detect_archive_type("file.tar") == "tar"

    def test_tar_gz(self):
        assert detect_archive_type("file.tar.gz") == "tar"

    def test_tgz(self):
        assert detect_archive_type("file.tgz") == "tar"

    def test_tar_bz2(self):
        assert detect_archive_type("file.tar.bz2") == "tar"

    def test_tar_xz(self):
        assert detect_archive_type("file.tar.xz") == "tar"

    def test_non_archive(self):
        assert detect_archive_type("file.txt") is None

    def test_python_file(self):
        assert detect_archive_type("script.py") is None


class TestIsArchive:
    def test_zip(self, tmp_path):
        p = tmp_path / "test.zip"
        with zipfile.ZipFile(str(p), "w") as zf:
            zf.writestr("hello.txt", "hello")
        assert is_archive(str(p)) is True

    def test_regular_file(self, tmp_path):
        p = tmp_path / "test.txt"
        p.write_text("hello")
        assert is_archive(str(p)) is False


class TestListArchive:
    def test_list_zip(self, tmp_path):
        p = tmp_path / "test.zip"
        with zipfile.ZipFile(str(p), "w") as zf:
            zf.writestr("dir/subdir/file.txt", "content")
            zf.writestr("root.txt", "root content")
        entries = list_archive(str(p))
        names = [e.name for e in entries]
        assert "root.txt" in names
        assert any("dir" in n for n in names)

    def test_list_tar_gz(self, tmp_path):
        p = tmp_path / "test.tar.gz"
        # Create a tar.gz with some files
        inner = tmp_path / "inner"
        inner.mkdir()
        (inner / "a.txt").write_text("aaa")
        subdir = inner / "sub"
        subdir.mkdir()
        (subdir / "b.txt").write_text("bbb")
        with tarfile.open(str(p), "w:gz") as tf:
            tf.add(str(inner / "a.txt"), arcname="a.txt")
            tf.add(str(subdir / "b.txt"), arcname="sub/b.txt")
        entries = list_archive(str(p))
        names = [e.name for e in entries]
        assert "a.txt" in names
        assert "sub/b.txt" in names

    def test_list_empty_zip(self, tmp_path):
        p = tmp_path / "empty.zip"
        with zipfile.ZipFile(str(p), "w") as zf:
            pass
        entries = list_archive(str(p))
        assert entries == []

    def test_list_nonexistent(self, tmp_path):
        entries = list_archive(str(tmp_path / "nope.zip"))
        assert entries == []


class TestListArchiveAtDepth:
    def test_top_level(self, tmp_path):
        p = tmp_path / "test.zip"
        with zipfile.ZipFile(str(p), "w") as zf:
            zf.writestr("src/main.py", "code")
            zf.writestr("src/utils/helper.py", "code")
            zf.writestr("README.md", "readme")
        entries = list_archive_at_depth(str(p))
        names = [e.name for e in entries]
        assert any("src" in n for n in names)
        assert "README.md" in names

    def test_sub_level(self, tmp_path):
        p = tmp_path / "test.zip"
        with zipfile.ZipFile(str(p), "w") as zf:
            zf.writestr("src/main.py", "code")
            zf.writestr("src/utils/helper.py", "code")
        entries = list_archive_at_depth(str(p), "src")
        names = [e.name for e in entries]
        assert any("main.py" in n or "main" in n for n in names)
        assert any("utils" in n for n in names)


class TestExtractFile:
    def test_extract_from_zip(self, tmp_path):
        p = tmp_path / "test.zip"
        with zipfile.ZipFile(str(p), "w") as zf:
            zf.writestr("hello.txt", "hello world")
        dest = tmp_path / "out"
        dest.mkdir()
        result = extract_file(str(p), "hello.txt", str(dest))
        assert result is not None
        assert os.path.exists(result)
        with open(result) as f:
            assert f.read() == "hello world"

    def test_extract_nonexistent_entry(self, tmp_path):
        p = tmp_path / "test.zip"
        with zipfile.ZipFile(str(p), "w") as zf:
            zf.writestr("hello.txt", "hello")
        dest = tmp_path / "out"
        dest.mkdir()
        result = extract_file(str(p), "nonexistent.txt", str(dest))
        assert result is None


class TestGetArchiveTopDirs:
    def test_top_dirs(self, tmp_path):
        p = tmp_path / "test.zip"
        with zipfile.ZipFile(str(p), "w") as zf:
            zf.writestr("src/a.py", "a")
            zf.writestr("docs/readme.md", "r")
            zf.writestr("top.txt", "t")
        dirs = get_archive_top_dirs(str(p))
        assert "src" in dirs
        assert "docs" in dirs