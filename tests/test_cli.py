import sys
from pathlib import Path
import tempfile


def test_cli_file_diff(tmp_path):
    """Test CLI file diff on identical files."""
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("hello world")
    f2.write_text("hello world")

    from src.cli import do_file_diff
    code = do_file_diff(str(f1), str(f2))
    assert code == 0


def test_cli_file_diff_different(tmp_path, capsys):
    """Test CLI file diff on different files."""
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("hello world")
    f2.write_text("hello mars")

    from src.cli import do_file_diff
    code = do_file_diff(str(f1), str(f2))
    assert code == 1


def test_cli_dir_diff(tmp_path):
    """Test CLI directory diff on identical dirs."""
    d1 = tmp_path / "dir1"
    d2 = tmp_path / "dir2"
    d1.mkdir()
    d2.mkdir()
    (d1 / "file.txt").write_text("content")
    (d2 / "file.txt").write_text("content")

    from src.cli import do_dir_diff
    code = do_dir_diff(str(d1), str(d2))
    assert code == 0


def test_cli_hash(tmp_path):
    """Test CLI hash command."""
    f = tmp_path / "file.txt"
    f.write_text("content")

    from src.cli import do_hash
    code = do_hash([str(f)], "xxh3_64")
    assert code == 0
