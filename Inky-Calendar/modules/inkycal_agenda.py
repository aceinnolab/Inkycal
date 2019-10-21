#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Calendar module for Inky-Calendar Project

Copyright by aceisace
"""
from __future__ import print_function
from inkycal_icalendar import upcoming_events
from configuration import *
from settings import *
import arrow


"""Find max number of lines that can fit in the middle section and allocate
a position for each line"""
lines = middle_section_height // line_height
line_pos = {}
for i in range(lines):
  y = top_section_height + i * line_height
  line_pos['pos'+str(i+1)] = (x_padding, y)


"""Create a list of dictionaries containing dates of the next days"""
now = arrow.now()
agenda_list = [{'date':now.replace(days=+i),
  'date_str':now.replace(days=+i).format('ddd D MMM YY',locale=language),
  'type':'date'} for i in range(lines)]


"""Copy the list from the icalendar module"""
filtered_events = upcoming_events.copy()

"""Print events with some styling"""
"""
style = 'D MMM YY HH:mm'
if filtered_events:
  line_width = max(len(i.name) for i in filtered_events)
  for events in filtered_events:
    print('{0} {1} | {2} | {3} |'.format(events.name,
          ' '* (line_width - len(events.name)), events.begin.format(style),
          events.end.format(style)), events.all_day)
"""

"""Convert the event-timings from utc to the specified locale's time
and create a ready-to-display list for the agenda view"""
for events in filtered_events:
  if not events.all_day:
    events.end = events.end.to(get_tz())
    events.begin = events.begin.to(get_tz())
    if hours == '24':
        agenda_list.append({'date': events.begin,
          'title':events.begin.format('HH:mm')+' '+ str(events.name),
          'type':'timed_event'})
    if hours == '12':
        agenda_list.append({'date': events.begin,
          'title':events.begin.format('hh:mm a')+' '+str(events.name),
          'type':'timed_event'})
  else:
    if events.duration.days == 1:
      agenda_list.append({'date': events.begin,'title':events.name, 'type':'full_day_event'})
    else:
      for days in range(events.duration.days):
        agenda_list.append({'date': events.begin.replace(days=+i),'title':events.name, 'type':'full_day_event'})

"""Sort events and dates in chronological order"""
agenda_list = sorted(agenda_list, key = lambda i: i['date'])

"""Crop the agenda_list in case it's too long"""
if len(agenda_list) > len(line_pos):
  del agenda_list[len(line_pos):]

"""Display all events and dates on the display"""
for i in range(len(agenda_list)):
  if agenda_list[i]['type'] == 'date':
    write_text(line_width, line_height, agenda_list[i]['date_str'],
      line_pos['pos'+str(i+1)], alignment = 'left')
  elif agenda_list[i]['type'] is 'timed_event':
    write_text(line_width, line_height, agenda_list[i]['title'],
      line_pos['pos'+str(i+1)], alignment = 'left')
  else:
    write_text(line_width, line_height, agenda_list[i]['title'],
      line_pos['pos'+str(i+1)])

"""Crop the image to show only the middle section"""
image.crop((0, top_section_height, display_width,
            display_height-bottom_section_height)).save('agenda.png')
