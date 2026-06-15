import os
import tempfile


def test_cli_merge_no_conflict():
    """Test CLI 3-way merge with non-overlapping changes — clean output."""
    from src.cli import do_merge
    base = "line1\nline2\nline3"
    local = "line1\nline2 LOCAL\nline3"
    remote = "line1\nline2\nline3 REMOTE"

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        base_path = f.name
        f.write(base)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        local_path = f.name
        f.write(local)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        remote_path = f.name
        f.write(remote)

    try:
        code = do_merge(base_path, local_path, remote_path, output=None, use_gui=False)
        assert code == 0
    finally:
        os.unlink(base_path)
        os.unlink(local_path)
        os.unlink(remote_path)


def test_cli_merge_conflict():
    """Test CLI 3-way merge with conflict — exit code 1."""
    from src.cli import do_merge
    base = "line1\nline2\nline3"
    local = "line1\nline2 LOCAL\nline3"
    remote = "line1\nline2 REMOTE\nline3"

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        base_path = f.name
        f.write(base)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        local_path = f.name
        f.write(local)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        remote_path = f.name
        f.write(remote)

    try:
        code = do_merge(base_path, local_path, remote_path, output=None, use_gui=False)
        assert code == 1
    finally:
        os.unlink(base_path)
        os.unlink(local_path)
        os.unlink(remote_path)


def test_cli_merge_output_file():
    """Test CLI 3-way merge writing to output file."""
    from src.cli import do_merge
    base = "line1\nline2\nline3"
    local = "line1\nline2\nline3"
    remote = "line1\nline2\nline3"

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        base_path = f.name
        f.write(base)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        local_path = f.name
        f.write(local)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        remote_path = f.name
        f.write(remote)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        out_path = f.name

    try:
        code = do_merge(base_path, local_path, remote_path, output=out_path, use_gui=False)
        assert code == 0
        with open(out_path, "r") as f:
            content = f.read()
        assert "line1" in content
    finally:
        os.unlink(base_path)
        os.unlink(local_path)
        os.unlink(remote_path)
        os.unlink(out_path)
