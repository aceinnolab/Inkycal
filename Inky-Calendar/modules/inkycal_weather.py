#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Weather module for Inky-Calendar software. In development...

To-do:
- make locations of icons and text dynamic
Copyright by aceisace
"""
from __future__ import print_function
import pyowm
from settings import *
from configuration import *
from PIL import Image, ImageDraw, ImageFont
import arrow

print('Initialising weather...', end=' ')
owm = pyowm.OWM(api_key, language=language)
print('Done')

"""Icon-code to unicode dictionary for weather-font"""
weathericons = {
  '01d': '\uf00d', '02d': '\uf002', '03d': '\uf013',
  '04d': '\uf012', '09d': '\uf01a', '10d': '\uf019',
  '11d': '\uf01e', '13d': '\uf01b', '50d': '\uf014',
  '01n': '\uf02e', '02n': '\uf013', '03n': '\uf013',
  '04n': '\uf013', '09n': '\uf037', '10n': '\uf036',
  '11n': '\uf03b', '13n': '\uf038', '50n': '\uf023'
  }


"""Split top_section into to 2 rows"""
section_height = top_section_height // 2
section_width = (top_section_width - top_section_height) // 3

"""Allocate icon sizes"""
icon_small = section_height
icon_large = top_section_height

"""Split top section into 4 coloums"""
section1 = 0
section2 = icon_large + (top_section_width - icon_large) // 3 * 0
section3 = icon_large + (top_section_width - icon_large) // 3 * 1
section4 = icon_large + (top_section_width - icon_large) // 3 * 2

"""Allocate positions for icons"""
weather_icon_pos = (section1, 0)
wind_icon_pos = (section2, 0)
sun_icon_pos = (section3, 0)
temperature_icon_pos = (section4, 0)
weather_description_pos = (section2, section_height)
humidity_icon_pos = (section4, section_height)

"""Allocate positions for text"""
next_to = lambda x: (x[0]+ icon_small, x[1])
icon_offset = section_width - icon_small

wind_pos = next_to(wind_icon_pos)
temperature_pos = next_to(temperature_icon_pos)
sun_pos = next_to(sun_icon_pos)
humidity_pos = next_to(humidity_icon_pos)
weather_pos = (section2, section_height)


#def main():

"""Connect to Openweathermap API and fetch weather data"""
if top_section == "Weather" and api_key != "" and owm.is_API_online() is True:
  try:
    print("Fetching weather data from openweathermap...",end = ' ')
    observation = owm.weather_at_place(location)
    print("Done")

    weather = observation.get_weather()
    weathericon = weather.get_weather_icon_name()
    Humidity = str(weather.get_humidity())
    cloudstatus = str(weather.get_clouds())
    weather_description = (str(weather.get_detailed_status()))

    """Add the icons at the correct positions"""
    print('Adding weather info and icons to the image...', end = ' ')
    write_text(icon_small, icon_small, '\uf055', temperature_icon_pos,
      font = w_font, adapt_fontsize = True) # Temperature icon

    write_text(icon_large, icon_large, weathericons[weathericon],
      weather_icon_pos, font = w_font, adapt_fontsize = True) # Weather icon

    write_text(icon_small, icon_small, '\uf07a', humidity_icon_pos, font = w_font,
      adapt_fontsize = True) #Humidity icon

    write_text(icon_small,icon_small, '\uf050', wind_icon_pos, font = w_font,
      adapt_fontsize = True) #Wind icon

    """Format and write the temperature and windspeed"""
    if units == "metric":
      Temperature = str(int(weather.get_temperature(unit='celsius')['temp']))
      windspeed = str(int(weather.get_wind()['speed']))

      write_text(icon_offset, section_height, Temperature+'°C', temperature_pos)

      write_text(icon_offset,section_height, windspeed+" km/h", wind_pos)

    else:
      Temperature = str(int(weather.get_temperature('fahrenheit')['temp']))
      windspeed = str(int(weather.get_wind()['speed']*0.621))

      write_text(icon_offset, section_height, Temperature+' F', temperature_pos)

      write_text(icon_offset,section_height, windspeed+" mph", wind_pos)

    """write the humidity at the given position"""
    write_text(icon_offset, section_height, Humidity+'%', humidity_pos)

    now = arrow.now(tz=get_tz())
    sunrise = arrow.get(weather.get_sunrise_time()).to(get_tz())
    sunset = arrow.get(weather.get_sunset_time()).to(get_tz())

    """Add the sunrise/sunset icon and display the time"""
    if (now <= sunrise and now <= sunset) or (now >= sunrise and now >= sunset):
      write_text(icon_small, icon_small, '\uf051', sun_icon_pos, font = w_font,
                 adapt_fontsize = True)
      if hours == "24":
        write_text(icon_offset, section_height, sunrise.format('H:mm'), sun_pos)
      else:
        write_text(icon_offset, section_height, sunrise.format('h:mm'), sun_pos)
    else:
      write_text(icon_small, '\uf052', sun_icon_pos, font = w_font,
                 adapt_fontsize = True)
      if hours == "24":
        write_text(icon_offset, section_height, sunset.format('H:mm'), sun_pos)
      else:
        write_text(icon_offset, section_height, sunset.format('h:mm'), sun_pos)


    """Add a short weather description"""
    write_text(section2+section3-icon_offset, section_height,
               weather_description, weather_pos)

    print('Done'+'\n')

    """Show the fetched weather data"""
    print("Today's weather report: The current Temperature is {0}°C. The "
    "relative humidity is {1} %. The current windspeed is {2} km/h. "
    "The sunrise today was at {3}. The sunset is at {4}. The weather can "
    "be described with: {5}".format(Temperature, Humidity, windspeed,
      sunrise.format('H:mm'), sunset.format('H:mm'), weather_description))

    image.crop((0,0, top_section_width, top_section_height)).save('weather.png')

  except Exception as e:
    """If no response was received from the openweathermap
    api server, add the cloud with question mark"""
    print('__________OWM-ERROR!__________')
    print('Reason: ',e)
    write_text(icon_large, icon_large, '\uf07b', weather_icon_pos,
               font = w_font, adapt_fontsize = True)
    pass


#if __name__ == '__main__':
    #main()
