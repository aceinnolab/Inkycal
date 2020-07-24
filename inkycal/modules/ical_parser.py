#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
iCalendar (parsing) module for Inky-Calendar Project
Copyright by aceisace
"""
import arrow.arrow
import urllib
from urllib.request import urlopen
import logging
import time
import os
import sys
from typing import Union

"""               ---info about iCalendars---
• all day events start at midnight, ending at midnight of the next day
• iCalendar saves all event timings in UTC -> need to be converted into local
  time
• Only non-all_day events or multi-day need to be converted to
  local timezone. Converting all-day events to local timezone is a problem!
"""

try:
    import recurring_ical_events
except ModuleNotFoundError:
    print('recurring-ical-events library could not be found.')
    print('Please install this with: pip3 install recurring-ical-events')
    sys.exit(1)  # Close application since required module is not found

try:
    from icalendar import Calendar, Event
except ModuleNotFoundError:
    print('icalendar library could not be found. Please install this with:')
    print('pip3 install icalendar')
    sys.exit(1)  # Close application since required module is not found

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)
logger.setLevel(level=logging.ERROR)


class iCalendar:
    """
    iCalendar parsing moudule for inkycal.
    Parses events from given iCalendar URLs / paths
    """

    def __init__(self) -> None:
        self.icalendars = []
        self.parsed_events = []

    def load_url(self, url, username: str = None, password: str = None) -> None:
        """
        Input a string or list of strings containing valid iCalendar URLs
        example: 'URL1' (single url) OR ['URL1', 'URL2'] (multiple URLs)
        add username and password to access protected files
        """
        if type(url) == list:
            if (username is None) and (password is None):
                ical = [Calendar.from_ical(str(urlopen(_).read().decode()))
                        for _ in url]
            else:
                ical = [self.__auth_ical(each_url, username, password) for each_url in url]
        elif type(url) == str:
            if (username is None) and (password is None):
                ical = [Calendar.from_ical(str(urlopen(url).read().decode()))]
            else:
                ical = [self.__auth_ical(url, username, password)]
        else:
            raise Exception("Input: '{}' is not a string or list!".format(url))

        # Add the parsed icalendar/s to the self.icalendars list
        if ical:
            self.icalendars += ical
        logger.info('loaded iCalendars from URLs')

    def load_from_file(self, filepath: Union[list, str]) -> None:
        """
        Input a string or list of strings containing valid iCalendar filepaths
        example: 'path1' (single file) OR ['path1', 'path2'] (multiple files)
        returns a list of iCalendars as string (raw)
        """
        if type(filepath) == list:
            ical = (Calendar.from_ical(open(path)) for path in filepath)
        elif type(filepath) == str:
            ical = (Calendar.from_ical(open(filepath)))
        else:
            raise Exception("Input: '{}' is not a string or list!".format(filepath))

        self.icalendars += ical
        logger.info('loaded iCalendars from filepaths')

    def get_events(self, timeline_start: arrow.Arrow, timeline_end: arrow.Arrow, timezone: str = None) -> list:
        """
        Input an arrow (time) object for:
        * the beginning of timeline (events have to end after this time)
        * the end of the timeline (events have to begin before this time)
        * timezone if events should be formatted to local time
        Returns a list of events sorted by date
        """
        if timezone is None:
            timezone = 'UTC'
        t_start = timeline_start
        t_end = timeline_end

        # parse non-recurring events

        # Recurring events time-span has to be in this format:
        # "%Y%m%dT%H%M%SZ" (python strftime)
        t_start_recurring = self.__fmt(t_start)
        t_end_recurring = self.__fmt(t_end)

        # Fetch recurring events
        recurring_events = (recurring_ical_events.of(ical).between(
            t_start_recurring, t_end_recurring)
            for ical in self.icalendars)

        events = (
            {
                'title': events.get('SUMMARY').lstrip(),

                'begin': arrow.get(events.get('DTSTART').dt).to(timezone) if (
                        arrow.get(events.get('dtstart').dt).format('HH:mm') != '00:00')
                else arrow.get(events.get('DTSTART').dt).replace(tzinfo=timezone),

                'end': arrow.get(events.get("DTEND").dt).to(timezone) if (
                        arrow.get(events.get('dtstart').dt).format('HH:mm') != '00:00')
                else arrow.get(events.get('DTEND').dt).replace(tzinfo=timezone)
            } for ical in recurring_events for events in ical)

        # if any recurring events were found, add them to parsed_events
        if events:
            self.parsed_events += list(events)

        # Sort events by their beginning date
        self.sort()
        return self.parsed_events

    def sort(self) -> None:
        """
        Sort all parsed events in order of beginning time
        """
        if not self.parsed_events:
            logger.debug('no events found to be sorted')
        else:
            # sort events by date
            self.parsed_events.sort(key=lambda event: event['begin'])

    def clear_events(self) -> None:
        """
        clear previously parsed events
        """
        self.parsed_events = []

    @staticmethod
    def all_day(event: dict) -> bool:
        """
        Check if an event is an all day event.
        Returns True if event is all day, else False
        """
        if not ('end' and 'begin') in event:
            print('Events must have a starting and ending time')
            raise Exception('This event is not valid!')
        else:
            begin, end = event['begin'], event['end']
            duration = end - begin
            if (begin.format('HH:mm') == '00:00' and end.format('HH:mm') == '00:00'
                    and duration.days >= 1):
                return True
            else:
                return False

    @staticmethod
    def get_system_tz() -> str:
        """
        Get the timezone set by the system
        """
        try:
            local_tz = time.tzname[1]
        except:
            print('System timezone could not be parsed!')
            print('Please set timezone manually!. Setting timezone to None...')
            local_tz = None
        return local_tz

    def show_events(self, fmt: str = 'DD MMM YY HH:mm') -> None:
        """
        print all parsed events in a more readable way
        use the format (fmt) parameter to specify the date format
        see https://arrow.readthedocs.io/en/latest/#supported-tokens
        for more info tokens
        """
        if not self.parsed_events:
            logger.debug('no events found to be shown')
        else:
            line_width = max(len(_['title']) for _ in self.parsed_events)
            for events in self.parsed_events:
                title = events['title']
                begin, end = events['begin'].format(fmt), events['end'].format(fmt)
                print('{0} {1} | {2} | {3}'.format(
                    title, ' ' * (line_width - len(title)), begin, end))

    @staticmethod
    def __fmt(date: arrow.Arrow) -> tuple:
        return date.year, date.month, date.day, date.hour, date.minute, date.second

    @staticmethod
    def __auth_ical(url: str, uname: str, passwd: str) -> list:
        """
        Authorisation helper for protected ical files
        """
        # Credits to Joshka
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password('realm', url, uname, passwd)
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)
        ical = Calendar.from_ical(str(opener.open(url).read().decode()))
        return ical


if __name__ == '__main__':
    print('running {0} in standalone mode'.format(filename))
