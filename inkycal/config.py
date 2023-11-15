"""
Inkycal config file
Contains paths and variables used throughout Inkycal.
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    FONT_DIR = f"{basedir}/fonts"
    FONT_PROFONT_PATH = f"{FONT_DIR}/ProFont/ProFont.ttf"
    FONT_NOTOSANS_UI_REGULAR_PATH = f"{FONT_DIR}/NotoSansUI/NotoSansUI-Regular.ttf"
    FONT_NOTOSANS_UI_BOLD_PATH = f"{FONT_DIR}/NotoSansUI/NotoSansUI-Bold.ttf"
    FONT_WEATHER_ICONS_PATH =  f"{FONT_DIR}/WeatherFont/weathericons-regular-webfont.ttf"

    DISPlAY_DRIVERS_PATH = f"{basedir}/display/drivers"

    LOG_DIRECTORY = f"{basedir}/logs"
    IMAGE_FOLDER = f"{basedir}/images"
