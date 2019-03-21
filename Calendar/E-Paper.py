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
from datetime import datetime, date, timedelta
from time import sleep
from dateutil.rrule import *
from dateutil.parser import parse
import re
import random
import gc

try:
    import feedparser
except ImportError:
    print("Please install feedparser with: sudo pip3 install feedparser")
    print("and")
    print("pip3 install feedparser")

try:
    import numpy as np
except ImportError:
    print("Please install numpy with: sudo apt-get install python3-numpy")

from settings import *
from icon_positions_locations import *

from PIL import Image, ImageDraw, ImageFont, ImageOps
import pyowm
from ics import Calendar
try:
    from urllib.request import urlopen
except Exception as e:
    print("Something didn't work right, maybe you're offline?"+e.reason)

if display_colours is "bwr":
    import epd7in5b
    epd = epd7in5b.EPD()

if display_colours is "bw":
    import epd7in5
    epd = epd7in5.EPD()

from calibration import calibration

EPD_WIDTH = 640
EPD_HEIGHT = 384
font = ImageFont.truetype(path+'Assistant-Regular.ttf', 18)
im_open = Image.open

owm = pyowm.OWM(api_key)

possible_update_values = [10, 15, 20, 30, 60]
if int(update_interval) not in possible_update_values:
    print('Selected update-interval: ',update_interval, 'minutes')
    print('Please select an update interval from these values:', possible_update_values)
    raise ValueError

"""Main loop starts from here"""
def main():
    calibration_countdown = 'initial'
    while True:
        time = datetime.now()
        hour = int(time.strftime("%-H"))
        month = int(time.now().strftime('%-m'))
        year = int(time.now().strftime('%Y'))
        mins = int(time.strftime("%M"))
        seconds = int(time.strftime("%S"))

        for i in range(1):
            print('_________Starting new loop___________'+'\n')

            """Start by printing the date and time for easier debugging"""
            print('Date:', time.strftime('%a %-d %b %y'), 'Time: '+time.strftime('%H:%M')+'\n')

            """At the hours specified in the settings file,
            calibrate the display to prevent ghosting"""
            if hour in calibration_hours:
                if calibration_countdown is 'initial':
                    calibration_countdown = 0
                    calibration()
                else:
                    if calibration_countdown % (60 // int(update_interval)) is 0:
                        calibration()
                        calibration_countdown = 0

            """Create a blank white page first"""
            image = Image.new('RGB', (EPD_HEIGHT, EPD_WIDTH), 'white')

            """Add the icon with the current month's name"""
            image.paste(im_open(mpath+str(time.strftime("%B")+'.jpeg')), monthplace)

            """Add the line seperating the weather and Calendar section"""
            image.paste(seperator, seperatorplace)

            """Add weekday-icons (Mon, Tue...) and draw a circle on the
            current weekday"""
            if (week_starts_on is "Monday"):
                calendar.setfirstweekday(calendar.MONDAY)
                image.paste(weekmon, weekplace)
                image.paste(weekday, weekdaysmon[(time.strftime("%a"))], weekday)

            """For those whose week starts on Sunday, change accordingly"""
            if (week_starts_on is "Sunday"):
                calendar.setfirstweekday(calendar.SUNDAY)
                image.paste(weeksun, weekplace)
                image.paste(weekday, weekdayssun[(time.strftime("%a"))], weekday)

            """Using the built-in calendar function, draw icons for each
               number of the month (1,2,3,...28,29,30)"""
            cal = calendar.monthcalendar(time.year, time.month)

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
            if len(cal) is 6:
                for numbers in cal[5]:
                    image.paste(im_open(dpath+str(numbers)+'.jpeg'), positions['f'+str(cal[5].index(numbers)+1)])

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
                    space = Image.new('RGB', (box_width, box_height), color='white')
                    ImageDraw.Draw(space).text((x, y), text, fill='black', font=font)
                    image.paste(space, tuple)

            """Connect to Openweathermap API to fetch weather data"""
            print("Connecting to Openweathermap API servers...")
            if owm.is_API_online() is True:
                observation = owm.weather_at_place(location)
                print("weather data:")
                weather = observation.get_weather()
                weathericon = weather.get_weather_icon_name()
                Humidity = str(weather.get_humidity())
                cloudstatus = str(weather.get_clouds())
                weather_description = (str(weather.get_status()))

                if units is "metric":
                    Temperature = str(int(weather.get_temperature(unit='celsius')['temp']))
                    windspeed = str(int(weather.get_wind()['speed']))
                    write_text(50, 35, Temperature + " °C", (334, 0))
                    write_text(100, 35, windspeed+" km/h", (114, 0))

                if units is "imperial":
                    Temperature = str(int(weather.get_temperature('fahrenheit')['temp']))
                    windspeed = str(int(weather.get_wind()['speed']*0.621))
                    write_text(50, 35, Temperature + " °F", (334, 0))
                    write_text(100, 35, windspeed+" mph", (114, 0))

                if hours is "24":
                    sunrisetime = str(datetime.fromtimestamp(int(weather.get_sunrise_time(timeformat='unix'))).strftime('%-H:%M'))
                    sunsettime = str(datetime.fromtimestamp(int(weather.get_sunset_time(timeformat='unix'))).strftime('%-H:%M'))

                if hours is "12":
                    sunrisetime = str(datetime.fromtimestamp(int(weather.get_sunrise_time(timeformat='unix'))).strftime('%-I:%M'))
                    sunsettime = str(datetime.fromtimestamp(int(weather.get_sunset_time(timeformat='unix'))).strftime('%-I:%M'))

                print('Temperature: '+Temperature+' °C')
                print('Humidity: '+Humidity+'%')
                #print('Icon code: '+weathericon)
                print('weather-icon name: '+weathericons[weathericon])
                print('Wind speed: '+windspeed+'km/h')
                print('Sunrise-time: '+sunrisetime)
                print('Sunset time: '+sunsettime)
                print('Cloudiness: ' + cloudstatus+'%')
                print('Weather description: '+weather_description+'\n')

                """Add the weather icon at the top left corner"""
                image.paste(im_open(wpath+weathericons[weathericon]+'.jpeg'), wiconplace)

                """Add the temperature icon at it's position"""
                image.paste(tempicon, tempplace)

                """Add the humidity icon and display the humidity"""
                image.paste(humicon, humplace)
                write_text(50, 35, Humidity + " %", (334, 35))

                """Add the sunrise icon and display the sunrise time"""
                image.paste(sunriseicon, sunriseplace)
                write_text(50, 35, sunrisetime, (249, 0))

                """Add the sunset icon and display the sunrise time"""
                image.paste(sunseticon, sunsetplace)
                write_text(50, 35, sunsettime, (249, 35))

                """Add the wind icon at it's position"""
                image.paste(windicon, windiconspace)

                """Add a short weather description"""
                write_text(144, 35, weather_description, (70, 35))

            else:
                """If no response was received from the openweathermap
                api server, add the cloud with question mark"""
                image.paste(no_response, wiconplace)

            """Algorithm for filtering and sorting events from your
            iCalendar/s"""
            print('Fetching events from your calendar'+'\n')
            events_this_month = []
            upcoming = []
            today = date.today()

            """Create a time span using the events_max_range value (in days)
            to filter events in that range"""
            time_span = today + timedelta(days=int(events_max_range))

            for icalendars in ical_urls:
                decode = str(urlopen(icalendars).read().decode())
                beginAlarmIndex = 0
                while beginAlarmIndex >= 0:
                    beginAlarmIndex = decode.find('BEGIN:VALARM')
                    if beginAlarmIndex >= 0:
                        endAlarmIndex = decode.find('END:VALARM')
                        decode = decode[:beginAlarmIndex] + decode[endAlarmIndex+12:]
                ical = Calendar(decode)
                for events in ical.events:
                   if re.search('RRULE',str(events)) is not None:
                           r = re.search('RRULE:(.+?)\n',str(events))
                           r_start = re.search('DTSTART:(.+?)\n',str(events))
                           if r_start is not None: # if r_start is None the format of DTSTART is not recognized
                               if time.now().month == 12:
                                   r_string=(r.group(1).rstrip()+';UNTIL='+'%04d%02d%02d'+'T000000Z') % (time.now().year+1, 1, 1)
                               else:
                                   r_string=(r.group(1).rstrip()+';UNTIL='+'%04d%02d%02d'+'T000000Z') % (time.now().year, time.now().month+1, 1)
                               rule=rrulestr(r_string,dtstart=parse(r_start.group(1)))
                               for i in rule:
                                   if i.year == time.now().year and i.month == time.now().month and i.day >= time.now().day:
                                       upcoming.append({'date':str(time.now().year) + " " + time.now().strftime('%m')+ " " + str(i.day).zfill(2), 'event':events.name})
                                       if i.day not in events_this_month:
                                          events_this_month.append(i.day)
                                   # uncomment this line to see fetched recurring events
                                   #print ("Appended recurring event: " + events.name + " on " + str(time.now().year) + " " + time.now().strftime('%m')+ " " + str(i.day).zfill(2))
                   else:
                       if events.begin.date().month == today.month:
                          if int((events.begin).format('D')) not in events_this_month:
                             events_this_month.append(int((events.begin).format('D')))
                       if today <= events.begin.date() <= time_span:
                          upcoming.append({'date':events.begin.format('YYYY MM DD'), 'event':events.name})


            def takeDate(elem):
                return elem['date']

            upcoming.sort(key=takeDate)

            #print('Upcoming events:',upcoming) #Display fetched events

            def write_text_left(box_width, box_height, text, tuple):
                text_width, text_height = font.getsize(text)
                while (text_width, text_height) > (box_width, box_height):
                    text=text[0:-1]
                    text_width, text_height = font.getsize(text)
                y = int((box_height / 2) - (text_height / 2))
                space = Image.new('RGB', (box_width, box_height), color='white')
                ImageDraw.Draw(space).text((0, y), text, fill='black', font=font)
                image.paste(space, tuple)

            """Write event dates and names on the E-Paper"""
            if additional_feature is "events":
                if len(cal) is 5:
                    del upcoming[6:]

                    for dates in range(len(upcoming)):
                        readable_date = datetime.strptime(upcoming[dates]['date'], '%Y %m %d').strftime('%-d %b')
                        write_text(70, 25, readable_date, date_positions['d'+str(dates+1)])
                    for events in range(len(upcoming)):
                        write_text_left(314, 25, (upcoming[events]['event']), event_positions['e'+str(events+1)])

                if len(cal) is 6:
                    del upcoming[4:]

                    for dates in range(len(upcoming)):
                        readable_date = datetime.strptime(upcoming[dates]['date'], '%Y %m %d').strftime('%-d %b')
                        write_text(70, 25, readable_date, date_positions['d'+str(dates+3)])
                    for events in range(len(upcoming)):
                        write_text_left(314, 25, (upcoming[events]['event']), event_positions['e'+str(events+3)])

            """Add rss-feeds at the bottom section of the Calendar"""
            if additional_feature is "rss":

                def multiline_text(text, max_width):
                    lines = []
                    if font.getsize(text)[0] <= max_width:
                        lines.append(text)
                    else:
                        words = text.split(' ')
                        i = 0
                        while i < len(words):
                            line = ''
                            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
                                line = line + words[i] + " "
                                i += 1
                            if not line:
                                line = words[i]
                                i += 1
                            lines.append(line)
                    return lines

                rss_feed = []
                for feeds in rss_feeds:
                    text = feedparser.parse(feeds)
                    for posts in text.entries:
                        rss_feed.append(posts.title)

                random.shuffle(rss_feed)
                news = []

                if len(cal) is 5:
                    del rss_feed[6:]

                if len(cal) is 6:
                    del rss_feed[4:]

                for title in range(len(rss_feeds)):
                    news.append(multiline_text(rss_feed[title], 384))

                news = [j for i in news for j in i]

                if len(cal) is 5:
                    if len(news) > 6:
                        del news[6:]
                    for lines in range(len(news)):
                        write_text_left(384, 25, news[lines], rss_places['line_'+str(lines+1)])

                if len(cal) is 6:
                    if len(news) > 4:
                        del news[4:]
                    for lines in range(len(news)):
                        write_text_left(384, 25, news[lines], rss_places['line_'+str(lines+3)])

            """Draw smaller squares on days with events"""
            for numbers in events_this_month:
                if numbers in cal[0]:
                    image.paste(eventicon, positions['a'+str(cal[0].index(numbers)+1)], eventicon)
                if numbers in cal[1]:
                    image.paste(eventicon, positions['b'+str(cal[1].index(numbers)+1)], eventicon)
                if numbers in cal[2]:
                    image.paste(eventicon, positions['c'+str(cal[2].index(numbers)+1)], eventicon)
                if numbers in cal[3]:
                    image.paste(eventicon, positions['d'+str(cal[3].index(numbers)+1)], eventicon)
                if numbers in cal[4]:
                    image.paste(eventicon, positions['e'+str(cal[4].index(numbers)+1)], eventicon)
                if len(cal) is 6:
                    if numbers in cal[5]:
                        image.paste(eventicon, positions['f'+str(cal[5].index(numbers)+1)], eventicon)

            """Draw a larger square on today's date"""
            today = time.day
            if today in cal[0]:
                image.paste(dateicon, positions['a'+str(cal[0].index(today)+1)], dateicon)
            if today in cal[1]:
                image.paste(dateicon, positions['b'+str(cal[1].index(today)+1)], dateicon)
            if today in cal[2]:
                image.paste(dateicon, positions['c'+str(cal[2].index(today)+1)], dateicon)
            if today in cal[3]:
                image.paste(dateicon, positions['d'+str(cal[3].index(today)+1)], dateicon)
            if today in cal[4]:
                image.paste(dateicon, positions['e'+str(cal[4].index(today)+1)], dateicon)
            if len(cal) is 6:
                if today in cal[5]:
                    image.paste(dateicon, positions['f'+str(cal[5].index(today)+1)], dateicon)

            """
            Map all pixels of the generated image to red, white and black
            so that the image can be displayed 'correctly' on the E-Paper
            """
            buffer = np.array(image)
            r,g,b = buffer[:,:,0], buffer[:,:,1], buffer[:,:,2]
            if display_colours is "bwr":
                buffer[np.logical_and(r > 240, g > 240)] = [255,255,255] #white
                buffer[np.logical_and(r > 240, g < 240)] = [255,0,0] #red
                buffer[np.logical_and(r != 255, r is g )] = [0,0,0] #black

            if display_colours is "bw":
                buffer[np.logical_and(r > 240, g > 240)] = [255,255,255] #white
                buffer[g < 255] = [0,0,0] #black
            
            improved_image = Image.fromarray(buffer).rotate(270, expand=True)
            print('Initialising E-Paper Display')
            epd.init()
            sleep(5)
            print('Converting image to data and sending it to the display')
            epd.display_frame(epd.get_frame_buffer(improved_image))
            print('Data sent successfully')
            print('______Powering off the E-Paper until the next loop______'+'\n')
            epd.sleep()

            del events_this_month
            del upcoming

            if additional_feature is "rss":
                del rss_feed
                del news

            del buffer
            del image
            del improved_image
            gc.collect()

            if calibration_countdown is 'initial':
                    calibration_countdown = 0
            calibration_countdown += 1

            for i in range(1):
                timings = []
                updates_per_hour = 60//int(update_interval)

                for updates in range(updates_per_hour):
                    timings.append(60 - int(update_interval)*updates)

                for update_times in timings:
                    if update_times >= mins:
                        sleep_for_minutes = update_times - mins
                
                next_update_countdown = sleep_for_minutes*60 + (60-seconds)

                print(sleep_for_minutes,'Minutes and ', (60-seconds),'Seconds left until next loop')

                del timings
                sleep(next_update_countdown)

if __name__ == '__main__':
    main()
