#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PIL import Image, ImageFont
from settings import *
im_open = Image.open

path =      '/home/pi/E-Paper-Master/Calendar/'
wpath =     path+'weather-icons/'
mpath =     path+'translations/'+language+'/months/'
weekpath =  path+'translations/'+language+'/week/'
dpath =     path+'days/'
opath =     path+'other/'

weekday =       im_open(opath+'weekday.bmp').convert('L')
eventicon =     im_open(opath+'event.bmp').convert('L')
dateicon =      im_open(opath+'today.bmp').convert('L')
tempicon =      im_open(opath+'temperature.jpeg')
humicon =       im_open(opath+'humidity.jpeg')
weekmon =       im_open(weekpath+'week-mon.jpeg')
weeksun =       im_open(weekpath+'week-sun.jpeg')
seperator =     im_open(opath+'seperator.jpeg').convert('L')
no_response=    im_open(opath+'cloud-no-response.jpeg')
sunriseicon =   im_open(opath+'wi-sunrise.jpeg')
sunseticon =    im_open(opath+'wi-sunset.jpeg')
windicon =      im_open(opath+'wi-strong-wind.jpeg')

wiconplace = (0, 0)
tempplace = (299, 0)
humplace = (299, 35)
seperatorplace = (0, 72)
monthplace = (0, 74)
weekplace = (3, 134)
windiconspace = (79, 0)
sunriseplace = (214, 0)
sunsetplace = (214, 35)

e_col = 70
date_col = 0

e_row_1 = 540
e_row_2 = 565
e_row_3 = 590
e_row_4 = 615

event_positions = {
'e1': (e_col, e_row_1), 'e2': (e_col, e_row_2), 'e3': (e_col, e_row_3),
'e4': (e_col, e_row_4)
}

date_positions = {
'd1': (date_col, e_row_1), 'd2': (date_col, e_row_2), 'd3': (date_col, e_row_3),
'd4': (date_col, e_row_4)
}

col1 = 3
col2 = 57
col3 = 111
col4 = 165
col5 = 219
col6 = 273
col7 = 327

row1 = 162
row2 = 225
row3 = 288
row4 = 351
row5 = 414
row6 = 477

positions = {
'a1': (col1, row1), 'a2': (col2, row1), 'a3': (col3, row1), 'a4': (col4, row1),
'a5': (col5, row1), 'a6': (col6, row1), 'a7': (col7, row1),

'b1': (col1, row2), 'b2': (col2, row2), 'b3': (col3, row2), 'b4': (col4, row2),
'b5': (col5, row2), 'b6': (col6, row2), 'b7': (col7, row2),

'c1': (col1, row3), 'c2': (col2, row3), 'c3': (col3, row3), 'c4': (col4, row3),
'c5': (col5, row3), 'c6': (col6, row3), 'c7': (col7, row3),

'd1': (col1, row4), 'd2': (col2, row4), 'd3': (col3, row4), 'd4': (col4, row4),
'd5': (col5, row4), 'd6': (col6, row4), 'd7': (col7, row4),

'e1': (col1, row5), 'e2': (col2, row5), 'e3': (col3, row5), 'e4': (col4, row5),
'e5': (col5, row5), 'e6': (col6, row5), 'e7': (col7, row5),

'f1': (col1, row6), 'f2': (col2, row6), 'f3': (col3, row6), 'f4': (col4, row6),
'f5': (col5, row6), 'f6': (col6, row6), 'f7': (col7, row6)
}

week_row = 134

weekdaysmon = {
'Mon': (col1,week_row), 'Tue': (col2,week_row), 'Wed': (col3,week_row),
'Thu': (col4,week_row), 'Fri': (col5,week_row), 'Sat': (col6,week_row),
'Sun': (col7,week_row)
}

weekdayssun = {
'Sun': (col1,week_row), 'Mon': (col2,week_row), 'Tue': (col3,week_row),
'Wed': (col4,week_row), 'Thu': (col5,week_row), 'Fri': (col6,week_row),
'Sat': (col7,week_row)
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
