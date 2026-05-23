import tomllib
import tomli_w
import os
from pathlib import Path
from typing import Optional

SESSION_DIR = Path.home() / ".config" / "beyondcomp"
LAST_SESSION_FILE = SESSION_DIR / "last_session.toml"


def save_session(file_path: str, data: dict) -> bool:
    try:
        with open(file_path, "wb") as f:
            tomli_w.dump(data, f)
        return True
    except OSError:
        return False


def load_session(file_path: str) -> Optional[dict]:
    try:
        with open(file_path, "rb") as f:
            return tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError, FileNotFoundError):
        return None


def save_last_session(left_path: str, right_path: str, config: dict) -> bool:
    data = {
        "left_path": left_path,
        "right_path": right_path,
        "hash_algorithm": config.get("comparison", {}).get("hash_algorithm", "xxh3_64"),
        "ignore_patterns": config.get("ignore", {}).get("patterns", []),
        "show_identical": config.get("ignore", {}).get("show_identical", True),
    }
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    return save_session(str(LAST_SESSION_FILE), data)


def load_last_session() -> Optional[dict]:
    if not LAST_SESSION_FILE.exists():
        return None
    return load_session(str(LAST_SESSION_FILE))


def clear_last_session():
    if LAST_SESSION_FILE.exists():
        LAST_SESSION_FILE.unlink()
