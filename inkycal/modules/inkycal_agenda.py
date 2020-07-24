#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Agenda module for Inky-Calendar Project
Copyright by aceisace
"""

from inkycal.modules.template import inkycal_module
from inkycal.custom import *
from inkycal.modules.ical_parser import iCalendar

import calendar as cal
import arrow

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)
logger.setLevel(level=logging.ERROR)


class Agenda(inkycal_module):
    """
    Agenda class
    Create agenda and show events from given icalendars
    """

    def __init__(self, section_size: tuple, section_config: dict) -> None:
        """
        Initialize inkycal_agenda module
        """
        super().__init__(section_size, section_config)
        # Module specific parameters
        required = ['week_starts_on', 'ical_urls']
        for param in required:
            if param not in section_config:
                raise Exception('config is missing {}'.format(param))

        # class name
        self.name = self.__class__.__name__

        # module specific parameters
        self.date_format = 'ddd D MMM'
        self.time_format = "HH:mm"
        self.language = self.config['language']
        self.timezone = get_system_tz()
        self.ical = None
        self.ical_urls = self.config['ical_urls']
        self.ical_files = []

        # give an OK message
        print('{0} loaded'.format(self.name))

    def __validate(self) -> None:
        """
        Validate module-specific parameters
        """
        if not isinstance(self.date_format, str):
            print('date_format has to be an arrow-compatible token')

        if not isinstance(self.time_format, str):
            print('time_format has to be an arrow-compatible token')

        if not isinstance(self.language, str):
            print('language has to be a string: "en" ')

        if not isinstance(self.timezone, str):
            print('The timezone has bo be a string.')

        if not isinstance(self.ical_urls, list):
            print('ical_urls has to be a list ["url1", "url2"] ')

        if not isinstance(self.ical_files, list):
            print('ical_files has to be a list ["path1", "path2"] ')

    def generate_image(self) -> None:
        """
        Generate image for this module
        """
        # Define new image size with respect to padding
        im_width = int(self.width - (self.width * 2 * self.margin_x))
        im_height = int(self.height - (self.height * 2 * self.margin_y))
        im_size = im_width, im_height

        logger.info('Image size: {0}'.format(im_size))

        # Create an image for black pixels and one for coloured pixels
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        # Calculate the max number of lines that can fit on the image
        line_spacing = 1
        line_height = int(self.font.getsize('hg')[1]) + line_spacing
        line_width = im_width
        max_lines = im_height // line_height
        logger.debug(('max lines:', max_lines))

        # Create timeline for agenda
        now = arrow.now()
        today = now.floor('day')

        # Create a list of dates for the next days
        agenda_events = [
            {'begin': today.shift(days=+_),
             'title': today.shift(days=+_).format(
                 self.date_format, locale=self.language)}
            for _ in range(max_lines)]

        # Load icalendar from config
        self.ical = iCalendar()
        parser = self.ical

        if self.ical_urls:
            parser.load_url(self.ical_urls)
        if self.ical_files:
            parser.load_from_file(self.ical_files)

        # Load events from all icalendar in timerange
        upcoming_events = parser.get_events(today, agenda_events[-1]['begin'], self.timezone)

        # Sort events by beginning time
        parser.sort()
        # parser.show_events()

        # Set the width for date, time and event titles
        date_width = int(max([self.font.getsize(
            dates['begin'].format(self.date_format, locale=self.language))[0]
                              for dates in agenda_events]) * 1.2)
        logger.debug(('date_width:', date_width))

        # Calculate positions for each line
        line_pos = [(0, int(line * line_height)) for line in range(max_lines)]
        logger.debug(('line_pos:', line_pos))

        # Check if any events were filtered
        if upcoming_events:
            # Find out how much space the event times take
            time_width = int(max([self.font.getsize(
                events['begin'].format(self.time_format, locale=self.language))[0]
                                  for events in upcoming_events]) * 1.2)
            logger.debug(('time_width:', time_width))

            # Calculate x-pos for time
            x_time = date_width
            logger.debug(('x-time:', x_time))

            # Find out how much space is left for event titles
            event_width = im_width - time_width - date_width
            logger.debug(('width for events:', event_width))

            # Calculate x-pos for event titles
            x_event = date_width + time_width
            logger.debug(('x-event:', x_event))

            # Merge list of dates and list of events
            agenda_events += upcoming_events

            # Sort the combined list in chronological order of dates
            agenda_events.sort(key=lambda event: event['begin'])

            # Delete more entries than can be displayed (max lines)
            del agenda_events[max_lines:]

            cursor = 0
            for event in agenda_events:
                title = event['title']
                # Check if item is a date
                if 'end' not in event:
                    ImageDraw.Draw(im_colour).line(
                        (0, line_pos[cursor][1], im_width, line_pos[cursor][1]), fill='black'
                    )

                    write(im_black, line_pos[cursor], (date_width, line_height),
                          title, font=self.font, alignment='left'
                          )

                    cursor += 1

                # Check if item is an event
                if 'end' in event:
                    _time = event['begin'].format(self.time_format)

                    # Check if event is all day, if not, add the time
                    if not parser.all_day(event):
                        write(im_black, (x_time, line_pos[cursor][1]),
                              (time_width, line_height), _time, font=self.font, alignment='left')

                    write(im_black, (x_event, line_pos[cursor][1]),
                          (event_width, line_height),
                          '• ' + title, font=self.font, alignment='left')
                    cursor += 1

        # If no events were found, write only dates and lines
        else:
            cursor = 0
            for event in agenda_events:
                title = event['title']
                ImageDraw.Draw(im_colour).line((0, line_pos[cursor][1], im_width, line_pos[cursor][1]), fill='black')

                write(im_black, line_pos[cursor], (date_width, line_height),
                      title, font=self.font, alignment='left')

                cursor += 1

            logger.info('no events found')

        # Save image of black and colour channel in image-folder
        im_black.save(images + self.name + '.png')
        im_colour.save(images + self.name + '_colour.png')


if __name__ == '__main__':
    print('running {0} in standalone mode'.format(filename))
