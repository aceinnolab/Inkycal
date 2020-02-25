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

def fetch_events(from_time, until_time, timezone = get_tz()):
  """Get events from sepcified range. Input arrow objects!"""
  
  if type(from_time) != arrow.arrow.Arrow or type(until_time) != arrow.arrow.Arrow:
    print('Received invalid time objects! Please check if they are arrow objects!')
    raise TypeError
  else:
    timeline_start = from_time
    timeline_end = until_time.replace(minutes=1)

  """Parse the iCalendars from the urls, fixing some known errors with ics"""
  calendars = [Calendar(fix_ical(url)) for url in ical_urls]

  """Filter events which haven't ended from start of timeline and begin before
     the end of the timeline"""
  upcoming_events = [events for ical in calendars for events in ical.events
      if (timeline_start <= events.begin <= timeline_end) and
         (timeline_start <= events.end <= timeline_end)]

  """Fix event timings of upcoming events"""
  if upcoming_events:
    for events in upcoming_events:
      if events.duration.days >= 1:
        events.end.replace(days =-2)
        events.make_all_day
      elif events.duration.days < 1:
        events.end = events.end.to(timezone)
        events.begin = events.begin.to(timezone)

  """Try to parse all recurring events. In beta!"""
  if use_recurring_events == True:
    recurring_events = [events for ical in calendars for events in ical.events
                        if re.search('RRULE:(.+?)\n', str(events))]

    """Fix event timings of upcoming events"""
    if recurring_events:
      for events in recurring_events:
        if events.duration.days >= 1:
          events.end.replace(days =-2)
          events.make_all_day
        elif events.duration.days < 1:
          events.end = events.end.to(timezone)
          events.begin = events.begin.to(timezone)

        """Try getting recurrence dates of recurring events"""
        try:
          rule = re.search('RRULE:(.+?)\n', str(events)).group(0)[:-2]
          if re.search('UNTIL=(.+?);', rule) and not re.search('UNTIL=(.+?)Z;', rule):
            rule = re.sub('UNTIL=(.+?);', 'UNTIL='+re.search('UNTIL=(.+?);', rule).group(0)[6:-1]+'T000000Z;', rule)
          dates = rrulestr(rule, dtstart= events.begin.datetime).between(after= timeline_start, before = timeline_end.datetime)

          if dates:
            duration = events.duration
            for date in dates:
              cc = events.clone()
              cc.end = arrow.get(date+duration)
              cc.begin = arrow.get(date)
              upcoming_events.append(cc)
              print("Added '{}' starting on {}".format(cc.name, cc.begin.format('DD MMM YY')))

        except Exception as e:
          print('Problematic re-event: ', events.name, rule)
          pass

  """Sort events according to their beginning date"""
  def sort_dates(event):
    return event.begin
  upcoming_events.sort(key=sort_dates)

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
