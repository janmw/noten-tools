"""Pfad-Auflösung für noten-tools (Repo-Daten + User-Config + Cache)."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from platformdirs import user_cache_dir, user_config_dir

APP_NAME = "noten-tools"


def config_dir() -> Path:
    p = Path(user_config_dir(APP_NAME))
    p.mkdir(parents=True, exist_ok=True)
    return p


def cache_dir() -> Path:
    p = Path(user_cache_dir(APP_NAME))
    p.mkdir(parents=True, exist_ok=True)
    return p


def log_dir() -> Path:
    p = cache_dir() / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def config_file() -> Path:
    return config_dir() / "config.yaml"


def learned_aliases_file() -> Path:
    return config_dir() / "learned_aliases.yaml"


def repo_root() -> Path:
    """Sucht das Repo-Wurzelverzeichnis (für Entwicklungs-Modus mit data/ und assets/)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "data").is_dir() and (parent / "assets").is_dir():
            return parent
    return here.parents[2]


def instruments_yaml() -> Path:
    return repo_root() / "data" / "instruments.yaml"


def default_logo() -> Path:
    return repo_root() / "assets" / "logo.png"


def default_font() -> Path:
    return repo_root() / "assets" / "00_stamp.ttf"


def default_mono_font() -> Path:
    return repo_root() / "assets" / "JetBrainsMono-Regular.ttf"
