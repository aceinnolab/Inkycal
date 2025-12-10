"""enums.py"""
import os
from enum import Enum

from inkycal.settings import Settings

settings = Settings()

class FONTS(str, Enum):
    # material icons
    material_icons = os.path.join(settings.FONT_PATH, "MaterialIcons", "MaterialIcons.ttf")

    # noto sans
    noto_sans_semicondensed = os.path.join(settings.FONT_PATH, "NotoSans", "NotoSans-SemiCondensed.ttf")
    noto_sans_semicondensed_medium = os.path.join(settings.FONT_PATH, "NotoSans", "NotoSans-SemiCondensedMedium.ttf")
    noto_sans_semicondensed_semibold = os.path.join(settings.FONT_PATH, "NotoSans", "NotoSans-SemiCondensedSemiBold.ttf")

    # noto cjk (support for chinese, korean, japanese)
    noto_sans_cjk_bold = os.path.join(settings.FONT_PATH, "NotoSansCJK", "NotoSansCJKsc-Bold.otf")
    noto_sans_cjk_medium = os.path.join(settings.FONT_PATH, "NotoSansCJK", "NotoSansCJKsc-Medium.otf")
    noto_sans_cjk_regular = os.path.join(settings.FONT_PATH, "NotoSansCJK", "NotoSansCJKsc-Regular.otf")

    # noto sans ui
    noto_sans_ui_bold = os.path.join(settings.FONT_PATH, "NotoSansUI", "NotoSansUI-Bold.ttf")
    noto_sans_ui_regular = os.path.join(settings.FONT_PATH, "NotoSansUI", "NotoSansUI-Regular.ttf")

    # weather icons
    weather_icons = os.path.join(settings.FONT_PATH, "WeatherFont", "weathericons-regular-webfont.ttf")

    # default
    default = noto_sans_semicondensed_medium