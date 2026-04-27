"""Logger zu Konsole (rich) + rotierendem Logfile in ~/.cache/noten-tools/logs/."""

from __future__ import annotations

import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

from rich.logging import RichHandler

from .paths import log_dir


def setup_logger(verbose: bool = False, quiet: bool = False, name: str = "noten-tools") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    console_level = logging.WARNING if quiet else (logging.DEBUG if verbose else logging.INFO)
    console = RichHandler(
        level=console_level,
        show_time=False,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    console.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console)

    timestamp = datetime.now().strftime("%Y-%m-%d")
    logfile = log_dir() / f"{timestamp}.log"
    file_handler = RotatingFileHandler(logfile, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger
