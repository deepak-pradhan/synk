import tomllib
import tomli_w
import os
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".config" / "beyondcomp"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG = {
    "general": {
        "theme": "light",
        "font_size": 10,
    },
    "comparison": {
        "hash_algorithm": "xxh3_64",
        "context_lines": 3,
    },
    "ignore": {
        "patterns": [".git/", "*.pyc", "__pycache__/", ".DS_Store"],
        "show_identical": True,
    },
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {k: dict(v) for k, v in DEFAULT_CONFIG.items()}
    try:
        with open(CONFIG_FILE, "rb") as f:
            saved = tomllib.load(f)
        config = {k: dict(v) for k, v in DEFAULT_CONFIG.items()}
        for section, values in saved.items():
            if section in config and isinstance(values, dict):
                config[section].update(values)
            else:
                config[section] = values
        return config
    except (tomllib.TOMLDecodeError, OSError):
        return {k: dict(v) for k, v in DEFAULT_CONFIG.items()}


def save_config(config: dict) -> bool:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(CONFIG_FILE, "wb") as f:
            tomli_w.dump(config, f)
        return True
    except OSError:
        return False
