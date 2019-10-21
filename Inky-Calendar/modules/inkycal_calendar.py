#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Calendar module for Inky-Calendar Project

Copyright by aceisace
"""
from __future__ import print_function
import calendar
from configuration import *
from settings import *
import datetime 
from PIL import Image, ImageDraw

"""Define some parameters for the grid"""
grid_width, grid_height = display_width, 324
grid_rows = 6
grid_coloums = 7

padding_left = int((display_width % grid_coloums) / 2)
padding_up = int((grid_height % grid_rows) / 2)
icon_width = grid_width // grid_coloums
icon_height = grid_height // grid_rows

weekdays_height = 22
#def main():
this = datetime.datetime.now()

"""Add grid-coordinates in the grid dictionary for a later lookup"""
grid = {}

counter = 0
for row in range(grid_rows):
  y = middle_section_offset - grid_height + row*icon_height
  for col in range(grid_coloums):
    x = padding_left + col*icon_width
    counter += 1
    grid['pos'+str(counter)] = (x,y)


"""Set the Calendar to start on the day specified by the settings file """
if week_starts_on is "" or "Monday":
  calendar.setfirstweekday(calendar.MONDAY)
else:
  calendar.setfirstweekday(calendar.SUNDAY)

"""Create a scrolling calendar"""
cal = calendar.monthcalendar(this.year, this.month)
current_row = [cal.index(i) for i in cal if this.day in i][0]

if current_row > 1:
  del cal[:current_row-1]

if len(cal) < grid_rows:
  next_month = this + datetime.timedelta(days=30)
  cal_next_month = calendar.monthcalendar(next_month.year, next_month.month)
  cal.extend(cal_next_month[:grid_rows - len(cal)]

"""
flatten = lambda z: [x for y in z for x in y]
cal = flatten(cal)
cal_next_month = flatten(cal_next_month)

cal.extend(cal_next_month)

num_font= ImageFont.truetype(NotoSansCJK+'Light.otf', 30)
"""






#draw = ImageDraw.Draw(image) #



"""
counter = 0
for i in range(len(cal)):
  counter += 1
  if cal[i] != 0 and counter <= grid_rows*grid_coloums:
    write_text(icon_width, icon_height, str(cal[i]), grid['pos'+str(counter)],
               font = num_font)
  ##if this.day == cal[i]:
    ##pos = grid['pos'+str(counter)]
    #x = pos[0] + int(icon_width/2)
    #y = pos[1] + int(icon_height/2)
    #r = int(icon_width * 0.75#coords = (x-r, y-r, x+r, y+r)
    #draw.ellipse(coords, fill= 0, outline='black',
      #width=3)

image.crop((0, top_section_height, display_width,
            display_height-bottom_section_height)).save('cal.png')

#if __name__ == '__main__':
#    main()
"""
