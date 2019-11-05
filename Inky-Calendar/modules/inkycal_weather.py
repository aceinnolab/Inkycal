#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Weather module for Inky-Calendar software. In development...

The lunar phase calculation algorithm was taken from Michael Bishop
from Github after being granted permission. Thanks, Michael Bishop for your
awesome code!

Copyright by aceisace
"""
from __future__ import print_function
import pyowm
from settings import *
from configuration import *
from PIL import Image, ImageDraw, ImageFont
import arrow
import math, decimal
dec = decimal.Decimal

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


"""Add a border to increase readability"""
border_top = int(top_section_height * 0.05)
border_left = int(top_section_width * 0.02)

"""Calculate size for each weather sub-section"""
row_height = (top_section_height-(border_top*2)) // 3
coloumn_width = (top_section_width-(border_left*2)) // 7

"""Calculate paddings"""
x_padding = int( (top_section_width % coloumn_width) / 2 )
y_padding = int( (top_section_height % row_height) / 2 )

"""Allocate sizes for weather icons"""
icon_small = row_height
icon_medium = row_height * 2

"""Calculate the x-axis position of each coloumn"""
coloumn1 = x_padding
coloumn2 = coloumn1 + coloumn_width
coloumn3 = coloumn2 + coloumn_width
coloumn4 = coloumn3 + coloumn_width
coloumn5 = coloumn4 + coloumn_width
coloumn6 = coloumn5 + coloumn_width
coloumn7 = coloumn6 + coloumn_width

"""Calculate the y-axis position of each row"""
row1 = y_padding
row2 = row1 + row_height
row3 = row2 + row_height

"""Allocate positions for current weather details"""
text_now_pos = (coloumn1, row1)
weather_icon_now_pos = (coloumn1, row2)

temperature_icon_now_pos = (coloumn2, row1)
temperature_now_pos = (coloumn2+icon_small, row1)
humidity_icon_now_pos = (coloumn2, row2)
humidity_now_pos = (coloumn2+icon_small, row2)
windspeed_icon_now_pos = (coloumn2, row3)
windspeed_now_pos = (coloumn2+icon_small, row3)

moon_phase_now_pos = (coloumn3, row1)
sunrise_icon_now_pos = (coloumn3, row2)
sunrise_time_now_pos = (coloumn3+icon_small, row2)
sunset_icon_now_pos = (coloumn3, row3)
sunset_time_now_pos = (coloumn3+ icon_small, row3)

"""Allocate positions for weather forecast after 3 hours"""
text_3h_pos = (coloumn4, row1)
icon_3h_pos = (coloumn4, row2)
temperature_3h_pos = (coloumn4, row3)

"""Allocate positions for weather forecast after 6 hours"""
text_6h_pos = (coloumn5, row1)
icon_6h_pos = (coloumn5, row2)
temperature_6h_pos = (coloumn5, row3)

"""Allocate positions for weather forecast after 9 hours"""
text_9h_pos = (coloumn6, row1)
icon_9h_pos = (coloumn6, row2)
temperature_9h_pos = (coloumn6, row3)

"""Allocate positions for weather forecast after 12 hours"""
text_12h_pos = (coloumn7, row1)
icon_12h_pos = (coloumn7, row2)
temperature_12h_pos = (coloumn7, row3)

"""Windspeed (m/s) to beaufort (index of list) conversion"""
windspeed_to_beaufort = [0.02, 1.5, 3.3, 5.4, 7.9, 10.7, 13.8, 17.1, 20.7,
  24.4, 28.4, 32.6, 100]

"""Function to convert tempertures from kelvin to celcius or fahrenheit"""
def to_units(kelvin):
  if units == 'metric':
    conversion =  str(int(kelvin - 273.15)) + '°C'
  else:
    conversion = str(int((kelvin - 273.15) * 9/5 + 32)) + 'F'
  return conversion

"""Function to convert time objects to specified format 12/24 hours"""
"""Simple means just the hour and if 12 hours, am/pm as well"""
def to_hours(datetime_object, simple = False):
  if hours == '24':
    if simple == True:
      converted_time = datetime_object.format('H')
    else:
      converted_time = datetime_object.format('HH:mm')
  else:
    if simple == True:
      converted_time = datetime_object.format('H a')
    else:
      converted_time = datetime_object.format('hh:mm')
  return str(converted_time)

#def main():
try:
  """Connect to Openweathermap API and fetch weather data"""
  if top_section == "Weather" and api_key != "" and owm.is_API_online() is True:
    #try:
    print("Fetching weather data from openweathermap API...",end = ' ')
    current_weather_setup = owm.weather_at_place(location)
    weather = current_weather_setup.get_weather()

    """Set-up and get weather forecast data"""
    forecast = owm.three_hours_forecast(location)
    print("Done")

    """Round the hour to the nearest multiple of 3"""
    now = arrow.now(tz=get_tz())
    hour_gap = (now.hour % 3)

    """Prepare timings for forecasts"""
    in_3h = now.replace(hours = + hour_gap + 3)
    in_6h = now.replace(hours = + hour_gap + 6)
    in_9h = now.replace(hours = + hour_gap + 9)
    in_12h = now.replace(hours = + hour_gap + 12)

    """Prepare forecast objects for the specified timings"""
    forecast_3h = forecast.get_weather_at(in_3h.datetime)
    forecast_6h = forecast.get_weather_at(in_6h.datetime)
    forecast_9h = forecast.get_weather_at(in_9h.datetime)
    forecast_12h = forecast.get_weather_at(in_12h.datetime)

    """Get the current temperature and forcasts temperatures"""
    temperature_now = to_units(weather.get_temperature()['temp'])
    temperature_3h = to_units(forecast_3h.get_temperature()['temp'])
    temperature_6h = to_units(forecast_6h.get_temperature()['temp'])
    temperature_9h = to_units(forecast_9h.get_temperature()['temp'])
    temperature_12h = to_units(forecast_12h.get_temperature()['temp'])

    """Get current and forecast weather icon names"""
    weather_icon_now = weather.get_weather_icon_name()
    weather_icon_3h = forecast_3h.get_weather_icon_name()
    weather_icon_6h = forecast_6h.get_weather_icon_name()
    weather_icon_9h = forecast_9h.get_weather_icon_name()
    weather_icon_12h = forecast_12h.get_weather_icon_name()

    """Parse current weather details"""
    sunrise_time_now = arrow.get(weather.get_sunrise_time()).to(get_tz())
    sunset_time_now = arrow.get(weather.get_sunset_time()).to(get_tz())
    humidity_now = str(weather.get_humidity())
    cloudstatus_now = str(weather.get_clouds())
    weather_description_now = str(weather.get_detailed_status())
    windspeed_now = weather.get_wind(unit='meters_sec')['speed']

    beaufort = str([windspeed_to_beaufort.index(_) for _ in windspeed_to_beaufort
      if windspeed_now < _][0])


    """Calculate the moon phase"""
    def get_moon_phase():
     diff = now - arrow.get(2001, 1, 1)
     days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
     lunations = dec("0.20439731") + (days * dec("0.03386319269"))
     position = lunations % dec(1)
     index = math.floor((position * dec(8)) + dec("0.5"))
     return {0: '\uf095',1: '\uf099',2: '\uf09c',3: '\uf0a0',
             4: '\uf0a3',5: '\uf0a7',6: '\uf0aa',7: '\uf0ae' }[int(index) & 7]

    moonphase = get_moon_phase()

    print('Adding weather details on the image...', end = ' ')

    """Add weather details in column 1"""
    write_text(coloumn_width, row_height, 'now', text_now_pos)
    write_text(icon_medium, icon_medium, weathericons[weather_icon_now],
      weather_icon_now_pos, font = w_font, adapt_fontsize = True)

    """Add weather details in column 2"""
    write_text(icon_small, icon_small, '\uf053', temperature_icon_now_pos,
      font = w_font, adapt_fontsize = True)
    write_text(icon_small, icon_small, '\uf07a', humidity_icon_now_pos,
      font = w_font, adapt_fontsize = True)
    write_text(icon_small, icon_small, '\uf050', windspeed_icon_now_pos,
      font = w_font, adapt_fontsize = True)

    write_text(coloumn_width-icon_small, row_height,
      temperature_now, temperature_now_pos)
    write_text(coloumn_width-icon_small, row_height, humidity_now+'%',
      humidity_now_pos)
    write_text(coloumn_width-icon_small, row_height, beaufort,
      windspeed_now_pos)

    """Add weather details in column 3"""
    write_text(coloumn_width, row_height, moonphase , moon_phase_now_pos,
      font = w_font, adapt_fontsize = True)
    write_text(icon_small, icon_small, '\uf051', sunrise_icon_now_pos,
      font = w_font, adapt_fontsize = True)
    write_text(icon_small, icon_small, '\uf052', sunset_icon_now_pos,
      font = w_font, adapt_fontsize = True)

    write_text(coloumn_width-icon_small, row_height, to_hours(sunrise_time_now),
      sunrise_time_now_pos)
    write_text(coloumn_width-icon_small, row_height, to_hours(sunset_time_now),
      sunset_time_now_pos)

    """Add weather details in column 4"""
    write_text(coloumn_width, row_height, to_hours(in_3h, simple=True),
      text_3h_pos)
    write_text(coloumn_width, row_height, weathericons[weather_icon_3h],
      icon_3h_pos, font = w_font, adapt_fontsize = True)
    write_text(coloumn_width, row_height, temperature_3h,
        temperature_3h_pos)

    """Add weather details in column 5"""
    write_text(coloumn_width, row_height, to_hours(in_6h, simple=True),
      text_6h_pos)
    write_text(coloumn_width, row_height, weathericons[weather_icon_6h],
      icon_6h_pos, font = w_font, adapt_fontsize = True)
    write_text(coloumn_width, row_height, temperature_6h,
        temperature_6h_pos)

    """Add weather details in column 6"""
    write_text(coloumn_width, row_height, to_hours(in_9h, simple=True),
      text_9h_pos)
    write_text(coloumn_width, row_height, weathericons[weather_icon_9h],
      icon_9h_pos, font = w_font, adapt_fontsize = True)
    write_text(coloumn_width, row_height, temperature_9h,
        temperature_9h_pos)

    """Add weather details in column 7"""
    write_text(coloumn_width, row_height, to_hours(in_12h, simple=True),
      text_12h_pos)
    write_text(coloumn_width, row_height, weathericons[weather_icon_12h],
      icon_12h_pos, font = w_font, adapt_fontsize = True)
    write_text(coloumn_width, row_height, temperature_12h,
        temperature_12h_pos)


    """Add seperators between section4 and section7"""
    draw = ImageDraw.Draw(image)
    line_start_y = int(top_section_height*0.1)
    line_end_y = int(top_section_height*0.9)

    draw.line((coloumn4, line_start_y, coloumn4, line_end_y), fill='black')
    draw.line((coloumn5, line_start_y, coloumn5, line_end_y), fill='black')
    draw.line((coloumn6, line_start_y, coloumn6, line_end_y), fill='black')
    draw.line((coloumn7, line_start_y, coloumn7, line_end_y), fill='black')
    draw.line((0, top_section_height-border_top, top_section_width-border_left,
      top_section_height-border_top), fill='red', width=3)

    print('Done'+'\n')
    image.crop((0,0, top_section_width, top_section_height)).save('weather.png')

except Exception as e:
  """If no response was received from the openweathermap
  api server, add the cloud with question mark"""
  print('__________OWM-ERROR!__________')
  print('Reason: ',e)
  write_text(icon_medium, icon_medium, '\uf07b', weather_icon_now_pos,
  font = w_font, adapt_fontsize = True)
  message = 'No internet connectivity or API timeout'
  write_text(coloumn_width*6, row_height, message, humidity_icon_now_pos)
  pass


#if __name__ == '__main__':
    #main()
