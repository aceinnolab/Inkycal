#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Weather module for Inky-Calendar software.

The lunar phase calculation is from Sean B. Palmer, inamidst.com.
Thank You Palmer for the awesome code!

Copyright by aceisace
"""
from __future__ import print_function
import pyowm
from configuration import *
import math, decimal
import time
dec = decimal.Decimal

"""Optional parameters"""
round_temperature = True
round_windspeed = True
use_beaufort = True
show_wind_direction = False
use_wind_direction_icon = False
now_str_time = time.strftime("@%H:%M")

"""Set the optional parameters"""
decimal_places_temperature = None if round_temperature == True else 1
decimal_places_windspeed = None if round_windspeed == True else 1

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
row_height = (top_section_height-(border_top*2)) // 4
column_width = (top_section_width-(border_left*2)) // 7

"""Calculate paddings"""
x_padding = int( (top_section_width % column_width) / 2 )
y_padding = int( (top_section_height % row_height) / 2 )

"""Allocate sizes for weather icons"""
icon_small = row_height
icon_medium = row_height * 2

"""Calculate the x-axis position of each column"""
column1 = x_padding
column2 = column1 + column_width
column3 = column2 + column_width
column4 = column3 + column_width
column5 = column4 + column_width
column6 = column5 + column_width
column7 = column6 + column_width

"""Calculate the y-axis position of each row"""
row1 = y_padding
row2 = row1 + row_height
row3 = row2 + row_height
row4 = row3 + row_height

"""Windspeed (m/s) to beaufort (index of list) conversion"""
windspeed_to_beaufort = [0.02, 1.5, 3.3, 5.4, 7.9, 10.7, 13.8, 17.1, 20.7,
  24.4, 28.4, 32.6, 100]

def to_units(kelvin):
  """Function to convert tempertures from kelvin to celcius or fahrenheit"""
  degrees_celsius = round(kelvin - 273.15, ndigits = decimal_places_temperature)
  fahrenheit = round((kelvin - 273.15) * 9/5 + 32,
                     ndigits = decimal_places_temperature)
  if units == 'metric':
    conversion = str(degrees_celsius) + '°C'

  if units == 'imperial':
    conversion = str(fahrenheit) + 'F'

  return conversion

def red_temp(negative_temperature):
  if three_colour_support == True and negative_temperature[0] == '-' and units == 'metric':
    colour = 'red'
  else:
    colour = 'black'
  return colour

"""Function to convert time objects to specified format 12/24 hours"""
"""Simple means just the hour and if 12 hours, am/pm as well"""
def to_hours(datetime_object, simple = False):
  if hours == '24':
    if simple == True:
      converted_time = datetime_object.format('H') + '.00'
    else:
      converted_time = datetime_object.format('HH:mm')
  else:
    if simple == True:
      converted_time = datetime_object.format('H a')
    else:
      converted_time = datetime_object.format('hh:mm')
  return str(converted_time)

"""Choose font optimised for the weather section"""
fontsize = 8
font = ImageFont.truetype(NotoSans+'Medium.ttf', fontsize)
fill_height = 0.8

while font.getsize('hg')[1] <= (row_height * fill_height):
  fontsize += 1
  font = ImageFont.truetype(NotoSans+'.ttf', fontsize)

def generate_image():
  """Connect to Openweathermap API and fetch weather data"""
  if top_section == "inkycal_weather2" and api_key != "" and owm.is_API_online() is True:
    try:
      clear_image('top_section')
      print('Weather module: Connectivity check passed, Generating image...',
        end = '')
      current_weather_setup = owm.weather_at_place(location)
      weather = current_weather_setup.get_weather()
      
      """Set-up and get weather forecast data"""
      forecast = owm.three_hours_forecast(location)

      """Round the hour to the nearest multiple of 3"""
      now = arrow.utcnow()
      if (now.hour % 3) != 0:
        hour_gap = 3 - (now.hour % 3)
      else:
        hour_gap = 3

      """Prepare timings for forecasts"""
      fc1 = now.replace(hours = + hour_gap).floor('hour')
      fc2 = now.replace(hours = + hour_gap + 3).floor('hour')
      fc3 = now.replace(hours = + hour_gap + 6).floor('hour')
      fc4 = now.replace(hours = + hour_gap + 9).floor('hour')

      """Prepare forecast objects for the specified timings"""
      forecast_fc1 = forecast.get_weather_at(fc1.datetime)
      forecast_fc2 = forecast.get_weather_at(fc2.datetime)
      forecast_fc3 = forecast.get_weather_at(fc3.datetime)
      forecast_fc4 = forecast.get_weather_at(fc4.datetime)

      """Get the current temperature and forcasts temperatures"""
      temperature_now = to_units(weather.get_temperature()['temp'])
      temperature_fc1 = to_units(forecast_fc1.get_temperature()['temp'])
      temperature_fc2 = to_units(forecast_fc2.get_temperature()['temp'])
      temperature_fc3 = to_units(forecast_fc3.get_temperature()['temp'])
      temperature_fc4 = to_units(forecast_fc4.get_temperature()['temp'])

      """Get current and forecast weather icon names"""
      weather_icon_now = weather.get_weather_icon_name()
      weather_icon_fc1 = forecast_fc1.get_weather_icon_name()
      weather_icon_fc2 = forecast_fc2.get_weather_icon_name()
      weather_icon_fc3 = forecast_fc3.get_weather_icon_name()
      weather_icon_fc4 = forecast_fc4.get_weather_icon_name()

      """Get current rain in mm/h"""
      rain = weather.get_rain()
#      print ('get_rain: ', rain)
      if '1h' in rain:
        rain_now = rain['1h']
      elif '3h' in rain:
        rain_now = rain['3h']/3
      else:
        rain_now = 0
      rain_now = str("%0.1f" % (rain_now))
#      print ('rain_now = ', rain_now)
#      print ('fc1.get_rain',forecast_fc1.get_rain())
#      rain = forecast_fc1.get_rain()
#      if '1h' in rain:
#        humidity_fc1 = rain['1h']
#      elif '3h' in rain:
#        humidity_fc1 = rain['3h']/3
#        print('humidity_fc1', humidity_fc1)
#      else:
#        humidity_fc1 = 0
#      humidity_fc1 = str("%0.2f" % (humidity_fc1))

      """Parse current weather details"""
      sunrise_time_now = arrow.get(weather.get_sunrise_time()).to(get_tz())
      sunset_time_now = arrow.get(weather.get_sunset_time()).to(get_tz())
#      humidity_now = str(weather.get_humidity())
      cloudstatus_now = str(weather.get_clouds())
      weather_description_now = str(weather.get_detailed_status())
      windspeed_now = weather.get_wind(unit='meters_sec')['speed']
      wind_degrees = forecast_fc1.get_wind()['deg']
      wind_direction = ["N","NE","E","SE","S","SW","W","NW"][round(
        wind_degrees/45) % 8]

      if use_beaufort == True:
        wind = str([windspeed_to_beaufort.index(_) for _ in
          windspeed_to_beaufort if windspeed_now < _][0])
      else:
        meters_sec = round(windspeed_now, ndigits = windspeed_decimal_places)
        miles_per_hour = round(windspeed_now * 2,23694,
                               ndigits = windspeed_decimal_places)
        if units == 'metric':
          wind = str(meters_sec) + 'm/s'
        if units == 'imperial':
          wind = str(miles_per_hour) + 'mph'
      if show_wind_direction == True:
        wind += '({0})'.format(wind_direction)

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

      """Add weather details in column 1"""
      write_text(column_width, row_height, now_str_time, (column1, row1),
                 font = font, alignment='left')
      write_text(icon_medium, icon_medium, weathericons[weather_icon_now],
                 (column1, row2), font = w_font, fill_width = 0.9)
      write_text(column_width, row_height, temperature_now, (column1,row4),
                 font = font, alignment='middle')

      """Add weather details in column 2"""
      write_text(icon_small, icon_small, '\uf07a', (column2,row1),
        font = w_font, fill_height = 0.9)
      
      if use_wind_direction_icon == False:  
        write_text(icon_small, icon_small, '\uf050', (column2,row3),
          font = w_font, fill_height = 0.9)
      else:
        write_text(icon_small, icon_small, '\uf0b1', (column2,row3),
          font = w_font, fill_height = 0.9, rotation = -wind_degrees)

      write_text(column_width, row_height, rain_now+'mm',
        (column2,row2), font = font, alignment = 'left')
      write_text(column_width, row_height, wind,
        (column2,row4), font = font, alignment = 'left', autofit = True)

      """Add weather details in column 3"""
#      write_text(column_width, row_height, moonphase , (column3, row1),
#        font = w_font, fill_height = 0.9)
      write_text(icon_small-1, icon_small-1, '\uf051', (column3, row1),
        font = w_font, fill_height = 0.9)
      write_text(icon_small, icon_small, '\uf052', (column3, row3),
        font = w_font, fill_height = 0.9)

      write_text(column_width, row_height,
        to_hours(sunrise_time_now), (column3, row2), font = font,
                 fill_width = 0.9)
      write_text(column_width, row_height,
        to_hours(sunset_time_now), (column3, row4), font = font,
                 fill_width = 0.9)

      """Add weather details in column 4 (forecast 1)"""
      write_text(column_width, row_height, to_hours(fc1.to(get_tz()),
        simple=True), (column4, row1), font = font)
      write_text(column_width, row_height, weathericons[weather_icon_fc1],
        (column4, row2), font = w_font, fill_height = 1.0)
      write_text(column_width, row_height, temperature_fc1, (column4, row3),
                 font = font, colour = red_temp(temperature_fc1))

      """Add weather details in column 5 (forecast 2)"""
      write_text(column_width, row_height, to_hours(fc2.to(get_tz()),
        simple=True), (column5, row1), font = font)
      write_text(column_width, row_height, weathericons[weather_icon_fc2],
        (column5, row2), font = w_font, fill_height = 1.0)
      write_text(column_width, row_height, temperature_fc2,
          (column5, row3), font = font, colour = red_temp(
          temperature_fc2))

      """Add weather details in column 6 (forecast 3)"""
      write_text(column_width, row_height, to_hours(fc3.to(get_tz()),
        simple=True), (column6, row1), font = font)
      write_text(column_width, row_height, weathericons[weather_icon_fc3],
        (column6, row2), font = w_font, fill_height = 1.0)
      write_text(column_width, row_height, temperature_fc3,
          (column6, row3), font = font, colour = red_temp(
          temperature_fc3))

      """Add weather details in column 7 (forecast 4)"""
      write_text(column_width, row_height, to_hours(fc4.to(get_tz()),
        simple=True), (column7, row1), font = font)
      write_text(column_width, row_height, weathericons[weather_icon_fc4],
        (column7, row2), font = w_font, fill_height = 1.0)
      write_text(column_width, row_height, temperature_fc4,
          (column7, row3), font = font, colour = red_temp(
          temperature_fc4))

      """Add vertical lines between forecast sections"""
      draw = ImageDraw.Draw(image)
      line_start_y = int(top_section_height*0.1)
      line_end_y = int(top_section_height*0.9)

      draw.line((column4, line_start_y, column4, line_end_y), fill='black')
      draw.line((column5, line_start_y, column5, line_end_y), fill='black')
      draw.line((column6, line_start_y, column6, line_end_y), fill='black')
      draw.line((column7, line_start_y, column7, line_end_y), fill='black')

      if three_colour_support == True:
        draw_col.line((0, top_section_height-border_top, top_section_width-
        border_left, top_section_height-border_top), fill='black', width=3)
      else:
        draw.line((0, top_section_height-border_top, top_section_width-
        border_left, top_section_height-border_top), fill='black', width=3)

      weather_image = crop_image(image, 'top_section')  
      weather_image.save(image_path+'inkycal_weather2.png')

      if three_colour_support == True:
        weather_image_col = crop_image(image_col, 'top_section')  
        weather_image_col.save(image_path+'inkycal_weather2_col.png')
        
      print('Done')

    except Exception as e:
      """If something went wrong, print a Error message on the Terminal"""
      print('Failed!')
      print('Error in weather module!')
      print('Reason: ',e)
      clear_image('top_section')
      write_text(top_section_width, top_section_height, str(e),
                 (0, 0), font = font)
      weather_image = crop_image(image, 'top_section')
      weather_image.save(image_path+'inkycal_weather2.png')
      pass

def main():
  generate_image()

main()
