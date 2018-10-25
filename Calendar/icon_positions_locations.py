#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PIL import Image, ImageFont
from settings import *
open = Image.open

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
no_response=            open(opath+'cloud-no-response.bmp')

wiconplace = (570, 219)
tempplace = (605, 310)
humplace = (572, 308)
monthplace = (443, 0)
weekplace = (415,0)
seperatorplace = (555, 0)

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
