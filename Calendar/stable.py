#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
E-Paper Software (main script) for the 3-colour and 2-Colour E-Paper display
A full and detailed breakdown for this code can be found in the wiki.
If you have any questions, feel free to open an issue at Github.

Copyright by Ace-Laboratory
"""
from settings import *

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

if (week_starts_on == "Monday"):
    calendar.setfirstweekday(calendar.MONDAY)
    
if (week_starts_on == "Sunday"):
    calendar.setfirstweekday(calendar.Sunday)

c = Calendar(urlopen(url).read().decode('UTF-8'))
e = Event()
open = Image.open
EPD_WIDTH = 640
EPD_HEIGHT = 384

path = '/home/pi/E-Paper-Master/Calendar/'
wpath = path+'weather-icons/'
mpath = path+'months/'+language+'/'
dpath = path+'days/'
opath = path+'other/'+language+'/'
font = ImageFont.truetype(path+'Assistant-Bold.ttf', 18)

weekday =               open(opath+'weekday.bmp')
eventicon =             open(opath+'event.bmp')
dateicon =              open(opath+'today.bmp')
tempicon =              open(opath+'temp-icon.bmp')
humicon =               open(opath+'hum-icon.bmp')
weekmon =               open(opath+'week-mon.bmp')
weeksun =               open(opath+'week-sun.bmp')
seperator =             open(opath+'seperator.bmp')

wiconplace = (570, 219)
tempplace = (605, 310)
humplace = (572, 308)
monthplace = (443, 0)
weekplace = (415,0)
seperator_place = (555, 0)

weekdaysmon = {'Mon': (416,3), 'Tue': (416,57), 'Wed': (416,111), 'Thu': (416,165), 'Fri': (416,219), 'Sat': (416,273), 'Sun':(416,327)}
weekdayssun = {'Sun': (416,3), 'Mon': (416,57), 'Tue': (416,111), 'Wed': (416,165), 'Thu': (416,219), 'Fri': (416,273), 'Sat':(416,327)}

positions = {'a1': (351, 3), 'a2': (351, 57), 'a3': (351, 111), 'a4': (351, 165),  'a5': (351, 219), 'a6': (351, 273), 'a7': (351, 327),
'b1': (284, 3), 'b2': (284, 57), 'b3': (284, 111), 'b4': (284, 165), 'b5': (284, 219), 'b6': (284, 273), 'b7': (284, 327),
'c1': (217, 3), 'c2': (217, 57), 'c3': (217, 111), 'c4': (217, 165), 'c5': (217, 219), 'c6': (217, 273), 'c7': (217, 327),
'd1': (150, 3), 'd2': (150, 57), 'd3': (150, 111), 'd4': (150, 165), 'd5': (150, 219), 'd6': (150, 273), 'd7': (150, 327),
'e1': (83, 3), 'e2': (83, 57), 'e3': (83, 111), 'e4': (83, 165), 'e5': (83, 219), 'e6': (83, 273), 'e7': (83, 327),
'f1': (16, 3), 'f2': (16, 57), 'f3': (16, 111), 'f4': (16, 165), 'f5': (16, 219), 'f6': (16, 273), 'f7': (16, 327)}

weathericons = {'01d': 'wi-day-sunny', '02d':'wi-day-cloudy', '03d': 'wi-cloudy',
'04d': 'wi-cloudy-windy', '09d': 'wi-showers', '10d':'wi-rain',
'11d':'wi-thunderstorm', '13d':'wi-snow', '50d': 'wi-fog',
'01n': 'wi-night-clear', '02n':'wi-night-cloudy',
'03n': 'wi-night-cloudy', '04n': 'wi-night-cloudy',
'09n': 'wi-night-showers', '10n':'wi-night-rain',
'11n':'wi-night-thunderstorm', '13n':'wi-night-snow',
'50n': 'wi-night-alt-cloudy-windy'}

def main():
    while True:
        
        time = datetime.now()
        hour = int(time.strftime("%-H"))
        
        for i in range(1):
            if hour is 0:
                calibration()
            if hour is 12:
                calibration()
            if hour is 18:
                calibration()
            epd.init()
            image = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), 255)
            draw = (ImageDraw.Draw(image)).bitmap
            
            #background image
            draw(monthplace, Image.open(mpath+str(time.strftime("%B"))+'.bmp'))

            if calendar.firstweekday() == 0:
                #print('Your week starts on Monday') #->debug
                draw(weekplace, weekmon)
                
            if calendar.firstweekday() == 6:
                #print('Your week starts on Sunday') #->debug
                draw(weekplace, weeksun)
            
            draw(seperatorplace, seperator) 

            cal = calendar.monthcalendar(time.year, time.month)

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
            
            # openweathermap api
            try:
                print("Before fetching owm data")
                owm = pyowm.OWM(api_key)
                observation = owm.weather_at_place(location)
                print("Fetching weather data...")
                weather = observation.get_weather()
                weathericon = weather.get_weather_icon_name()
            except Exception as e:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)
                print("************ OWM DID NOT RESPOND *************")
                pass
            Temperature = str(int(weather.get_temperature(unit='celsius')['temp']))
            Humidity = str(weather.get_humidity())
            print('temp: '+Temperature +' °C') #->debug
            print('humidity: '+Humidity+'%') #->debug
            print(weathericon)              #->debug
            
            #weather icon handler
            draw(wiconplace, open(wpath+weathericons[weathericon]+'.bmp'))

            # date writing function
            space1=Image.new('1', (115,25), color=255)
            measure1= ImageDraw.Draw(space1)
            date = ImageDraw.Draw(space1)
            date.text((2, 3), (time.strftime('%a %-d %b %y')),  font=font, fill=0)
            rotate1 = space1.rotate(270,  expand=1)
            image.paste(rotate1, (595,20))

            # temperature writing function
            space2 = Image.new('1', (50,35), color=255)
            measure2= ImageDraw.Draw(space2)
            temperature = ImageDraw.Draw(space2)
            temperature.text((2, 8), (Temperature + " °C"),  fill=0 ,font=font)
            #if you come across a 'Non-ASCII' Syntax error and comment out the line above and uncomment the line below.
            #This is for advanced users who want to experiment with encodings.
            #temperature.text((2, 8), (Temperature + u'\xb0' + "C"), fill=0 ,font=font)
            rotate2 = space2.rotate(270,  expand=1)
            image.paste(rotate2, (605,334))

            # humidity writing function
            space3 = Image.new('1', (50,35), color=255)
            measure3= ImageDraw.Draw(space3)
            humidity = ImageDraw.Draw(space3)
            humidity.text((4, 8), (Humidity +'%'),  fill=0 ,font=font)
            rotate3 = space3.rotate(270,  expand=1)
            image.paste(rotate3, (570,334))

            # weekday handler
            if calendar.firstweekday() == 0:
                draw(weekdaysmon[(time.strftime("%a"))], weekday)
                
            if calendar.firstweekday() == 6:
                draw(weekdayssun[(time.strftime("%a"))], weekday)
            
            print('It is currently:',time.strftime('%a %-d %b %y')) #--debug
            print('The current time is:', time.strftime('%H:%M')) #--debug
    
            elist = []
            for events in c.events:
                if str(time.year) in str((events.begin).format('YYYY')):
                    if str(time.month) in str((events.begin).format('M')):
                        elist.append(int((events.begin).format('D')))

            print('In this month, you have',len(elist),'Events')
            
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
            epd.display_frame(epd.get_frame_buffer(image))

            # delete the list so deleted events can be removed from the list
            del elist[:]
            epd.sleep()
            
            for i in range(1):
                nexthour = ((60 - int(time.strftime("%-M")))*60) - (int(time.strftime("%-S")))
                sleep(nexthour)

if __name__ == '__main__':
    main()
