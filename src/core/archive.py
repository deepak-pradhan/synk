import zipfile
import tarfile
import os
from dataclasses import dataclass
from typing import Optional

ARCHIVE_EXTENSIONS = {
    ".zip": "zip",
    ".tar": "tar",
    ".tar.gz": "tar",
    ".tgz": "tar",
    ".tar.bz2": "tar",
    ".tbz2": "tar",
    ".tar.xz": "tar",
    ".txz": "tar",
    ".tar.zst": "tar",
}


@dataclass
class ArchiveEntry:
    name: str
    size: int
    mtime: float
    is_dir: bool


def detect_archive_type(path: str) -> Optional[str]:
    """Return 'zip', 'tar', or None based on file extension."""
    lower = path.lower()
    for ext, kind in sorted(ARCHIVE_EXTENSIONS.items(), key=lambda kv: -len(kv[0])):
        if lower.endswith(ext):
            return kind
    return None


def is_archive(path: str) -> bool:
    return detect_archive_type(path) is not None


def list_archive(path: str) -> list[ArchiveEntry]:
    """List entries in an archive file. Returns a list of ArchiveEntry."""
    kind = detect_archive_type(path)
    if kind == "zip":
        return _list_zip(path)
    elif kind == "tar":
        return _list_tar(path)
    return []


def _list_zip(path: str) -> list[ArchiveEntry]:
    entries = []
    try:
        with zipfile.ZipFile(path, "r") as zf:
            for info in zf.infolist():
                name = info.filename
                if name.endswith("/"):
                    is_dir = True
                    name = name.rstrip("/")
                else:
                    is_dir = False
                if not name:
                    continue
                basename = os.path.basename(name)
                if not basename:
                    continue
                entries.append(ArchiveEntry(
                    name=name,
                    size=info.file_size,
                    mtime=info.date_time if isinstance(info.date_time, (int, float)) else 0.0,
                    is_dir=is_dir,
                ))
    except (zipfile.BadZipFile, OSError):
        pass
    return entries


def _list_tar(path: str) -> list[ArchiveEntry]:
    entries = []
    try:
        with tarfile.open(path, "r:*") as tf:
            for member in tf.getmembers():
                name = member.name
                if not name or name == ".":
                    continue
                entries.append(ArchiveEntry(
                    name=name,
                    size=member.size,
                    mtime=member.mtime if member.mtime else 0.0,
                    is_dir=member.isdir(),
                ))
    except (tarfile.TarError, OSError, EOFError):
        pass
    return entries


def extract_file(archive_path: str, entry_name: str, dest_dir: str) -> Optional[str]:
    """Extract a single file from an archive to dest_dir. Returns the extracted path or None."""
    kind = detect_archive_type(archive_path)
    if kind == "zip":
        return _extract_zip_file(archive_path, entry_name, dest_dir)
    elif kind == "tar":
        return _extract_tar_file(archive_path, entry_name, dest_dir)
    return None


def _extract_zip_file(archive_path: str, entry_name: str, dest_dir: str) -> Optional[str]:
    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extract(entry_name, dest_dir)
            return os.path.join(dest_dir, entry_name)
    except (KeyError, zipfile.BadZipFile, OSError):
        return None


def _extract_tar_file(archive_path: str, entry_name: str, dest_dir: str) -> Optional[str]:
    try:
        with tarfile.open(archive_path, "r:*") as tf:
            member = tf.getmember(entry_name)
            tf.extract(member, dest_dir, filter="data")
            return os.path.join(dest_dir, member.name)
    except (KeyError, tarfile.TarError, OSError):
        return None


def get_archive_top_dirs(path: str) -> list[str]:
    """Get the top-level directory names inside an archive (for navigating into it)."""
    entries = list_archive(path)
    top = set()
    for e in entries:
        parts = e.name.split("/")
        top.add(parts[0])
    return sorted(top)


def list_archive_at_depth(path: str, prefix: str = "") -> list[ArchiveEntry]:
    """List entries at a given prefix depth inside the archive.
    If prefix is empty, returns top-level entries.
    If prefix is 'src/', returns entries directly under 'src/'.
    """
    entries = list_archive(path)
    result = []
    seen = set()
    prefix = prefix.rstrip("/")

    for entry in entries:
        if prefix and not entry.name.startswith(prefix + "/"):
            continue
        remainder = entry.name[len(prefix) + 1:] if prefix else entry.name
        if not remainder:
            continue
        top = remainder.split("/")[0]
        key = (prefix + "/" + top) if prefix else top
        if key in seen:
            continue
        seen.add(key)

        if "/" in remainder:
            is_dir = True
        else:
            is_dir = entry.is_dir

        result.append(ArchiveEntry(
            name=key,
            size=entry.size if not is_dir else 0,
            mtime=entry.mtime,
            is_dir=is_dir,
        ))
    return result