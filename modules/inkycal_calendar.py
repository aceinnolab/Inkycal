#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Calendar module for Inky-Calendar Project
Copyright by aceisace
"""
from __future__ import print_function
import calendar
from configuration import *

print_events = False
show_events = True
today_in_your_language = 'today'
tomorrow_in_your_language = 'tomorrow'
at_in_your_language = 'at'
event_icon = 'square' # dot #square
style = "DD MMM"

fontsize = 16
font = ImageFont.truetype(NotoSans+'.ttf', fontsize)
space_between_lines = 0

if show_events == True:
  from inkycal_icalendar import fetch_events

"""Add a border to increase readability"""
border_top = int(middle_section_height * 0.02)
border_left = int(middle_section_width * 0.02)

main_area_height = middle_section_height-border_top*2
main_area_width = middle_section_width-border_left*2

line_height = font.getsize('hg')[1] + space_between_lines
line_width = middle_section_width - (border_left*2)

"""Calculate height for each sub-section"""
month_name_height = int(main_area_height*0.1)
weekdays_height = int(main_area_height*0.05)
calendar_height = int(main_area_height*0.6)
events_height = int(main_area_height*0.25)

"""Set rows and coloumns in the calendar section and calculate sizes"""
calendar_rows, calendar_coloumns = 6, 7
icon_width = main_area_width // calendar_coloumns
icon_height = calendar_height // calendar_rows

"""Calculate paddings for calendar section"""
x_padding_calendar = int((main_area_width % icon_width) / 2)
y_padding_calendar = int((main_area_height % calendar_rows) / 2)

"""Add coordinates for number icons inside the calendar section"""
grid_start_y = (middle_section_offset + border_top + month_name_height +
                weekdays_height + y_padding_calendar)
grid_start_x = border_left + x_padding_calendar

grid = [(grid_start_x + icon_width*x, grid_start_y + icon_height*y)
        for y in range(calendar_rows) for x in range(calendar_coloumns)]

weekday_pos = [(grid_start_x + icon_width*_, middle_section_offset +
                month_name_height) for _ in range(calendar_coloumns)]

max_event_lines = (events_height - border_top) // (font.getsize('hg')[1]
  + space_between_lines)

event_lines = [(border_left,(bottom_section_offset - events_height)+
  int(events_height/max_event_lines*_)) for _ in range(max_event_lines)]

def generate_image():
  if middle_section == "inkycal_calendar" and internet_available() == True:
    try:
      clear_image('middle_section')
      print('Calendar module: Generating image...', end = '')
      now = arrow.now(tz = get_tz())

      """Set up the Calendar template based on personal preferences"""
      if week_starts_on == "Monday":
        calendar.setfirstweekday(calendar.MONDAY)
        weekstart = now.replace(days = - now.weekday())
      else:
        calendar.setfirstweekday(calendar.SUNDAY)
        weekstart = now.replace(days = - now.isoweekday())

      """Write the name of the current month at the correct position"""
      write_text(main_area_width, month_name_height,
        str(now.format('MMMM',locale=language)), (border_left,
        middle_section_offset), autofit = True)

      """Set up weeknames in local language and add to main section"""
      weekday_names = [weekstart.replace(days=+_).format('ddd',locale=language)
        for _ in range(7)]

      for _ in range(len(weekday_pos)):
        write_text(icon_width, weekdays_height, weekday_names[_],
                   weekday_pos[_], autofit = True)

      """Create a calendar template and flatten (remove nestings)"""
      flatten = lambda z: [x for y in z for x in y]
      calendar_flat = flatten(calendar.monthcalendar(now.year, now.month))

      """Add the numbers on the correct positions"""
      for i in range(len(calendar_flat)):
        if calendar_flat[i] != 0:
          write_text(icon_width, icon_height, str(calendar_flat[i]), grid[i])

      """Draw a red/black circle with the current day of month in white"""
      icon = Image.new('RGBA', (icon_width, icon_height))
      current_day_pos = grid[calendar_flat.index(now.day)]
      x_circle,y_circle = int(icon_width/2), int(icon_height/2)
      radius = int(icon_width * 0.25)
      text_width, text_height = default.getsize(str(now.day))
      x_text = int((icon_width / 2) - (text_width / 2))
      y_text = int((icon_height / 2) - (text_height / 1.7))
      ImageDraw.Draw(icon).ellipse((x_circle-radius, y_circle-radius,
        x_circle+radius, y_circle+radius), fill= 'red' if
        three_colour_support == True else 'black', outline=None)
      ImageDraw.Draw(icon).text((x_text, y_text), str(now.day), fill='white',
        font=bold)
      image.paste(icon, current_day_pos, icon)

      """Create some reference points for the current month"""
      days_current_month = calendar.monthrange(now.year, now.month)[1]
      month_start = now.floor('month')
      month_end = now.ceil('month')

      if show_events == True:
        """Filter events which begin before the end of this month"""
        upcoming_events = fetch_events()

        calendar_events = [events for events in upcoming_events if
          month_start <= events.end <= month_end ]

        """Find days with events in the current month"""
        days_with_events = []
        for events in calendar_events:
          if events.duration.days <= 1:
            days_with_events.append(int(events.begin.format('D')))
          else:
            for day in range(events.duration.days):
              days_with_events.append(
                int(events.begin.replace(days=+i).format('D')))
        days_with_events = set(days_with_events)

        if event_icon == 'dot':
          for days in days_with_events:
            write_text(icon_width, int(icon_height * 0.2), '•',
              (grid[calendar_flat.index(days)][0],
               int(grid[calendar_flat.index(days)][1] + icon_height*0.8)))

        if event_icon == 'square':
          square_size = int(icon_width * 0.6)
          center_x = int((icon_width - square_size) / 2)
          center_y = int((icon_height - square_size) / 2)
          for days in days_with_events:
            draw_square((int(grid[calendar_flat.index(days)][0]+center_x),
               int(grid[calendar_flat.index(days)][1] + center_y )),
               8, square_size , square_size)


        """Add a small section showing events of today and tomorrow"""
        event_list = ['{0} {1} {2} : {3}'.format(today_in_your_language,
          at_in_your_language, event.begin.format('HH:mm' if hours == 24 else
          'hh:mm'), event.name) for event in calendar_events if event.begin.day
          == now.day and now < event.end]

        event_list += ['{0} {1} {2} : {3}'.format(tomorrow_in_your_language,
          at_in_your_language, event.begin.format('HH:mm' if hours == 24 else
          'hh:mm'), event.name) for event in calendar_events if event.begin.day
          == now.replace(days=1).day]

        after_two_days = now.replace(days=2).floor('day')

        event_list += ['{0} {1} {2} : {3}'.format(event.begin.format('D MMM'),
          at_in_your_language, event.begin.format('HH:mm' if hours == 24 else
          'hh:mm'), event.name) for event in upcoming_events if event.end >
           after_two_days]

        del event_list[max_event_lines:]

      if event_list:
        for lines in event_list:
          write_text(main_area_width, int(events_height/max_event_lines), lines,
            event_lines[event_list.index(lines)], alignment='left',
            fill_height = 0.7)
      else:
        write_text(main_area_width, int(events_height/max_event_lines),
         'No upcoming events.', event_lines[0], alignment='left',
         fill_height = 0.7)

      """Set print_events_to True to print all events in this month"""
      style = 'DD MMM YY HH:mm'
      if print_events == True and calendar_events:
        line_width = max(len(_.name) for _ in calendar_events)
        for events in calendar_events:
          print('{0} {1} | {2} | {3} | All day ='.format(events.name,
            ' ' * (line_width - len(events.name)), events.begin.format(style),
            events.end.format(style)), events.all_day)

      calendar_image = crop_image(image, 'middle_section')
      calendar_image.save(image_path+'inkycal_calendar.png')

      print('Done')

    except Exception as e:
      """If something went wrong, print a Error message on the Terminal"""
      print('Failed!')
      print('Error in Calendar module!')
      print('Reason: ',e)
      pass

def main():
  generate_image()

main()
