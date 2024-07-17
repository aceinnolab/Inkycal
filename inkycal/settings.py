"""Settings class
Used to initialize the settings for the application.
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Settings:
    """Settings class to initialize the settings for the application.

    """
    CACHE_PATH = os.path.join(basedir, "cache")
    LOG_PATH = os.path.join(basedir, "../logs")
    INKYCAL_LOG_PATH = os.path.join(LOG_PATH, "inkycal.log")
    FONT_PATH = os.path.join(basedir, "../fonts")
    IMAGE_FOLDER = os.path.join(basedir, "../image_folder")
    PARALLEL_DRIVER_PATH = os.path.join(basedir, "display", "drivers", "parallel_drivers")
    TEMPORARY_FOLDER = os.path.join(basedir, "tmp")
    VCOM = "2.0"
    # /boot/settings.json is path on older releases, while the latter is more the more recent ones
    SETTINGS_JSON_PATHS = ["/boot/settings.json", "/boot/firmware/settings.json"]
