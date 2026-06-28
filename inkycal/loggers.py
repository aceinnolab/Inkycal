"""Logging configuration for Inkycal."""
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

from inkycal.settings import Settings


def _resolve_level(level_name: str) -> int:
    return getattr(logging, level_name.upper(), logging.INFO)


def configure_logging(level_name: Optional[str] = None) -> None:
    """Configure root logging once for CLI, modules and tests."""
    settings = Settings()

    log_dir = os.getenv("INKYCAL_LOG_DIR", settings.LOG_PATH)
    log_file = os.getenv("INKYCAL_LOG_FILE", os.path.join(log_dir, "inkycal.log"))
    log_parent = os.path.dirname(log_file) or "."
    os.makedirs(log_parent, exist_ok=True)

    if level_name is None:
        level_name = os.getenv("INKYCAL_LOG_LEVEL", "INFO")
    level = _resolve_level(level_name)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s: %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(level)

    # Keep setup idempotent when tests or repeated imports call this again.
    existing_handler_names = {getattr(handler, "name", "") for handler in root.handlers}

    if "inkycal_console" not in existing_handler_names:
        stream_handler = logging.StreamHandler()
        stream_handler.set_name("inkycal_console")
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        root.addHandler(stream_handler)

    if "inkycal_file" not in existing_handler_names:
        # Keep one active log plus 14 daily rotations.
        file_handler = TimedRotatingFileHandler(
            log_file,
            when="midnight",
            interval=1,
            backupCount=14,
            encoding="utf-8",
        )
        file_handler.set_name("inkycal_file")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    logging.getLogger("PIL").setLevel(logging.WARNING)


# Keep previous import-side-effect behavior for existing entry points.
configure_logging()


