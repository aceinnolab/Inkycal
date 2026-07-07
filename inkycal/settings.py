"""Settings class
Used to initialize the settings for the application.
"""
import json
import os

basedir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(basedir, os.pardir))


class Settings:
    """Settings class to initialize the settings for the application."""
    CACHE_PATH = os.path.join(basedir, "cache")
    LOG_PATH = os.path.join(project_root, "logs")
    FONT_PATH = os.path.join(basedir, "fonts")
    IMAGE_FOLDER = os.path.join(basedir, "image_folder")
    PARALLEL_DRIVER_PATH = os.path.join(basedir, "display", "drivers", "parallel_drivers")
    TEMPORARY_FOLDER = os.path.join(basedir, "tmp")
    VCOM = "2.0"
    # /boot/settings.json is path on older releases, while the latter is more the more recent ones
    SETTINGS_JSON_PATHS = ["/boot/settings.json", "/boot/firmware/settings.json"]

    def __init__(self):
        self.VCOM = self._load_vcom()

    @classmethod
    def _settings_file(cls) -> str | None:
        for path in cls.SETTINGS_JSON_PATHS:
            if os.path.exists(path):
                return path
        return None

    def _load_vcom(self) -> str:
        settings_file = self._settings_file()
        if not settings_file:
            return type(self).VCOM

        try:
            with open(settings_file, mode="r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return type(self).VCOM

        value = data.get("vcom", data.get("VCOM", type(self).VCOM))
        return str(value)
