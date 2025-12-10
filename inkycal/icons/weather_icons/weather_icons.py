import os
import urllib

from PIL import Image


HERE = os.path.dirname(os.path.abspath(__file__))
OWM_ICONS_CACHE = os.path.join(HERE, "owm_icons_cache/")

if not os.path.exists(OWM_ICONS_CACHE):
    os.mkdir(OWM_ICONS_CACHE)


def get_weather_icon(icon_name, size) -> Image:
    """
    Gets the requested weather icon as Image and returns it in the requested size
    :param icon_name:
        icon_name for the weather
    :param size:
        size of the icon in pixels
    :return:
        the resized weather icon
    """

    iconpath = os.path.join(OWM_ICONS_CACHE, f"{icon_name}.png")

    if not os.path.exists(iconpath):
        urllib.request.urlretrieve(url=f"https://openweathermap.org/img/wn/{icon_name}@2x.png", filename=f"{iconpath}")
    icon = Image.open(iconpath)

    icon = icon.resize((size, size))

    return icon
