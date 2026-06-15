#!/usr/bin/env python3
"""
Synk CLI — Headless file/folder comparison utility.

Usage:
    synk diff file1.txt file2.txt
    synk diff dir1/ dir2/
    synk hash file1.txt [file2.txt ...]
    synk compare --hash-algo xxh3_64 dir1/ dir2/
"""

import argparse
import sys
import os
from pathlib import Path

from src.core.hasher import Hasher
from src.core.merge import three_way_merge
from diff_match_patch import diff_match_patch


def print_diff(text1: str, text2: str) -> None:
    """Print inline diff of two text files."""
    dmp = diff_match_patch()
    diffs = dmp.diff_main(text1, text2)
    dmp.diff_cleanupSemantic(diffs)

    for op, text in diffs:
        if op == -1:
            print(f"\033[91m{text}\033[0m", end="")  # deleted (red)
        elif op == 1:
            print(f"\033[92m{text}\033[0m", end="")  # inserted (green)
        else:
            print(text, end="")
    print()


def do_file_diff(path1: str, path2: str) -> int:
    """Compare two files and print diff. Returns exit code."""
    # Handle SFTP URLs
    text1 = _read_text(path1)
    text2 = _read_text(path2)

    if text1 is None:
        print(f"Error: Cannot read {path1}", file=sys.stderr)
        return 1
    if text2 is None:
        print(f"Error: Cannot read {path2}", file=sys.stderr)
        return 1

    if text1 == text2:
        print("Files are identical.")
        return 0

    print_diff(text1, text2)
    return 1


def _read_text(path: str) -> str | None:
    """Read text from local path."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def do_dir_diff(dir1: str, dir2: str, hash_algo: str = "xxh3_64") -> int:
    """Compare two directories and summarize differences."""
    hasher = Hasher(hash_algo)
    p1 = Path(dir1)
    p2 = Path(dir2)

    if not p1.is_dir():
        print(f"Error: Not a directory: {dir1}", file=sys.stderr)
        return 1
    if not p2.is_dir():
        print(f"Error: Not a directory: {dir2}", file=sys.stderr)
        return 1

    files1 = {f.relative_to(p1).as_posix(): f for f in p1.rglob("*") if f.is_file() and not f.name.startswith(".")}
    files2 = {f.relative_to(p2).as_posix(): f for f in p2.rglob("*") if f.is_file() and not f.name.startswith(".")}

    all_files = sorted(set(files1.keys()) | set(files2.keys()))
    identical = 0
    different = 0
    left_only = 0
    right_only = 0

    for rel in all_files:
        if rel in files1 and rel in files2:
            h1 = hasher.hash_file(str(files1[rel]))
            h2 = hasher.hash_file(str(files2[rel]))
            if h1 == h2:
                identical += 1
                print(f"  = {rel}")
            else:
                different += 1
                print(f"  ≠ {rel}")
        elif rel in files1:
            left_only += 1
            print(f"  < {rel}")
        else:
            right_only += 1
            print(f"  > {rel}")

    print(f"\nSummary: {identical} identical, {different} different, {left_only} left-only, {right_only} right-only")
    return 0 if different == 0 and left_only == 0 and right_only == 0 else 1


def do_hash(paths: list[str], algo: str = "xxh3_64") -> int:
    """Print hashes of given files."""
    hasher = Hasher(algo)
    for path in paths:
        if not os.path.isfile(path):
            print(f"Error: Not a file: {path}", file=sys.stderr)
            continue
        h = hasher.hash_file(path)
        print(f"{h}  {path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Synk — headless file/folder comparison")
    subparsers = parser.add_subparsers(dest="command")

    # diff
    diff_parser = subparsers.add_parser("diff", help="Compare files or directories")
    diff_parser.add_argument("path1")
    diff_parser.add_argument("path2")
    diff_parser.add_argument("--hash-algo", default="xxh3_64", choices=["xxh3_64", "xxh64", "md5", "sha1", "sha256"])

    # hash
    hash_parser = subparsers.add_parser("hash", help="Hash files")
    hash_parser.add_argument("paths", nargs="+")
    hash_parser.add_argument("--algo", default="xxh3_64", choices=["xxh3_64", "xxh64", "md5", "sha1", "sha256"])

    # merge
    merge_parser = subparsers.add_parser("merge", help="3-way merge of base, local, remote files")
    merge_parser.add_argument("base")
    merge_parser.add_argument("local")
    merge_parser.add_argument("remote")
    merge_parser.add_argument("--output", "-o", help="Write merged result to file (default: stdout)")
    merge_parser.add_argument("--gui", action="store_true", help="Launch GUI merge dialog (requires display)")

    args = parser.parse_args()

    if args.command == "diff":
        if os.path.isdir(args.path1) or os.path.isdir(args.path2):
            return do_dir_diff(args.path1, args.path2, args.hash_algo)
        return do_file_diff(args.path1, args.path2)
    elif args.command == "hash":
        return do_hash(args.paths, args.algo)
    elif args.command == "merge":
        return do_merge(args.base, args.local, args.remote, args.output, args.gui)
    else:
        parser.print_help()
        return 1


def do_merge(base_path: str, local_path: str, remote_path: str, output: str | None, use_gui: bool) -> int:
    """Perform a 3-way merge and output result."""
    base_text = _read_text(base_path)
    local_text = _read_text(local_path)
    remote_text = _read_text(remote_path)

    if base_text is None:
        print(f"Error: Cannot read base: {base_path}", file=sys.stderr)
        return 1
    if local_text is None:
        print(f"Error: Cannot read local: {local_path}", file=sys.stderr)
        return 1
    if remote_text is None:
        print(f"Error: Cannot read remote: {remote_path}", file=sys.stderr)
        return 1

    if use_gui:
        from PySide6.QtWidgets import QApplication
        from src.ui.merge_dialog import MergeDialog
        app = QApplication.instance() or QApplication(sys.argv)
        dialog = MergeDialog(base_text, local_text, remote_text,
                             base_label=base_path, local_label=local_path, remote_label=remote_path)
        dialog.exec()
        if dialog.result is not None:
            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(dialog.result)
                print(f"Merge written to {output}")
            else:
                print(dialog.result)
            return 0
        return 1

    result = three_way_merge(base_text, local_text, remote_text)
    text = result.to_text()

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Merge written to {output}")
    else:
        print(text)

    return 1 if result.has_conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
