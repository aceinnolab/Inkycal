#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Agenda module for Inky-Calendar Project
Copyright by aceisace
"""
from __future__ import print_function
from inkycal_icalendar import fetch_events
from configuration import*
from settings import *
import arrow

fontsize = 14
show_events = True
print_events = False
style = 'D MMM YY HH:mm'

"""Add a border to increase readability"""
border_top = int(middle_section_height * 0.02)
border_left = int(middle_section_width * 0.02)

"""Choose font optimised for the agenda section"""
font = ImageFont.truetype(NotoSans+'Medium.ttf', fontsize)
line_height = int(font.getsize('hg')[1] * 1.2) + 1
line_width = int(middle_section_width - (border_left*2))

"""Set some positions for events, dates and times"""
date_col_width = int(line_width * 0.20)
time_col_width = int(line_width * 0.15)
event_col_width = int(line_width - date_col_width - time_col_width)

date_col_start = border_left
time_col_start = date_col_start + date_col_width
event_col_start = time_col_start + time_col_width

"""Find max number of lines that can fit in the middle section and allocate
a position for each line"""
if bottom_section:
  max_lines = int((middle_section_height - border_top*2) // line_height)
else:
  max_lines = int(middle_section_height+bottom_section_height -
                  (border_top * 2))// line_height

line_pos = [(border_left, int(top_section_height + border_top + line * line_height))
  for line in range(max_lines)]

def main():
  try:
    clear_image('middle_section')

    print('Agenda module: Generating image...', end = '')
    now = arrow.now(get_tz())
    today_start = arrow.get(now.year, now.month, now.day)

    """Create a list of dictionaries containing dates of the next days"""
    agenda_events = [{'date':today_start.replace(days=+_),
      'date_str': now.replace(days=+_).format('ddd D MMM',locale=language),
      'type':'date'} for _ in range(max_lines)]

    """Copy the list from the icalendar module with some conditions"""
    upcoming_events = fetch_events()
    filtered_events = [events for events in upcoming_events if
                       events.end > now]

    """Set print_events_to True to print all events in this month"""
    if print_events == True and filtered_events:
      auto_line_width = max(len(_.name) for _ in filtered_events)
      for events in filtered_events:
        print('{0} {1} | {2} | {3} | All day ='.format(events.name,
          ' '* (auto_line_width - len(events.name)), events.begin.format(style),
          events.end.format(style)), events.all_day)

    """Convert the event-timings from utc to the specified locale's time
    and create a ready-to-display list for the agenda view"""
    for events in filtered_events:
      if not events.all_day:
        agenda_events.append({'date': events.begin, 'time': events.begin.format(
          'HH:mm' if hours == '24' else 'hh:mm a'), 'name':str(events.name),
          'type':'timed_event'})
      else:
        if events.duration.days == 1:
          agenda_events.append({'date': events.begin,'time':'All day',
                                'name': events.name,'type':'full_day_event'})
        else:
          for day in range(events.duration.days):
            agenda_events.append({'date': events.begin.replace(days=+day),
              'time':'All day','name':events.name, 'type':'full_day_event'})

    """Sort events and dates in chronological order"""
    agenda_events = sorted(agenda_events, key = lambda event: event['date'])

    """Crop the agenda_events in case it's too long"""
    del agenda_events[max_lines:]

    """Display all events, dates and times on the display"""
    if show_events == True:
      previous_date = None
      for events in range(len(agenda_events)):
        if agenda_events[events]['type'] == 'date':
          if previous_date == None or previous_date != agenda_events[events][
            'date']:
            write_text(date_col_width, line_height,
              agenda_events[events]['date_str'], line_pos[events], font = font)

          previous_date = agenda_events[events]['date']
          draw.line((date_col_start, line_pos[events][1],
            line_width,line_pos[events][1]), fill = 'red' if display_type == 'colour' else 'black')

        elif agenda_events[events]['type'] == 'timed_event':
          write_text(time_col_width, line_height, agenda_events[events]['time'],
            (time_col_start, line_pos[events][1]), font = font)

          write_text(event_col_width, line_height, ('• '+agenda_events[events][
            'name']), (event_col_start, line_pos[events][1]),
             alignment = 'left', font = font)

        else:
          write_text(time_col_width, line_height, agenda_events[events]['time'],
            (time_col_start, line_pos[events][1]), font = font)

          write_text(event_col_width, line_height, ('• '+agenda_events[events]['name']),
            (event_col_start, line_pos[events][1]), alignment = 'left', font = font)

    """Crop the image to show only the middle section"""
    if bottom_section:
      agenda_image = crop_image(image, 'middle_section')
    else:
      agenda_image = image.crop((0,middle_section_offset,display_width, display_height))

    agenda_image.save(image_path+'agenda.png')
    print('Done')

  except Exception as e:
    """If something went wrong, print a Error message on the Terminal"""
    print('Failed!')
    print('Error in Agenda module!')
    print('Reason: ',e)
    pass

if __name__ == '__main__':
  main()
