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

print_events = False
style = 'DD MMM YY HH:mm'


def fetch_events():
  """Set timelines for filtering upcoming events"""
  now = arrow.now(tz=get_tz())
  beginning_of_month = now.replace(days= - now.day +1)
  near_future = now.replace(days= 30)
  further_future = now.replace(days=40)

  """Parse the iCalendars from the urls, fixing some known errors with ics"""
  calendars = [Calendar(fix_ical(url)) for url in ical_urls]

  """Filter any upcoming events from all iCalendars and add them to a list"""
  upcoming_events = [events for ical in calendars for events in ical.events
    if beginning_of_month  <= events.end <= further_future or
    beginning_of_month <= events.begin <= near_future]

  """Sort events according to their beginning date"""
  def sort_dates(event):
    return event.begin
  upcoming_events.sort(key=sort_dates)

  """Multiday events are displayed incorrectly; fix that"""
  for events in upcoming_events:
    if events.all_day and events.duration.days > 1:
      events.end = events.end.replace(days=-2)
      
    if not events.all_day:
      events.begin = events.begin.to(get_tz())
      events.end = events.end.to(get_tz())
    

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
