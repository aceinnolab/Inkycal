#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PIL import Image, ImageFont
from settings import *
im_open = Image.open

path = '/home/pi/E-Paper-Master/Calendar/'
wpath = path+'weather-icons/'
mpath = path+'months/'+language+'/'
dpath = path+'days/'
opath = path+'other/'+language+'/'
font = ImageFont.truetype(path+'Assistant-Bold.ttf', 18)

weekday =       im_open(opath+'weekday.bmp')
eventicon =     im_open(opath+'event.bmp')
dateicon =      im_open(opath+'today.bmp')
tempicon =      im_open(opath+'temp-icon.bmp')
humicon =       im_open(opath+'hum-icon.bmp')
weekmon =       im_open(opath+'week-mon.bmp')
weeksun =       im_open(opath+'week-sun.bmp')
separator =     im_open(opath+'separator.bmp')
no_response=    im_open(opath+'cloud-no-response.bmp').convert('L')
sunriseicon =   im_open(wpath+'wi-sunrise.bmp').convert('L')
sunseticon =    im_open(wpath+'wi-sunset.bmp').convert('1')
windicon =      im_open(wpath+'wi-strong-wind.bmp').convert('L')

wiconplace = (570, 0)
tempplace = (605, 310)
humplace = (572, 308)
monthplace = (443, 0)
weekplace = (415,0)
seperatorplace = (555, 0)
windiconspace = (605, 100)
sunriseplace = (605,210)
sunsetplace = (570,210)

week_row = 416

row1 = 351
row2 = 284
row3 = 217
row4 = 150
row5 = 83
row6 = 16

col1 = 3
col2 = 57
col3 = 111
col4 = 165
col5 = 219
col6 = 273
col7 = 327


weekdaysmon = {
'Mon': (week_row,col1), 'Tue': (week_row,col2), 'Wed': (week_row,col3),
'Thu': (week_row,col4), 'Fri': (week_row,col5), 'Sat': (week_row,col6),
'Sun': (week_row,col7)
}

weekdayssun = {
'Sun': (week_row,col1), 'Mon': (week_row,col2), 'Tue': (week_row,col3),
'Wed': (week_row,col4), 'Thu': (week_row,col5), 'Fri': (week_row,col6),
'Sat':(week_row,col7)
}

positions = {
'a1': (row1, col1), 'a2': (row1, col2), 'a3': (row1, col3), 'a4': (row1, col4),
'a5': (row1, col5), 'a6': (row1, col6), 'a7': (row1, col7),

'b1': (row2, col1), 'b2': (row2, col2), 'b3': (row2, col3), 'b4': (row2, col4),
'b5': (row2, col5), 'b6': (row2, col6), 'b7': (row2, col7),

'c1': (row3, col1), 'c2': (row3, col2), 'c3': (row3, col3), 'c4': (row3, col4),
'c5': (row3, col5), 'c6': (row3, col6), 'c7': (row3, col7),

'd1': (row4, col1), 'd2': (row4, col2), 'd3': (row4, col3), 'd4': (row4, col4),
'd5': (row4, col5), 'd6': (row4, col6), 'd7': (row4, col7),

'e1': (row5, col1), 'e2': (row5, col2), 'e3': (row5, col3), 'e4': (row5, col4),
'e5': (row5, col5), 'e6': (row5, col6), 'e7': (row5, col7),

'f1': (row6, col1), 'f2': (row6, col2), 'f3': (row6, col3), 'f4': (row6, col4),
'f5': (row6, col5), 'f6': (row6, col6), 'f7': (row6, col7)
}

weathericons = {
'01d': 'wi-day-sunny', '02d':'wi-day-cloudy', '03d': 'wi-cloudy',
'04d': 'wi-cloudy-windy', '09d': 'wi-showers', '10d':'wi-rain',
'11d':'wi-thunderstorm', '13d':'wi-snow', '50d': 'wi-fog',
'01n': 'wi-night-clear', '02n':'wi-night-cloudy',
'03n': 'wi-night-cloudy', '04n': 'wi-night-cloudy',
'09n': 'wi-night-showers', '10n':'wi-night-rain',
'11n':'wi-night-thunderstorm', '13n':'wi-night-snow',
'50n': 'wi-night-alt-cloudy-windy'}
