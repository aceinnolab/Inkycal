#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
This file contains all the locations of the icons used.
It also contains the positions of these icons on the E-Paper display
"""

from PIL import Image
im_open = Image.open
import os

path = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
if path != "" and path[-1] != "/":
    path += "/"

wpath = path+'weather-icons/'
dpath = path+'days/'
opath = path+'other/'
fpath = path+'fonts/'

NotoSansCJK = 'NotoSansCJK/NotoSansCJKsc-'
NotoSans = 'NotoSans/NotoSans-SemiCondensed'
weather_font = 'WeatherFont/weathericons-regular-webfont.ttf'

weekday = im_open(opath+'weekday.png')
eventicon = im_open(opath+'event.png')
dateicon = im_open(opath+'today.png')
seperator = im_open(opath+'seperator.jpeg')
seperator2 = im_open(opath+'seperator2.jpeg')
tempicon = im_open(opath+'temperature.jpeg')
humicon = im_open(opath+'humidity.jpeg')
no_response = im_open(opath+'cloud-no-response.jpeg')
sunriseicon = im_open(opath+'wi-sunrise.jpeg')
sunseticon = im_open(opath+'wi-sunset.jpeg')
windicon = im_open(opath+'wi-strong-wind.jpeg')
black = im_open(opath+'black.jpeg')
white = im_open(opath+'white.jpeg')
red = im_open(opath+'red.jpeg')

wiconplace = (0, 0)
tempplace = (299, 0)
humplace = (299, 35)
seperatorplace = (0, 72)
monthplace = (0, 74)
weekplace = (3, 134)
windiconspace = (79, 0)
sunriseplace = (214, 0)
sunsetplace = (214, 35)


col = 0
agenda_view_lines = {
    'line1': (col, 75), 'line2': (col, 100),
    'line3': (col, 125), 'line4': (col, 150),
    'line5': (col, 175), 'line6': (col, 200),
    'line7': (col, 225), 'line8': (col, 250),
    'line9': (col, 275), 'line10': (col, 300),
    'line11': (col, 325), 'line12': (col, 350),
    'line13': (col, 375), 'line14': (col, 400),
    'line15': (col, 425), 'line16': (col, 450),
    'line17': (col, 475), 'line18': (col, 500),
    'line19': (col, 525), 'line20': (col, 550),
    'line21': (col, 575), 'line22': (col, 600),
    }

rss_places = {
    'line_1' : (0, 490), 'line_2' : (0, 515), 'line_3' : (0, 540),
    'line_4' : (0, 565), 'line_5' : (0, 590), 'line_6' : (0, 615)
    }

e_col = 70
date_col = 0

e_row_1 = 490
e_row_2 = 515
e_row_3 = 540
e_row_4 = 565
e_row_5 = 590
e_row_6 = 615

event_positions = {
    'e1': (e_col, e_row_1), 'e2': (e_col, e_row_2), 'e3': (e_col, e_row_3),
    'e4': (e_col, e_row_4), 'e5': (e_col, e_row_5), 'e6': (e_col, e_row_6)
    }

date_positions = {
    'd1': (date_col, e_row_1), 'd2': (date_col, e_row_2),
    'd3': (date_col, e_row_3), 'd4': (date_col, e_row_4),
    'd5': (date_col, e_row_5), 'd6': (date_col, e_row_6)
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

weekday_pos = {
    'pos0': (col1, week_row), 'pos1': (col2, week_row), 'pos2': (col3, week_row),
    'pos3': (col4, week_row), 'pos4': (col5, week_row), 'pos5': (col6, week_row),
    'pos6': (col7, week_row)
    }

weathericons = {
    '01d': '\uf00d', '02d': '\uf002', '03d': '\uf013',
    '04d': '\uf012', '09d': '\uf01a', '10d': '\uf019',
    '11d': '\uf01e', '13d': '\uf01b', '50d': '\uf014',
    '01n': '\uf02e', '02n': '\uf013', '03n': '\uf013',
    '04n': '\uf013', '09n': '\uf037', '10n': '\uf036',
    '11n': '\uf03b', '13n': '\uf038', '50n': '\uf023'
    }
