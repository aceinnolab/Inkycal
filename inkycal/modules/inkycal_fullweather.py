"""
Inkycal fullscreen weather module
Copyright by mrbwburns
"""
import locale
import logging
import math
import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

from icons.weather_icons.weather_icons import get_weather_icon
from inkycal.custom import owm_forecasts
from inkycal.custom.functions import fonts
from inkycal.custom.functions import internet_available
from inkycal.custom.functions import top_level
from inkycal.custom.inkycal_exceptions import NetworkNotReachableError
from inkycal.modules.template import inkycal_module

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

icons_dir = os.path.join(top_level, "icons", "ui-icons")


def outline(image: Image, size: int, color: tuple) -> Image:
    # Create a canvas for the outline image
    outlined = Image.new("RGBA", image.size, (0, 0, 0, 0))

    # Make a black outline
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.getpixel((x, y))
            if pixel[0] != 0 or pixel[1] != 0 or pixel[2] != 0:
                outlined.putpixel((x, y), color)

    # Enlarge the outlined image, and paste the original image on top to create a shadow effect
    outlined = outlined.resize((outlined.width + size, outlined.height + size))
    paste_position = ((outlined.width - image.width) // 2, (outlined.height - image.height) // 2)
    outlined.paste(image, paste_position, image)

    # Create a mask to prevent transparent pixels from overwriting
    mask = Image.new("L", outlined.size, 255)
    outlined = Image.composite(outlined, Image.new("RGBA", outlined.size, (0, 0, 0, 0)), mask)

    return outlined


class Fullweather(inkycal_module):
    """Fullscreen Weather class
    gets weather details from openweathermap and plots a nice fullscreen forecast picture
    """

    name = "Fullscreen weather (openweathermap) - Get weather forecasts from openweathermap"

    requires = {
        "api_key": {
            "label": "Please enter openweathermap api-key. You can create one for free on openweathermap",
        },
        "location": {
            "label": "Please enter your location ID found in the url "
            + "e.g. https://openweathermap.org/city/4893171 -> ID is 4893171"
        },
    }

    optional = {
        "temp_units": {
            "label": "Which temperature unit should be used?",
            "options": ["celsius", "fahrenheit"],
        },
        "wind_units": {
            "label": "Which wind speed unit should be used?",
            "options": ["beaufort", "knots", "miles_hour", "km_hour", "meters_sec"],
        },
        "wind_gusts": {
            "label": "Should current wind gust speed also be displayed?",
            "options": [True, False],
        },
        "keep_history": {
            "label": "Should the weather data be written to local json files (one per query)?",
            "options": [True, False],
        },
        "min_max_annotations": {
            "label": "Should the temperature plot have min/max annotation labels?",
            "options": [True, False],
        },
        "locale": {
            "label": "Your locale",
            "options": ["de_DE.UTF-8", "en_GB.UTF-8"],
        },
        "tz": {
            "label": "Your timezone",
            "options": ["Europe/Berlin", "UTC"],
        },
        "font_family": {
            "label": "Font family to use for the entire screen",
            "options": ["Roboto", "NotoSans", "Poppins"],
        },
        "chart_title": {
            "label": "Title of the temperature and precipitation plot",
            "options": ["Temperatur und Niederschlag", "Temperature and precipitation"],
        },
        "weekly_title": {
            "label": "Title of the weekly weather forecast",
            "options": ["Tageswerte", "Weekly forecast"],
        },
        "icon_outline": {
            "label": "Should the weather icons have outlines?",
            "options": [True, False],
        },
    }

    def __init__(self, config):
        """Initialize inkycal_weather module"""

        super().__init__(config)

        config = config["config"]

        # Check if all required parameters are present
        for param in self.requires:
            if not param in config:
                raise Exception(f"config is missing {param}")

        # required parameters
        self.api_key = config["api_key"]
        self.location = int(config["location"])
        self.font_size = int(config["fontsize"])

        # optional parameters
        if "wind_units" in config:
            self.wind_units = config["wind_units"]
        else:
            self.wind_units = "meters_sec"
        if self.wind_units == "beaufort":
            self.windDispUnit = "bft"
        elif self.wind_units == "knots":
            self.windDispUnit = "kn"
        elif self.wind_units == "km_hour":
            self.windDispUnit = "km/h"
        elif self.wind_units == "miles_hour":
            self.windDispUnit = "mph"
        else:
            self.windDispUnit = "m/s"

        if "wind_gusts" in config:
            self.wind_gusts = bool(config["wind_gusts"])
        else:
            self.wind_gusts = True

        if "temp_units" in config:
            self.temp_units = config["temp_units"]
        else:
            self.temp_units = "celsius"
        if self.temp_units == "fahrenheit":
            self.tempDispUnit = "F"
        elif self.temp_units == "celsius":
            self.tempDispUnit = "°"

        if "weekly_title" in config:
            self.weekly_title = config["weekly_title"]
        else:
            self.weekly_title = "Weekly forecast"

        if "chart_title" in config:
            self.chart_title = config["chart_title"]
        else:
            self.chart_title = "Temperature and precipitation"

        if "keep_history" in config:
            self.keep_history = config["keep_history"]
        else:
            self.keep_history = False

        if "min_max_annotations" in config:
            self.min_max_annotations = bool(config["min_max_annotations"])
        else:
            self.min_max_annotations = False

        if "locale" in config:
            self.locale = config["locale"]
        else:
            self.locale = "en_GB.UTF-8"
        locale.setlocale(locale.LC_TIME, self.locale)
        self.language = self.locale.split("_")[0]

        if "tz" in config:
            self.tz = config["tz"]
        else:
            self.tz = "UTC"

        if "icon_outline" in config:
            self.icon_outline = config["icon_outline"]
        else:
            self.icon_outline = True

        if "font_family" in config:
            self.font_family = config["font_family"]
        else:
            self.font_family = "Roboto"

        # some calculations for scalability
        # TODO: make this work for all sizes
        self.screen_width_in = 163 / 25.4  # 163 mm for 7in5
        self.screen_height_in = 98 / 25.4  # 98 mm for 7in5
        self.dpi = math.sqrt(
            (float(self.width) ** 2 + float(self.height) ** 2)
            / (self.screen_width_in**2 + self.screen_height_in**2)
        )
        self.left_section_width = int(self.width / 4)

        # give an OK message
        print(f"{__name__} loaded")

    def createBaseImage(self):
        """
        Creates background and adds current date
        """
        # Create white image
        self.image = Image.new("RGB", (self.width, self.height), (255, 255, 255))
        image_draw = ImageDraw.Draw(self.image)

        # Create black rectangle for the current weather section
        rect_width = int(self.width / 4)
        image_draw.rectangle((0, 0, rect_width, self.height), fill=0)

        # Add text with current date
        now = datetime.now()
        dateString = now.strftime("%d. %B")
        dateFont = self.get_font(family=self.font_family, style="Bold", size=self.font_size)
        # Get the width of the text
        dateStringbbox = dateFont.getbbox(dateString)
        dateW = dateStringbbox[2] - dateStringbbox[0]
        # Draw the current date centered
        image_draw.text(((rect_width - dateW) / 2, 5), dateString, font=dateFont, fill=(255, 255, 255))

    def addUserSection(self):
        """
        Adds user-defined section to the given image
        """
        ## Create drawing object for image
        image_draw = ImageDraw.Draw(self.image)

        if False:  # self.mqtt_sub == True:
            # Add icon for Home
            homeTempIcon = Image.open(os.path.join(icons_dir, "home_temp.png"))
            homeTempIcon = ImageOps.invert(homeTempIcon)
            homeTempIcon = homeTempIcon.resize((40, 40))
            homeTemp_y = int(self.height * 0.8125)
            self.image.paste(homeTempIcon, (15, homeTemp_y))

            # Home temperature
            # my_home = mqtt_temperature(host=mqtt_host, port=mqtt_port, user=mqtt_user, password=mqtt_pass, topic=mqtt_topic)
            # homeTemp = None
            # while homeTemp == None:
            #    homeTemp = my_home.get_temperature()
            # homeTempString = f"{homeTemp:.1f} {tempDispUnit}"
            # homeTempFont = font.font(font_family, "Bold", 28)
            # image_draw.text((65, homeTemp_y), homeTempString, font=homeTempFont, fill=(255, 255, 255))

            # Add icon for rH
            humidityIcon = Image.open(os.path.join(icons_dir, "humidity.bmp"))
            humidityIcon = humidityIcon.resize((40, 40))
            humidity_y = int(self.height * 0.90625)
            self.image.paste(humidityIcon, (15, humidity_y))

            # rel. humidity
            # rH = None
            # while rH == None:
            #    rH = my_home.get_rH()
            # humidityString = f"{rH:.0f} %"
            # humidityFont = font.font(font_family, "Bold", 28)
            # image_draw.text((65, humidity_y), humidityString, font=humidityFont, fill=(255, 255, 255))
        else:
            # Add icon for Humidity
            humidityIcon = Image.open(os.path.join(icons_dir, "humidity.bmp"))
            humidityIcon = humidityIcon.resize((40, 40))
            humidity_y = int(self.height * 0.8125)
            self.image.paste(humidityIcon, (15, humidity_y))

            # Humidity
            humidityString = f"{self.current_weather.humidity} %"
            humidityFont = self.get_font(self.font_family, "Bold", 28)
            image_draw.text((65, humidity_y), humidityString, font=humidityFont, fill=(255, 255, 255))

            # Add icon for uv
            uvIcon = Image.open(os.path.join(icons_dir, "uv.bmp"))
            uvIcon = uvIcon.resize((40, 40))
            ux_y = int(self.height * 0.90625)
            self.image.paste(uvIcon, (15, ux_y))

            # uvindex
            uvString = f"{self.current_weather.uvi if self.current_weather.uvi else '0'}"
            uvFont = self.get_font(self.font_family, "Bold", 28)
            image_draw.text((65, ux_y), uvString, font=uvFont, fill=(255, 255, 255))

    def addCurrentWeather(self):
        """
        Adds current weather situation to the left section of the image
        """
        ## Create drawing object for image
        image_draw = ImageDraw.Draw(self.image)

        ## Add detailed weather status text to the image
        sumString = self.current_weather.detailed_status.replace(" ", "\n ")
        sumFont = self.get_font(self.font_family, "Regular", self.font_size + 8)
        maxW = 0
        totalH = 0
        for word in sumString.split("\n "):
            sumStringbbox = sumFont.getbbox(word)
            sumW = sumStringbbox[2] - sumStringbbox[0]
            sumH = sumStringbbox[3] - sumStringbbox[1]
            maxW = max(maxW, sumW)
            totalH += sumH
        sumtext_x = int((self.left_section_width - maxW) / 2)
        sumtext_y = int(self.height * 0.19) - totalH
        image_draw.multiline_text((sumtext_x, sumtext_y), sumString, font=sumFont, fill=(255, 255, 255), align="center")
        logger.debug(f"Added current weather detailed status text: {sumString} at x:{sumtext_x}/y:{sumtext_y}.")

        ## Add current weather icon to the image
        icon = get_weather_icon(icon_name=self.current_weather.weather_icon_name, size=150)
        # Create a mask from the alpha channel of the weather icon
        if len(icon.split()) == 4:
            mask = icon.split()[-1]
        else:
            mask = None
        # Paste the foreground of the icon onto the background with the help of the mask
        icon_x = int((self.left_section_width - icon.width) / 2)
        icon_y = int(self.height * 0.2)
        self.image.paste(icon, (icon_x, icon_y), mask)

        ## Add current temperature to the image
        tempString = f"{self.current_weather.temperature(self.temp_units)['feels_like']:.0f}{self.tempDispUnit}"
        tempFont = self.get_font(self.font_family, "Bold", 68)
        # Get the width of the text
        tempStringbbox = tempFont.getbbox(tempString)
        tempW = tempStringbbox[2] - tempStringbbox[0]
        temp_x = int((self.left_section_width - tempW) / 2)
        temp_y = int(self.height * 0.4375)
        # Draw the current temp centered
        image_draw.text((temp_x, temp_y), tempString, font=tempFont, fill=(255, 255, 255))

        # Add icon for rain forecast
        rainIcon = Image.open(os.path.join(icons_dir, "rain-chance.bmp"))
        rainIcon = rainIcon.resize((40, 40))
        rain_y = int(self.height * 0.625)
        self.image.paste(rainIcon, (15, rain_y))

        # Amount of precipitation within next 3h
        rain = self.hourly_forecasts[0]["precip_3h_mm"]
        precipString = f"{rain:.1g} mm" if rain > 0.0 else "0 mm"
        precipFont = self.get_font(self.font_family, "Bold", 28)
        image_draw.text((65, rain_y), precipString, font=precipFont, fill=(255, 255, 255))

        # Add icon for wind speed
        windIcon = Image.open(os.path.join(icons_dir, "wind.bmp"))
        windIcon = windIcon.resize((40, 40))
        wind_y = int(self.height * 0.719)
        self.image.paste(windIcon, (15, wind_y))

        # Max. wind speed within next 3h
        wind_gust = f"{self.hourly_forecasts[0]['wind_gust']:.0f}"
        wind = f"{self.hourly_forecasts[0]['wind']:.0f}"
        if self.wind_gusts:
            if wind == wind_gust:
                windString = f"{wind} {self.windDispUnit}"
            else:
                windString = f"{wind} - {wind_gust} {self.windDispUnit}"
        else:
            windString = f"{wind} {self.windDispUnit}"

        windFont = self.get_font(self.font_family, "Bold", 28)
        image_draw.text((65, wind_y), windString, font=windFont, fill=(255, 255, 255))

    def generate_image(self):
        """Generate image for this module"""

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height
        logger.info(f"Image size: {im_size}")

        # Check if internet is available
        if internet_available():
            logger.info("Connection test passed")
        else:
            raise NetworkNotReachableError

        # Get the weather
        (self.current_weather, self.hourly_forecasts) = owm_forecasts.get_owm_data(
            token=self.api_key,
            city_id=self.location,
            temp_units=self.temp_units,
            wind_units=self.wind_units,
            language=self.language,
        )

        ## Create Base Image
        self.createBaseImage()

        ## Add Current Weather to the left section
        self.addCurrentWeather()

        ## Add user-configurable section to the bottom left corner
        self.addUserSection()

        ## Add Hourly Forecast
        # my_image = addHourlyForecast(display=display, image=my_image, hourly_forecasts=hourly_forecasts)

        ## Add Daily Forecast
        # my_image = addDailyForecast(display=display, image=my_image, hourly_forecasts=hourly_forecasts)

        self.image.save("./openweather_full.png")

        logger.info("Fullscreen weather forecast generated successfully.")
        # Return the images ready for the display
        # tbh, I have no idea why I need to return two separate images here
        return self.image, self.image

    @staticmethod
    def get_font(family, style, size):
        # Returns the TrueType font object with the given characteristics
        if family == "Roboto" and style == "ExtraBold":
            style = "Black"
        elif family == "Ubuntu" and style in ["ExtraBold", "Black"]:
            style = "Bold"
        elif family == "OpenSans" and style == "Black":
            style = "ExtraBold"
        return ImageFont.truetype(fonts[f"{family}-{style}"], size=size)


if __name__ == "__main__":
    print(f"running {__name__} in standalone mode")
