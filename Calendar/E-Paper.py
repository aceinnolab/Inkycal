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
import arrow
import re
import random
import gc
import feedparser
import numpy as np

from settings import *
from image_data import *

from PIL import Image, ImageDraw, ImageFont, ImageOps
import pyowm
from ics import Calendar
try:
    from urllib.request import urlopen
except Exception as e:
    print("Something didn't work right, maybe you're offline?"+e.reason)

import e_paper_drivers
epd = e_paper_drivers.EPD()

from calibration import calibration

EPD_WIDTH = 640
EPD_HEIGHT = 384
default = ImageFont.truetype(path+'Assistant-Regular.ttf', 18)
semi = ImageFont.truetype(path+'Assistant-SemiBold.ttf', 18)
bold = ImageFont.truetype(path+'Assistant-Bold.ttf', 18)
im_open = Image.open

owm = pyowm.OWM(api_key)

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

            """Custom function to display text on the E-Paper"""
            def write_text(box_width, box_height, text, tuple, font=default, alignment='middle'):
                text_width, text_height = font.getsize(text)
                while (text_width, text_height) > (box_width, box_height):
                    text=text[0:-1]
                    text_width, text_height = font.getsize(text)
                if alignment is "" or "middle" or None:
                    x = int((box_width / 2) - (text_width / 2))
                if alignment is 'left':
                    x = 0
                y = int((box_height / 2) - (text_height / 2))
                space = Image.new('RGB', (box_width, box_height), color='white')
                ImageDraw.Draw(space).text((x, y), text, fill='black', font=font)
                image.paste(space, tuple)

            """Connect to Openweathermap API and fetch weather data"""
            if top_section is "Weather" and api_key != "" and owm.is_API_online() is True:
                print("Connecting to Openweathermap API servers...")
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

                """Show the fetched weather data"""
                print('Temperature: '+ Temperature+' °C')
                print('Humidity: '+ Humidity+'%')
                print('weather-icon name: '+weathericons[weathericon])
                print('Wind speed: '+ windspeed+'km/h')
                print('Sunrise-time: '+ sunrisetime)
                print('Sunset time: '+ sunsettime)
                print('Cloudiness: ' + cloudstatus+'%')
                print('Weather description: '+ weather_description+'\n')

                """Add the weather icon at the top left corner"""
                image.paste(im_open(wpath + weathericons[weathericon] +'.jpeg'), wiconplace)

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

            """Using the built-in calendar to generate the monthly Calendar
            template"""
            cal = calendar.monthcalendar(time.year, time.month)
                
            if middle_section is "Calendar":
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

                """Create the calendar template of the current month"""
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
                if len(cal) is 6 and today in cal[5]:
                    image.paste(dateicon, positions['f'+str(cal[5].index(today)+1)], dateicon)

            """Add rss-feeds at the bottom section of the Calendar"""
            if bottom_section is "RSS" and rss_feeds != []:
                def multiline_text(text, max_width, font=default):
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

                """Parse the RSS-feed titles and save them to a list"""
                rss_feed = []
                for feeds in rss_feeds:
                    text = feedparser.parse(feeds)
                    for posts in text.entries:
                        rss_feed.append(posts.summary)#title

                """Shuffle the list to prevent displaying the same titles over and over"""
                random.shuffle(rss_feed)
                news = []

                """Remove all titles except the first 4 or 6,
                depenfing on how much space is available on the """
                if middle_section is 'Calendar' and len(cal) is 5 or middle_section is 'Agenda':
                    del rss_feed[6:]

                if len(cal) is 6:
                    del rss_feed[4:]

                """Split titles of the rss feeds into lines that can fit
                on the Calendar and add them to a list"""
                for title in range(len(rss_feeds)):
                    news.append(multiline_text(rss_feed[title], 384))

                news = [j for i in news for j in i]

                """Display the split lines of the titles"""
                if middle_section is 'Calendar' and len(cal) is 5 or middle_section is 'Agenda':
                    if len(news) > 6:
                        del news[6:]
                    for lines in range(len(news)):
                        write_text(384, 25, news[lines], rss_places['line_'+str(lines+1)], alignment = 'left')

                if len(cal) is 6:
                    if len(news) > 4:
                        del news[4:]
                    for lines in range(len(news)):
                        write_text(384, 25, news[lines], rss_places['line_'+str(lines+3)], alignment = 'left')


            if middle_section is "Calendar" or "Agenda":
                """Algorithm for filtering and sorting events from your
                iCalendar/s"""
                print('Fetching events from your calendar'+'\n')
                events_this_month = []
                upcoming = []
                now = arrow.now()
                today = time.today()

                """Create a time span using the events_max_range value (in days)
                to filter events in that range"""
                agenda_max_days = arrow.now().replace(days=+22)
                calendar_max_days = arrow.now().replace(days=+int(events_max_range))
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
                                        upcoming.append(events)
                                        if i.day not in events_this_month:
                                            events_this_month.append(i.day)
                                   # uncomment this line to see fetched recurring events
                                   #print ("Appended recurring event: " + events.name + " on " + str(time.now().year) + " " + time.now().strftime('%m')+ " " + str(i.day).zfill(2))
                        else:
                            if events.begin.date().year == today.year and events.begin.date().month is today.month and int((events.begin).format('D')) not in events_this_month:
                                events_this_month.append(int((events.begin).format('D')))
                            if middle_section is 'Agenda' and events in ical.timeline.included(now, agenda_max_days):
                                upcoming.append(events)
                            if middle_section is 'Calendar' and events in ical.timeline.included(now, calendar_max_days):
                                upcoming.append(events)

                def event_begins(elem):
                    return elem.begin

                upcoming.sort(key=event_begins)

                if middle_section is 'Agenda':
                    """For the agenda view, create a list containing dates and events of the next 22 days"""
                    if len(upcoming) is not 0:
                        while (upcoming[-1].begin.date().day - now.day) + len(upcoming) >= 22:
                            del upcoming[-1]
                    agenda_list = []
                    for i in range(22):
                        date = now.replace(days=+i)
                        agenda_list.append({'value':date.format('ddd D MMM YY'),'type':'date'})
                        for events in upcoming:
                            if events.begin.date().day == date.day:
                                if not events.all_day:
                                    agenda_list.append({'value':events.begin.format('HH:mm')+ ' '+ str(events.name), 'type':'timed_event'})
                                else:
                                    agenda_list.append({'value':events.name, 'type':'full_day_event'})

                    if bottom_section is not "":
                        del agenda_list[16:]
                        image.paste(seperator2, agenda_view_lines['line17'])

                    if bottom_section is "":
                        del agenda_list[22:]
                        image.paste(seperator2, agenda_view_lines['line22'])

                    for lines in range(len(agenda_list)):
                        if agenda_list[lines]['type'] is 'date':
                            write_text(384, 25, agenda_list[lines]['value'], agenda_view_lines['line'+str(lines+1)], font=bold, alignment='left')
                            image.paste(seperator2, agenda_view_lines['line'+str(lines+1)])
                        elif agenda_list[lines]['type'] is 'timed_event':
                            write_text(384, 25, agenda_list[lines]['value'], agenda_view_lines['line'+str(lines+1)], alignment='left')
                        else:
                            write_text(384, 25, agenda_list[lines]['value'], agenda_view_lines['line'+str(lines+1)])
      
            if middle_section is 'Calendar':
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
                    if len(cal) is 6 and numbers in cal[5]:
                        image.paste(eventicon, positions['f'+str(cal[5].index(numbers)+1)], eventicon)

            """Write event dates and names on the E-Paper"""
            if bottom_section is "Events":
                if len(cal) is 5:
                    del upcoming[6:]
                    for dates in range(len(upcoming)):
                        readable_date = datetime.strptime(upcoming[dates]['date'], '%Y %m %d').strftime('%-d %b')
                        write_text(70, 25, readable_date, date_positions['d'+str(dates+1)])
                    for events in range(len(upcoming)):
                        write_text(314, 25, (upcoming[events]['event']), event_positions['e'+str(events+1)], alignment = 'left')

                if len(cal) is 6:
                    del upcoming[4:]
                    for dates in range(len(upcoming)):
                        readable_date = datetime.strptime(upcoming[dates]['date'], '%Y %m %d').strftime('%-d %b')
                        write_text(70, 25, readable_date, date_positions['d'+str(dates+3)])
                    for events in range(len(upcoming)):
                        write_text(314, 25, (upcoming[events]['event']), event_positions['e'+str(events+3)], alignment = 'left')

            
            """
            Map all pixels of the generated image to red, white and black
            so that the image can be displayed 'correctly' on the E-Paper
            """
            buffer = np.array(image)
            r,g,b = buffer[:,:,0], buffer[:,:,1], buffer[:,:,2]
            if display_colours is "bwr":
                buffer[np.logical_and(r > 240, g > 240)] = [255,255,255] #white
                buffer[np.logical_and(r > 240, g < 240)] = [255,0,0] #red
                buffer[np.logical_and(r != 255, r == g )] = [0,0,0] #black

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

            #if middle_section is 'Calendar':
            del events_this_month
            del upcoming

            if bottom_section is 'RSS':
                del rss_feed
                del news
                
            if middle_section is 'Agenda':
                del agenda_list

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
