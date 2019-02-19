#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
E-Paper Software (main script) for the 3-colour and 2-Colour E-Paper display
A full and detailed breakdown for this code can be found in the wiki.
If you have any questions, feel free to open an issue at Github.

Copyright by aceisace
"""
from __future__ import print_function
import calendar
from datetime import datetime
from time import sleep

from settings import *
from icon_positions_locations import *

from PIL import Image, ImageDraw, ImageFont, ImageOps
import pyowm
from ics import Calendar
try:
    from urllib.request import urlopen
except Exception as e:
    print("Something didn't work right, maybe you're offline?"+e.reason)

if display_colours == "bwr":
    import epd7in5b
    epd = epd7in5b.EPD()

if display_colours == "bw":
    import epd7in5
    epd = epd7in5.EPD()

from calibration import calibration

EPD_WIDTH = 640
EPD_HEIGHT = 384
font = ImageFont.truetype(path+'Assistant-Regular.ttf', 18)
im_open = Image.open

"""Main loop starts from here"""
def main():
    while True:

        time = datetime.now()
        hour = int(time.strftime("%-H"))
        month = int(time.now().strftime('%-m'))
        year = int(time.now().strftime('%Y'))

        for i in range(1):
            print('_________Starting new loop___________'+'\n')
            """At the following hours (midnight, midday and 6 pm), perform
               a calibration of the display's colours"""

            if hour is 0 or hour is 12 or hour is 18:
                print('performing calibration for colours now')
                calibration()

            print('Date:', time.strftime('%a %-d %b %y')+', time: '+time.strftime('%H:%M')+'\n')

            """Create a blank white page, for debugging, change mode to
            to 'RGB' and and save the image by uncommenting the image.save
            line at the bottom"""
            image = Image.new('L', (EPD_HEIGHT, EPD_WIDTH), 'white')
            draw = (ImageDraw.Draw(image)).bitmap

            """Draw the icon with the current month's name"""
            image.paste(im_open(mpath+str(time.strftime("%B")+'.jpeg')), monthplace)

            """Draw a line seperating the weather and Calendar section"""
            image.paste(seperator, seperatorplace)

            """Draw the icons with the weekday-names (Mon, Tue...) and
               draw a circle  on the current weekday"""
            if (week_starts_on == "Monday"):
                calendar.setfirstweekday(calendar.MONDAY)
                image.paste(weekmon, weekplace)
                draw(weekdaysmon[(time.strftime("%a"))], weekday)

            if (week_starts_on == "Sunday"):
                calendar.setfirstweekday(calendar.SUNDAY)
                image.paste(weeksun, weekplace)
                draw(weekdayssun[(time.strftime("%a"))], weekday)

            """Using the built-in calendar function, draw icons for each
               number of the month (1,2,3,...28,29,30)"""
            cal = calendar.monthcalendar(time.year, time.month)
            #print(cal) #-uncomment for debugging with incorrect dates

            for numbers in cal[0]:
                image.paste(im_open(dpath+str(numbers)+'.jpeg'), positions['a'+str(cal[0].index(numbers)+1)])
            for numbers in cal[1]:
                image.paste(im_open(dpath+str(numbers)+'.jpeg'), positions['b'+str(cal[1].index(numbers)+1)])
            for numbers in cal[2]:
                image.paste(im_open(dpath+str(numbers)+'.jpeg'), positions['c'+str(cal[2].index(numbers)+1)])
            for numbers in cal[3]:
                image.paste(im_open(dpath+str(numbers)+'.jpeg'), positions['d'+str(cal[3].index(numbers)+1)])
            for numbers in cal[4]:
                image.paste(im_open(dpath+str(numbers)+'.jpeg'), positions['e'+str(cal[4].index(numbers)+1)])
            try:
                for numbers in cal[5]:
                    image.paste(im_open(dpath+str(numbers)+'.jpeg'), positions['f'+str(cal[5].index(numbers)+1)])
            except IndexError:
                pass

            """Custom function to display text on the E-Paper.
            Tuple refers to the x and y coordinates of the E-Paper display,
            with (0, 0) being the top left corner of the display."""
            def write_text(box_width, box_height, text, tuple):
                text_width, text_height = font.getsize(text)
                if (text_width, text_height) > (box_width, box_height):
                    raise ValueError('Sorry, your text is too big for the box')
                else:
                    x = int((box_width / 2) - (text_width / 2))
                    y = int((box_height / 2) - (text_height / 2))
                    space = Image.new('L', (box_width, box_height), color=255)
                    ImageDraw.Draw(space).text((x, y), text, fill=0, font=font)
                    image.paste(space, tuple)

            """ Handling Openweathermap API"""
            print("Connecting to Openweathermap API servers...")
            owm = pyowm.OWM(api_key)
            if owm.is_API_online() is True:
                observation = owm.weather_at_place(location)
                print("weather data:")
                weather = observation.get_weather()
                weathericon = weather.get_weather_icon_name()
                Humidity = str(weather.get_humidity())
                cloudstatus = str(weather.get_clouds())
                weather_description = (str(weather.get_status()))

                if units == "metric":
                    Temperature = str(int(weather.get_temperature(unit='celsius')['temp']))
                    windspeed = str(int(weather.get_wind()['speed']))
                    write_text(50, 35, Temperature + " °C", (334, 0))
                    write_text(100, 35, windspeed+" km/h", (114, 0))

                if units == "imperial":
                    Temperature = str(int(weather.get_temperature('fahrenheit')['temp']))
                    windspeed = str(int(weather.get_wind()['speed']*0.621))
                    write_text(50, 35, Temperature + " °F", (334, 0))
                    write_text(100, 35, windspeed+" mph", (114, 0))

                if hours == "24":
                    sunrisetime = str(datetime.fromtimestamp(int(weather.get_sunrise_time(timeformat='unix'))).strftime('%-H:%M'))
                    sunsettime = str(datetime.fromtimestamp(int(weather.get_sunset_time(timeformat='unix'))).strftime('%-H:%M'))

                if hours == "12":
                    sunrisetime = str(datetime.fromtimestamp(int(weather.get_sunrise_time(timeformat='unix'))).strftime('%-I:%M'))
                    sunsettime = str(datetime.fromtimestamp(int(weather.get_sunset_time(timeformat='unix'))).strftime('%-I:%M'))

                print('Temperature: '+Temperature+' °C')
                print('Humidity: '+Humidity+'%')
                print('Icon code: '+weathericon)
                print('weather-icon name: '+weathericons[weathericon])
                print('Wind speed: '+windspeed+'km/h')
                print('Sunrise-time: '+sunrisetime)
                print('Sunset time: '+sunsettime)
                print('Cloudiness: ' + cloudstatus+'%')
                print('Weather description: '+weather_description+'\n')

                """Drawing the fetched weather icon"""
                image.paste(im_open(wpath+weathericons[weathericon]+'.jpeg'), wiconplace)

                """Drawing the fetched temperature"""
                image.paste(tempicon, tempplace)

                """Drawing the fetched humidity"""
                image.paste(humicon, humplace)
                write_text(50, 35, Humidity + " %", (334, 35))

                """Drawing the fetched sunrise time"""
                image.paste(sunriseicon, sunriseplace)
                write_text(50, 35, sunrisetime, (249, 0))

                """Drawing the fetched sunset time"""
                image.paste(sunseticon, sunsetplace)
                write_text(50, 35, sunsettime, (249, 35))

                """Drawing the wind icon"""
                image.paste(windicon, windiconspace)

                """Write a short weather description"""
                write_text(144, 35, weather_description, (70, 35))

            else:
                image.paste(no_response, wiconplace)

            """Filter upcoming events from your iCalendar/s"""
            print('Fetching events from your calendar'+'\n')
            events_this_month = []
            upcoming = []
            for icalendars in ical_urls:
                decode = str(urlopen(icalendars).read().decode())
                #fix a bug related to Alarm action by replacing parts of the icalendar
                fix_e = decode.replace('BEGIN:VALARM\r\nACTION:NONE','BEGIN:VALARM\r\nACTION:DISPLAY\r\nDESCRIPTION:')
                #uncomment line below to display your calendar in ical format
                #print(fix_e)
                ical = Calendar(fix_e)
                for events in ical.events:
                    if time.now().strftime('%-m %Y') == (events.begin).format('M YYYY') and (events.begin).format('DD') >= time.now().strftime('%d'):
                        upcoming.append({'date':events.begin.format('DD MMM'), 'event':events.name})
                        events_this_month.append(int((events.begin).format('D')))
                    if month == 12:
                        if (1, year+1) == (1, int((events.begin).year)):
                            upcoming.append({'date':events.begin.format('DD MMM'), 'event':events.name})
                    if month != 12:
                        if (month+1, year) == (events.begin).format('M YYYY'):
                            upcoming.append({'date':events.begin.format('DD MMM'), 'event':events.name}) # HS sort events by date

            def takeDate(elem):
                return elem['date']

            upcoming.sort(key=takeDate)

            del upcoming[4:]
            # uncomment the following 2 lines to display the fetched events
            # from your iCalendar
            print('Upcoming events:')
            print(upcoming)

            #Credit to Hubert for suggesting truncating event names
            def write_text_left(box_width, box_height, text, tuple):
                text_width, text_height = font.getsize(text)
                while (text_width, text_height) > (box_width, box_height):
                    text=text[0:-1]
                    text_width, text_height = font.getsize(text)
                y = int((box_height / 2) - (text_height / 2))
                space = Image.new('L', (box_width, box_height), color=255)
                ImageDraw.Draw(space).text((0, y), text, fill=0, font=font)
                image.paste(space, tuple)

            """Write event dates and names on the E-Paper"""
            for dates in range(len(upcoming)):
                write_text(70, 25, (upcoming[dates]['date']), date_positions['d'+str(dates+1)])

            for events in range(len(upcoming)):
                write_text_left(314, 25, (upcoming[events]['event']), event_positions['e'+str(events+1)])

            """Draw smaller squares on days with events"""
            for numbers in events_this_month:
                if numbers in cal[0]:
                    draw(positions['a'+str(cal[0].index(numbers)+1)], eventicon)
                if numbers in cal[1]:
                    draw(positions['b'+str(cal[1].index(numbers)+1)], eventicon)
                if numbers in cal[2]:
                    draw(positions['c'+str(cal[2].index(numbers)+1)], eventicon)
                if numbers in cal[3]:
                    draw(positions['d'+str(cal[3].index(numbers)+1)], eventicon)
                if numbers in cal[4]:
                    draw(positions['e'+str(cal[4].index(numbers)+1)], eventicon)
                try:
                    if numbers in cal[5]:
                        draw(positions['f'+str(cal[5].index(numbers)+1)], eventicon)
                except IndexError:
                    pass

            """Draw a larger square on today's date"""
            today = time.day
            if today in cal[0]:
                draw(positions['a'+str(cal[0].index(today)+1)], dateicon)
            if today in cal[1]:
                draw(positions['b'+str(cal[1].index(today)+1)], dateicon)
            if today in cal[2]:
                draw(positions['c'+str(cal[2].index(today)+1)], dateicon)
            if today in cal[3]:
                draw(positions['d'+str(cal[3].index(today)+1)], dateicon)
            if today in cal[4]:
                draw(positions['e'+str(cal[4].index(today)+1)], dateicon)
            try:
                if today in cal[5]:
                    draw(positions['f'+str(cal[5].index(today)+1)], dateicon)
            except IndexError:
                pass

            print('Initialising E-Paper Display')
            epd.init()
            sleep(5)
            print('Converting image to data and sending it to the display')
            print('This may take a while...'+'\n')
            epd.display_frame(epd.get_frame_buffer(image.rotate(270, expand=1)))
            # Uncomment following line to save image
            #image.save(path+'test.png')
            del events_this_month[:]
            del upcoming[:]
            print('Data sent successfully')
            print('Powering off the E-Paper until the next loop'+'\n')
            epd.sleep()

            for i in range(1):
                nexthour = ((60 - int(time.strftime("%-M")))*60) - (int(time.strftime("%-S")))
                sleep(nexthour)

if __name__ == '__main__':
    main()
