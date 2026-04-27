"""Konfigurations-Verwaltung mit Defaults + User-Override über ~/.config/noten-tools/config.yaml."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path

import yaml

from .paths import config_file, default_logo, default_font


@dataclass
class StampPosition:
    """Stempel-Defaults in Punkten (1 pt = 1/72 inch ≈ 0,353 mm)."""

    logo_left_pt: float = 20.0
    logo_top_pt: float = 0.0
    logo_width_pt: float = 80.0
    logo_height_pt: float = 60.0
    archiv_right_pt: float = 120.0
    archiv_top_pt: float = 40.0
    archiv_font_size_pt: float = 24.0


@dataclass
class Config:
    a5: bool = False
    stamp_enabled_default: bool = True
    ocr_lang: str = "deu+eng"
    ocr_confidence: int = 70
    ocr_dpi: int = 300
    logo_path: str = ""
    font_path: str = ""
    stamp: StampPosition = field(default_factory=StampPosition)

    @classmethod
    def load(cls) -> "Config":
        path = config_file()
        cfg = cls()
        if not cfg.logo_path:
            cfg.logo_path = str(default_logo())
        if not cfg.font_path:
            cfg.font_path = str(default_font())
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            stamp_data = data.pop("stamp", {}) or {}
            for key, value in data.items():
                if hasattr(cfg, key):
                    setattr(cfg, key, value)
            for key, value in stamp_data.items():
                if hasattr(cfg.stamp, key):
                    setattr(cfg.stamp, key, value)
        return cfg

    def save(self) -> None:
        path = config_file()
        data = asdict(self)
        with path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True)

    @staticmethod
    def write_default_if_missing() -> Path:
        path = config_file()
        if path.exists():
            return path
        Config().save()
        return path
