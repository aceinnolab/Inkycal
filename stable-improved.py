#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
E-Paper Software (main script) for the 3-colour and 2-Colour E-Paper display
A full and detailed breakdown for this code can be found in the wiki.
If you have any questions, feel free to open an issue at Github.

Copyright by Ace-Laboratory
"""
print('importing modules'+'\n')
from settings import *
from icon_positions_locations import *

from PIL import Image, ImageDraw, ImageFont, ImageOps
import calendar,  pyowm
from ics import Calendar, Event
from datetime import datetime
from time import sleep
from urllib.request import urlopen
import arrow


if display_colours == "bwr":
    import epd7in5b
    epd = epd7in5b.EPD()
    from calibration import calibration

if display_colours == "bw":
    import epd7in5
    epd = epd7in5.EPD()
    from calibration_bw import calibration

c = Calendar(urlopen(url).read().decode('UTF-8'))
e = Event()
EPD_WIDTH = 640
EPD_HEIGHT = 384


def main():
    while True:
        
        time = datetime.now()
        hour = int(time.strftime("%-H"))
        
        for i in range(1):
            """At the following hours (midnight, midday and 6 pm), perform
               a calibration of the display's colours"""
            if (hour is 0) or (hour is 12) or (hour is 18):
                print('performing calibration now')
                calibration()

            print('Current date:',time.strftime('%a %-d %b %y'))
            print('Current time:', time.strftime('%H:%M')+'\n')
            
            """Create a blank page"""
            image = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), 255)
            draw = (ImageDraw.Draw(image)).bitmap

            """Draw the icon showing the current month"""
            draw(monthplace, Image.open(mpath+str(time.strftime("%B"))+'.bmp'))

            """Draw the 3 lines that seperates the top section"""
            draw(seperatorplace, seperator)

            """Draw the icons with the weekday-names (Mon, Tue...) and
               draw a circle  on the current weekday"""
            if (week_starts_on == "Monday"):
                calendar.setfirstweekday(calendar.MONDAY)
                draw(weekplace, weekmon)
                draw(weekdaysmon[(time.strftime("%a"))], weekday)

            if (week_starts_on == "Sunday"):
                calendar.setfirstweekday(calendar.SUNDAY)
                draw(weekplace, weeksun)
                draw(weekdayssun[(time.strftime("%a"))], weekday)

            """Using the built-in calendar function, draw icons for each
               number of the month (1,2,3,...28,29,30)"""
            cal = calendar.monthcalendar(time.year, time.month)
            #print(cal) #-uncomment for debugging with incorrect dates

            for i in cal[0]:
                draw(positions['a'+str(cal[0].index(i)+1)] ,open(dpath+str(i)+'.bmp'))
            for i in cal[1]:
                draw(positions['b'+str(cal[1].index(i)+1)] ,open(dpath+str(i)+'.bmp'))
            for i in cal[2]:
                draw(positions['c'+str(cal[2].index(i)+1)] ,open(dpath+str(i)+'.bmp'))
            for i in cal[3]:
                draw(positions['d'+str(cal[3].index(i)+1)] ,open(dpath+str(i)+'.bmp'))
            for i in cal[4]:
                draw(positions['e'+str(cal[4].index(i)+1)] ,open(dpath+str(i)+'.bmp'))
            try:
                for i in cal[5]:
                    draw(positions['f'+str(cal[5].index(i)+1)] ,Image.open(dpath+str(i)+'.bmp'))
            except IndexError:
                pass
            
            """ Handling Openweathermap API"""
            try:
                print("Preparing to fetch data from openweathermap API")
                owm = pyowm.OWM(api_key)
                observation = owm.weather_at_place(location)
                print("Fetching weather data...")
                weather = observation.get_weather()
                weathericon = weather.get_weather_icon_name()
                
                Temperature = str(int(weather.get_temperature(unit='celsius')['temp']))
                Humidity = str(weather.get_humidity())
                print('temperature: '+Temperature +' °C')
                print('humidity: '+Humidity+'%')
                print('fetched icon code: '+weathericon)
                print('equivalent to icon: '+weathericons[weathericon]+'\n')
                
                """Drawing the fetched weather icon"""
                draw(wiconplace, open(wpath+weathericons[weathericon]+'.bmp'))

                """Drawing the fetched temperature"""
                space2 = Image.new('1', (50,35), color=255)
                temperature = ImageDraw.Draw(space2)
                temperature.text((2, 8), (Temperature + " °C"),  fill=0 ,font=font)
                rotate2 = space2.rotate(270,  expand=1)
                image.paste(rotate2, (605,334))

                """Drawing the fetched humidity"""
                space3 = Image.new('1', (50,35), color=255)
                humidity = ImageDraw.Draw(space3)
                humidity.text((4, 8), (Humidity +'%'),  fill=0 ,font=font)
                rotate3 = space3.rotate(270,  expand=1)
                image.paste(rotate3, (570,334))
                
            except Exception as e:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)
                print("************ OWM DID NOT RESPOND *************")
                print("Drawing the 'no-response' icon on the display now")
                draw(wiconplace, no_response)
                pass

            """Drawing today's date at the top left corner"""
            space1=Image.new('1', (115,25), color=255)
            date = ImageDraw.Draw(space1)
            date.text((2, 3), (time.strftime('%a %-d %b %y')),  font=font, fill=0)
            rotate1 = space1.rotate(270,  expand=1)
            image.paste(rotate1, (595,20))

            """Sort the Events in your iCalendar"""
            print('Fetching upcoming events from your calendar')
            elist = []
            for events in c.events:
                if time.year <= int((events.begin).format('YYYY')):
                    if time.month == int((events.begin).format('M')):
                        elist.append(int((events.begin).format('D')))
            """Uncomment the next 4 lines to print your events on the console"""
#                        if time.day <= int((events.begin).format('D')):
#                           print(events.name+' starts on '+events.begin.format('D '+'MMM '+'YYYY'))
#                    if time.month < int((events.begin).format('M')):
#                        print(events.name+' starts on '+events.begin.format('D '+'MMM '+'YYYY'))

            """Draw circles on any days which include an Event"""
            for x in elist:
                if x in cal[0]:
                    draw(positions['a'+str(cal[0].index(x)+1)] ,eventicon)
                if x in cal[1]:
                    draw(positions['b'+str(cal[1].index(x)+1)] ,eventicon)
                if x in cal[2]:
                    draw(positions['c'+str(cal[2].index(x)+1)] ,eventicon)
                if x in cal[3]:
                    draw(positions['d'+str(cal[3].index(x)+1)] ,eventicon)
                if x in cal[4]:
                    draw(positions['e'+str(cal[4].index(x)+1)] ,eventicon)
                try:
                    if x in cal[5]:
                        draw(positions['f'+str(cal[5].index(x)+1)] ,eventicon)
                except IndexError:
                    pass


            """Draw a square with round corners on the today's date"""
            today = time.day
            if today in cal[0]:
                draw(positions['a'+str(cal[0].index(today)+1)] ,dateicon)
            if today in cal[1]:
                draw(positions['b'+str(cal[1].index(today)+1)] ,dateicon)
            if today in cal[2]:
                draw(positions['c'+str(cal[2].index(today)+1)] ,dateicon)
            if today in cal[3]:
                draw(positions['d'+str(cal[3].index(today)+1)] ,dateicon)
            if today in cal[4]:
                draw(positions['e'+str(cal[4].index(today)+1)] ,dateicon)
            try:
                if today in cal[5]:
                    draw(positions['f'+str(cal[5].index(today)+1)] ,dateicon)
            except IndexError:
                    pass

            draw(tempplace, tempicon)
            draw(humplace, humicon)

            print('\n'+'initialising E-Paper Display')
            epd.init()
            sleep(5)
            print('Converting image to data and sending it to the display...'+'\n')
            epd.display_frame(epd.get_frame_buffer(image))

            # delete the list so deleted events can be removed from the list
            del elist[:]
            print('data sent successfully'+'\n')
            print('letting the display sleep until the next hour')
            epd.sleep()
            
            for i in range(1):
                nexthour = ((60 - int(time.strftime("%-M")))*60) - (int(time.strftime("%-S")))
                sleep(nexthour)

if __name__ == '__main__':
    main()
