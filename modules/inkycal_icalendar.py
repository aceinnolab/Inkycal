#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
iCalendar (parsing) module for Inky-Calendar Project
Copyright by aceisace
"""
from __future__ import print_function
from configuration import *
from settings import ical_urls
import arrow
from ics import Calendar

use_recurring_events = True
print_events = False
style = 'DD MMM YY HH:mm'


if use_recurring_events == True:
  from dateutil.rrule import rrulestr, rruleset
  import re

def fetch_events():
  """Set timelines for filtering upcoming events"""
  timezone = get_tz()
  now = arrow.now(tz=timezone)
  beginning_of_month = now.replace(days= - now.day +1)
  near_future = now.replace(days= 30)
  further_future = now.replace(days=40)

  """Parse the iCalendars from the urls, fixing some known errors with ics"""
  calendars = [Calendar(fix_ical(url)) for url in ical_urls]

  """Filter any upcoming events from all iCalendars and add them to a list"""
  upcoming_events = [events for ical in calendars for events in ical.events
    if beginning_of_month  <= events.end <= further_future or
    beginning_of_month <= events.begin <= near_future]

  """Try to parse recurring events. This is clearly experimental! """
  if use_recurring_events == True:
    for ical in calendars:
      for events in ical.events:
        event_str = str(events)
        if re.search('RRULE:(.+?)\n', event_str):
          if events.all_day and events.duration.days > 1:
            events.end = events.end.replace(days=-2)
          else:
            events.end = events.end.to(timezone)
            events.begin = events.begin.to(timezone)
          try:
            rule = re.search('RRULE:(.+?)\n', event_str).group(0)[:-2]
            if re.search('UNTIL=(.+?);', rule) and not re.search('UNTIL=(.+?)Z;', rule):
              rule = re.sub('UNTIL=(.+?);', 'UNTIL='+re.search('UNTIL=(.+?);', rule).group(0)[6:-1]+'T000000Z;', rule)
            dates = rrulestr(rule, dtstart= events.begin.datetime).between(after= now.datetime, before = further_future.datetime)

            if dates:
              duration = events.duration
              for date in dates:
                cc = events.clone()
                cc.end = arrow.get(date+duration)
                cc.begin = arrow.get(date)
                upcoming_events.append(cc)
                #print("Added '{}' with new start at {}".format(cc.name, cc.begin.format('DD MMM YY')))

          except Exception as e:
            print('Something went wrong while parsing recurring events')
            pass

  """Sort events according to their beginning date"""
  def sort_dates(event):
    return event.begin
  upcoming_events.sort(key=sort_dates)

  """Multiday events are displayed incorrectly; fix that"""
  for events in upcoming_events:
    if events.all_day and events.duration.days > 1:
      events.end = events.end.replace(days=-2)
      events.make_all_day()

    if not events.all_day:
      events.end = events.end.to(timezone)
      events.begin = events.begin.to(timezone)

  """ The list upcoming_events should not be modified. If you need the data from
  this one, copy the list or the contents to another one."""
  #print(upcoming_events) # Print all events. Might look a bit messy

  """Print upcoming events in a more appealing way"""
  if print_events == True and upcoming_events:
    line_width = max(len(i.name) for i in upcoming_events)
    for events in upcoming_events:
      print('{0} {1} | {2} | {3} | All day ='.format(events.name,
            ' '* (line_width - len(events.name)), events.begin.format(style),
            events.end.format(style)), events.all_day)

  return upcoming_events
