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
dec = decimal.Decimal


"""Optional parameters"""
round_temperature = True
round_windspeed = True
use_beaufort = True
show_wind_direction = False
use_wind_direction_icon = False
now_str = 'now'


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
text_fc1_pos = (coloumn4, row1)
icon_fc1_pos = (coloumn4, row2)
temperature_fc1_pos = (coloumn4, row3)

"""Allocate positions for weather forecast after 6 hours"""
text_fc2_pos = (coloumn5, row1)
icon_fc2_pos = (coloumn5, row2)
temperature_fc2_pos = (coloumn5, row3)

"""Allocate positions for weather forecast after 9 hours"""
text_fc3_pos = (coloumn6, row1)
icon_fc3_pos = (coloumn6, row2)
temperature_fc3_pos = (coloumn6, row3)

"""Allocate positions for weather forecast after 12 hours"""
text_fc4_pos = (coloumn7, row1)
icon_fc4_pos = (coloumn7, row2)
temperature_fc4_pos = (coloumn7, row3)

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
      converted_time = datetime_object.format('h a')
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
  if top_section == "inkycal_weather" and api_key != "" and owm.is_API_online() is True:
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

      """Parse current weather details"""
      sunrise_time_now = arrow.get(weather.get_sunrise_time()).to(get_tz())
      sunset_time_now = arrow.get(weather.get_sunset_time()).to(get_tz())
      humidity_now = str(weather.get_humidity())
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
      write_text(coloumn_width, row_height, now_str, text_now_pos, font = font)
      write_text(icon_medium, icon_medium, weathericons[weather_icon_now],
        weather_icon_now_pos, font = w_font, fill_width = 0.9)

      """Add weather details in column 2"""
      write_text(icon_small, icon_small, '\uf053', temperature_icon_now_pos,
        font = w_font, fill_height = 0.9)
      write_text(icon_small, icon_small, '\uf07a', humidity_icon_now_pos,
        font = w_font, fill_height = 0.9)
      
      if use_wind_direction_icon == False:  
        write_text(icon_small, icon_small, '\uf050', windspeed_icon_now_pos,
          font = w_font, fill_height = 0.9)
      else:
        write_text(icon_small, icon_small, '\uf0b1', windspeed_icon_now_pos,
          font = w_font, fill_height = 0.9, rotation = -wind_degrees)

      write_text(coloumn_width-icon_small, row_height, temperature_now,
        temperature_now_pos, font = font, colour= red_temp(temperature_now))


      write_text(coloumn_width-icon_small, row_height, humidity_now+'%',
        humidity_now_pos, font = font)
      write_text(coloumn_width-icon_small, row_height, wind,
        windspeed_now_pos, font = font, autofit = True)

      """Add weather details in column 3"""
      write_text(coloumn_width, row_height, moonphase , moon_phase_now_pos,
        font = w_font, fill_height = 0.9)
      write_text(icon_small, icon_small, '\uf051', sunrise_icon_now_pos,
        font = w_font, fill_height = 0.9)
      write_text(icon_small, icon_small, '\uf052', sunset_icon_now_pos,
        font = w_font, fill_height = 0.9)

      write_text(coloumn_width-icon_small, row_height,
        to_hours(sunrise_time_now), sunrise_time_now_pos, font = font,
                 fill_width = 0.9)
      write_text(coloumn_width-icon_small, row_height,
        to_hours(sunset_time_now), sunset_time_now_pos, font = font,
                 fill_width = 0.9)

      """Add weather details in column 4 (forecast 1)"""
      write_text(coloumn_width, row_height, to_hours(fc1, simple=True),
        text_fc1_pos, font = font)
      write_text(coloumn_width, row_height, weathericons[weather_icon_fc1],
        icon_fc1_pos, font = w_font, fill_height = 1.0)
      write_text(coloumn_width, row_height, temperature_fc1,
        temperature_fc1_pos, font = font, colour = red_temp(
          temperature_fc1))

      """Add weather details in column 5 (forecast 2)"""
      write_text(coloumn_width, row_height, to_hours(fc2, simple=True),
        text_fc2_pos, font = font)
      write_text(coloumn_width, row_height, weathericons[weather_icon_fc2],
        icon_fc2_pos, font = w_font, fill_height = 1.0)
      write_text(coloumn_width, row_height, temperature_fc2,
          temperature_fc2_pos, font = font, colour = red_temp(
          temperature_fc2))

      """Add weather details in column 6 (forecast 3)"""
      write_text(coloumn_width, row_height, to_hours(fc3, simple=True),
        text_fc3_pos, font = font)
      write_text(coloumn_width, row_height, weathericons[weather_icon_fc3],
        icon_fc3_pos, font = w_font, fill_height = 1.0)
      write_text(coloumn_width, row_height, temperature_fc3,
          temperature_fc3_pos, font = font, colour = red_temp(
          temperature_fc3))

      """Add weather details in coloumn 7 (forecast 4)"""
      write_text(coloumn_width, row_height, to_hours(fc4, simple=True),
        text_fc4_pos, font = font)
      write_text(coloumn_width, row_height, weathericons[weather_icon_fc4],
        icon_fc4_pos, font = w_font, fill_height = 1.0)
      write_text(coloumn_width, row_height, temperature_fc4,
          temperature_fc4_pos, font = font, colour = red_temp(
          temperature_fc4))

      """Add vertical lines between forecast sections"""
      draw = ImageDraw.Draw(image)
      line_start_y = int(top_section_height*0.1)
      line_end_y = int(top_section_height*0.9)

      draw.line((coloumn4, line_start_y, coloumn4, line_end_y), fill='black')
      draw.line((coloumn5, line_start_y, coloumn5, line_end_y), fill='black')
      draw.line((coloumn6, line_start_y, coloumn6, line_end_y), fill='black')
      draw.line((coloumn7, line_start_y, coloumn7, line_end_y), fill='black')

      if three_colour_support == True:
        draw_col.line((0, top_section_height-border_top, top_section_width-
        border_left, top_section_height-border_top), fill='black', width=3)
      else:
        draw.line((0, top_section_height-border_top, top_section_width-
        border_left, top_section_height-border_top), fill='black', width=3)

      weather_image = crop_image(image, 'top_section')  
      weather_image.save(image_path+'inkycal_weather.png')

      if three_colour_support == True:
        weather_image_col = crop_image(image_col, 'top_section')  
        weather_image_col.save(image_path+'inkycal_weather_col.png')
        
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
      weather_image.save(image_path+'inkycal_weather.png')
      pass

def main():
  generate_image()

main()
