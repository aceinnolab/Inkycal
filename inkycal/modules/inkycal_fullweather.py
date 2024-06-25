"""
Inkycal fullscreen weather module
Copyright by mrbwburns
"""
import io
import locale
import logging
import math
import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from dateutil import tz
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

from icons.weather_icons.weather_icons import get_weather_icon
from inkycal.custom.functions import fonts
from inkycal.custom.functions import get_system_tz
from inkycal.custom.functions import internet_available
from inkycal.custom.inkycal_exceptions import NetworkNotReachableError
from inkycal.custom.openweathermap_wrapper import OpenWeatherMap
from inkycal.modules.inky_image import image_to_palette
from inkycal.modules.template import inkycal_module
from inkycal.settings import Settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

settings = Settings()

icons_dir = os.path.join(settings.FONT_PATH, "ui-icons")


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


def get_image_from_plot(fig: plt) -> Image:
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    return Image.open(buf)


class Fullweather(inkycal_module):
    """Fullscreen Weather class
    gets weather details from openweathermap and plots a nice fullscreen forecast picture
    """

    name = "Fullscreen weather (openweathermap) - Get weather forecasts from openweathermap"

    requires = {
        "api_key": {
            "label": "Please enter openweathermap api-key. You can create one for free on openweathermap",
        },
        "latitude": {"label": "Please enter your location' geographical latitude. E.g. 51.51 for London."},
        "longitude": {"label": "Please enter your location' geographical longitude. E.g. -0.13 for London."},
    }

    optional = {
        "api_version": {
            "label": "Please enter openweathermap api version. Default is '2.5'.",
            "options": ["2.5", "3.0"],
        },
        "orientation": {"label": "Please select the desired orientation", "options": ["vertical", "horizontal"]},
        "temp_unit": {
            "label": "Which temperature unit should be used?",
            "options": ["celsius", "fahrenheit"],
        },
        "wind_unit": {
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
        "font": {
            "label": "Font family to use for the entire screen",
            "options": ["NotoSans", "Roboto", "Poppins"],
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

        self.tz = get_system_tz()

        # Check if all required parameters are present
        for param in self.requires:
            if param not in config:
                raise Exception(f"config is missing {param}")

        # required parameters
        self.api_key = config["api_key"]
        self.location_lat = float(config["latitude"])
        self.location_lon = float(config["longitude"])
        self.font_size = int(config["fontsize"])

        # optional parameters
        if "api_version" in config and config["api_version"] == "3.0":
            self.owm_api_version = "3.0"
        else:
            self.owm_api_version = "2.5"
        if "orientation" in config:
            self.orientation = config["orientation"]
            assert self.orientation in ["horizontal", "vertical"]
        else:
            self.orientation = "horizontal"
        if "wind_unit" in config:
            self.wind_unit = config["wind_unit"]
        else:
            self.wind_unit = "meters_sec"
        if self.wind_unit == "beaufort":
            self.windDispUnit = "bft"
        elif self.wind_unit == "knots":
            self.windDispUnit = "kn"
        elif self.wind_unit == "km_hour":
            self.windDispUnit = "km/h"
        elif self.wind_unit == "miles_hour":
            self.windDispUnit = "mph"
        else:
            self.windDispUnit = "m/s"

        if "wind_gusts" in config:
            self.wind_gusts = bool(config["wind_gusts"])
        else:
            self.wind_gusts = True

        if "temp_unit" in config:
            self.temp_unit = config["temp_unit"]
        else:
            self.temp_unit = "celsius"
        if self.temp_unit == "fahrenheit":
            self.tempDispUnit = "F"
        elif self.temp_unit == "celsius":
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

        if "icon_outline" in config:
            self.icon_outline = config["icon_outline"]
        else:
            self.icon_outline = True

        if "font" in config:
            self.font = config["font"]
        else:
            self.font = "Roboto"

        # some calculations for scalability
        # TODO: make this work for all sizes
        if self.orientation == "horizontal":
            self.width, self.height = self.height, self.width
        self.screen_width_in = 163 / 25.4  # 163 mm for 7in5
        self.screen_height_in = 98 / 25.4  # 98 mm for 7in5
        self.dpi = math.sqrt(
            (float(self.width) ** 2 + float(self.height) ** 2)
            / (self.screen_width_in**2 + self.screen_height_in**2)
        )
        self.left_section_width = int(self.width / 4)

        # give an OK message
        logger.debug(f"{__name__} loaded")

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
        tz_info = tz.gettz(self.tz)
        dateString = datetime.now(tz=tz_info).strftime("%d. %B")
        dateFont = self.get_font(style="Bold", size=self.font_size)
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
            humidityString = f"{self.current_weather['humidity']} %"
            humidityFont = self.get_font("Bold", self.font_size + 8)
            image_draw.text((65, humidity_y), humidityString, font=humidityFont, fill=(255, 255, 255))

            # Add icon for uv
            uvIcon = Image.open(os.path.join(icons_dir, "uv.bmp"))
            uvIcon = uvIcon.resize((40, 40))
            ux_y = int(self.height * 0.90625)
            self.image.paste(uvIcon, (15, ux_y))

            # uvindex
            uvi = self.current_weather["uvi"] if self.current_weather["uvi"] else 0.0
            uvString = f"{uvi:.1f}"
            uvFont = self.get_font("Bold", self.font_size + 8)
            image_draw.text((65, ux_y), uvString, font=uvFont, fill=(255, 255, 255))

    def addCurrentWeather(self):
        """
        Adds current weather situation to the left section of the image
        """
        ## Create drawing object for image
        image_draw = ImageDraw.Draw(self.image)

        ## Add detailed weather status text to the image
        sumString = self.current_weather["detailed_status"].replace(" ", "\n ")
        sumFont = self.get_font("Regular", self.font_size + 8)
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
        icon = get_weather_icon(icon_name=self.current_weather["weather_icon_name"], size=150)
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
        tempString = f"{self.current_weather['temp_feels_like']:.0f}{self.tempDispUnit}"
        tempFont = self.get_font("Bold", 68)
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
        precipFont = self.get_font("Bold", self.font_size + 8)
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

        windFont = self.get_font("Bold", self.font_size + 8)
        image_draw.text((65, wind_y), windString, font=windFont, fill=(255, 255, 255))

    def addHourlyForecast(self):
        """
        Adds a plot for temperature and amount of rain for the upcoming hours to the upper right section
        """
        ## Create drawing object for image
        image_draw = ImageDraw.Draw(self.image)

        ## Draw hourly chart title
        title_x = self.left_section_width + 20  # X-coordinate of the title
        title_y = 5
        chartTitleFont = self.get_font("ExtraBold", self.font_size)
        image_draw.text((title_x, title_y), self.chart_title, font=chartTitleFont, fill=0)

        ## Plot the data
        # Define the chart parameters
        w, h = int(0.75 * self.width), int(0.45 * self.height)  # Width and height of the graph

        # Length of our time axis
        num_ticks_x = 22  # ticks*3 hours
        timestamps = [item["datetime"] for item in self.hourly_forecasts][:num_ticks_x]
        temperatures = np.array([item["temp"] for item in self.hourly_forecasts])[:num_ticks_x]
        precipitation = np.array([item["precip_3h_mm"] for item in self.hourly_forecasts])[:num_ticks_x]

        # Create the figure
        fig, ax1 = plt.subplots(figsize=(w / self.dpi, h / self.dpi), dpi=self.dpi)

        # Plot Temperature as line plot in red
        ax1.plot(timestamps, temperatures, marker=".", linestyle="-", color="r")
        temp_base = 3 if self.temp_unit == "celsius" else 5
        fig.gca().yaxis.set_major_locator(ticker.MultipleLocator(base=temp_base))
        ax1.tick_params(axis="y", colors="red")
        ax1.set_yticks(ax1.get_yticks())
        ax1.set_yticklabels([f"{int(value)}{self.tempDispUnit}" for value in ax1.get_yticks()])
        ax1.grid(visible=True, axis="both")  # Adding grid

        if self.min_max_annotations == True:
            # Calculate min_temp and max_temp values based on the minimum and maximum temperatures in the hourly data
            min_temp = np.min(temperatures)
            max_temp = np.max(temperatures)
            # Find positions of min and max values
            min_temp_index = np.argmin(temperatures)
            max_temp_index = np.argmax(temperatures)
            ax1.text(
                timestamps[min_temp_index],
                min_temp,
                f"Min: {min_temp:.1f}{self.tempDispUnit}",
                ha="left",
                va="top",
                color="blue",
                fontsize=12,
            )
            ax1.text(
                timestamps[max_temp_index],
                max_temp,
                f"Max: {max_temp:.1f}{self.tempDispUnit}",
                ha="left",
                va="bottom",
                color="red",
                fontsize=12,
            )

        # Create the second part of the plot as a bar chart for amount of precipitation
        ax2 = ax1.twinx()
        width = np.min(np.diff(mdates.date2num(timestamps)))
        ax2.bar(timestamps, precipitation, color="blue", width=width, alpha=0.2)
        ax2.tick_params(axis="y", colors="blue")
        ax2.set_ylim([0, 10])
        ax2.set_yticks(ax2.get_yticks())
        ax2.set_yticklabels([f"{value:.0f}" for value in ax2.get_yticks()])

        fig.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz=self.tz))
        fig.gca().xaxis.set_major_formatter(mdates.DateFormatter(fmt="%a", tz=self.tz))
        fig.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=3, tz=self.tz))
        fig.tight_layout()  # Adjust layout to prevent clipping of labels

        # Get image from plot and add it to the image
        hourly_forecast_plot = get_image_from_plot(plt)
        plot_x = self.left_section_width + 5
        plot_y = title_y + 30
        self.image.paste(hourly_forecast_plot, (plot_x, plot_y))

    def addDailyForecast(self):
        """
        Adds daily weather forecasts to the lower right section
        """
        ## Create drawing object for image
        image_draw = ImageDraw.Draw(self.image)

        ## Draw daily chart title
        title_y = int(self.height / 2)  # Y-coordinate of the title
        chartTitleFont = self.get_font("Bold", self.font_size)
        image_draw.text((self.left_section_width + 20, title_y), self.weekly_title, font=chartTitleFont, fill=0)

        # Define the parameters
        number_of_forecast_days = 5  # including today
        # Spread evenly, starting from title width
        rectangle_width = int((self.width - (self.left_section_width + 40)) / number_of_forecast_days)
        # Maximum height for each rectangle (avoid overlapping with title)
        rectangle_height = int(self.height / 2 - 20)

        # Rain icon is static
        rainIcon = Image.open(os.path.join(icons_dir, "rain-chance.bmp"))
        rainIcon.convert("L")
        rainIcon = ImageOps.invert(rainIcon)
        weeklyRainIcon = rainIcon.resize((20, 20))

        # Loop through the upcoming days' data and create rectangles
        for i in range(number_of_forecast_days):
            x_rect = self.left_section_width + 20 + i * rectangle_width  # Start from the title width
            y_rect = int(self.height / 2 + 30)

            day_data = self.my_owm.get_forecast_for_day(days_from_today=i)
            rect = Image.new("RGBA", (int(rectangle_width), int(rectangle_height)), (255, 255, 255))
            rect_draw = ImageDraw.Draw(rect)

            # Date string: Day of week on line 1, date on line 2
            short_day_font = self.get_font("ExtraBold", self.font_size + 4)
            short_month_day_font = self.get_font("Bold", self.font_size - 4)
            short_day_name = day_data["datetime"].strftime("%a")
            short_month_day = day_data["datetime"].strftime("%b %d")
            short_day_name_text = rect_draw.textbbox((0, 0), short_day_name, font=short_day_font)
            short_month_day_text = rect_draw.textbbox((0, 0), short_month_day, font=short_month_day_font)
            day_name_x = (rectangle_width - short_day_name_text[2] + short_day_name_text[0]) / 2
            short_month_day_x = (rectangle_width - short_month_day_text[2] + short_month_day_text[0]) / 2
            rect_draw.text((day_name_x, 0), short_day_name, fill=0, font=short_day_font)
            rect_draw.text(
                (short_month_day_x, 30),
                short_month_day,
                fill=0,
                font=short_month_day_font,
            )

            ## Min and max temperature split into diagonal placement
            min_temp = day_data["temp_min"]
            max_temp = day_data["temp_max"]
            temp_text_min = f"{min_temp:.0f}{self.tempDispUnit}"
            temp_text_max = f"{max_temp:.0f}{self.tempDispUnit}"
            rect_temp_font = self.get_font("ExtraBold", self.font_size + 4)
            temp_x_offset = 20
            # this is upper left: max temperature
            temp_text_max_x = temp_x_offset
            temp_text_max_y = int(rectangle_height * 0.25)
            # this is lower right: min temperature
            temp_text_min_bbox = rect_draw.textbbox((0, 0), temp_text_min, font=rect_temp_font)
            temp_text_min_x = (
                int((rectangle_width - temp_text_min_bbox[2] + temp_text_min_bbox[0]) / 2) + temp_x_offset + 7
            )
            temp_text_min_y = int(rectangle_height * 0.33)
            rect_draw.text((temp_text_min_x, temp_text_min_y), temp_text_min, fill=0, font=rect_temp_font)
            rect_draw.text(
                (temp_text_max_x, temp_text_max_y),
                temp_text_max,
                fill=0,
                font=rect_temp_font,
            )

            # Weather icon for the day
            icon_code = day_data["icon"]
            icon = get_weather_icon(icon_name=icon_code, size=90)
            if self.icon_outline:
                icon = outline(image=icon, size=8, color=(0, 0, 0, 255))
            icon_x = int((rectangle_width - icon.width) / 2)
            icon_y = int(rectangle_height * 0.4)
            # Create a mask from the alpha channel of the weather icon
            if len(icon.split()) == 4:
                mask = icon.split()[-1]
            else:
                mask = None
            # Paste the foreground of the icon onto the background with the help of the mask
            rect.paste(icon, (int(icon_x), icon_y), mask)

            ## Precipitation icon and text
            rain = day_data["precip_mm"]
            if rain:
                rain_text = f"{rain:.0f} mm"
                rain_font = self.get_font("ExtraBold", self.font_size)
                # Icon
                rain_icon_x = int((rectangle_width - icon.width) / 2)
                rain_icon_y = int(rectangle_height * 0.82)
                rect.paste(weeklyRainIcon, (rain_icon_x, rain_icon_y))
                # Text
                rain_text_y = int(rectangle_height * 0.8)
                rect_draw.text(
                    (rain_icon_x + weeklyRainIcon.width + 10, rain_text_y),
                    rain_text,
                    fill=0,
                    font=rain_font,
                    align="right",
                )

            self.image.paste(rect, (int(x_rect), int(y_rect)))

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
        self.my_owm = OpenWeatherMap(
            api_key=self.api_key,
            api_version=self.owm_api_version,
            lat=self.location_lat,
            lon=self.location_lon,
            temp_unit=self.temp_unit,
            wind_unit=self.wind_unit,
            language=self.language,
            tz_name=self.tz,
        )
        self.current_weather = self.my_owm.get_current_weather()
        self.hourly_forecasts = self.my_owm.get_weather_forecast()

        ## Create Base Image
        self.createBaseImage()

        ## Add Current Weather to the left section
        self.addCurrentWeather()

        ## Add user-configurable section to the bottom left corner
        self.addUserSection()

        ## Add Hourly Forecast to the top right section
        self.addHourlyForecast()

        ## Add Daily Forecast to the bottom right section
        self.addDailyForecast()

        if self.orientation == "horizontal":
            self.image = self.image.rotate(90, expand=True)

        logger.info("Fullscreen weather forecast generated successfully.")
        # Convert images according to specified palette
        im_black, im_colour = image_to_palette(image=self.image, palette="bwr", dither=True)

        # Return the images ready for the display
        return im_black, im_colour

    def get_font(self, style, size):
        # Returns the TrueType font object with the given characteristics
        # Some workarounds for typefaces that do not exist in some fonts out there
        if self.font == "Roboto" and style == "ExtraBold":
            style = "Black"
        elif self.font in ["Ubuntu", "NotoSansUI"] and style in ["ExtraBold", "Black"]:
            style = "Bold"
        elif self.font == "OpenSans" and style == "Black":
            style = "ExtraBold"
        return ImageFont.truetype(fonts[f"{self.font}-{style}"], size=size)


if __name__ == "__main__":
    print(f"running {__name__} in standalone mode")
