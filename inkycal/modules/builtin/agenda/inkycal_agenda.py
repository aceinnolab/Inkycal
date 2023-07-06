#!python3
"""
Inkycal Agenda Module
Copyright by aceinnolab
"""
import json

import arrow

from inkycal.custom import *
from inkycal.custom.ical_parser import iCalendar
from inkycal.custom.flexbox import Flexbox
from inkycal.modules.template import inkycal_module

logger = logging.getLogger(__name__)


class ConfigLoader:
    def load_config(self, config_file):
        with open(config_file) as file:
            config = json.load(file)
        return config


# TODO: use default if parameter in settings equals none

class Agenda(inkycal_module):
    """Agenda - Display upcoming events from given iCalendars"""

    def __init__(self, config, ical_urls: str or None = None, ical_files: str or None = None,
                 date_format: str = "ddd D MMM", time_format: str = "HH:mm") -> None:
        """Agenda - Display upcoming events from given iCalendars.

        Args:
            config:
                The default inkycal module config.
            ical_urls:
                iCalendar URL/s, separate multiple ones with a comma.
            ical_files:
                iCalendar filepaths, separated with a comma.
            date_format:
                Use an arrow-supported token for custom date formatting.
                See https://arrow.readthedocs.io/en/stable/#supported-tokens, e.g. ddd D MMM.
            time_format:
                Use an arrow-supported token for custom time formatting.
                See https://arrow.readthedocs.io/en/stable/#supported-tokens, e.g. HH:mm.

        Returns:
            None.
        """
        super().__init__(config)
        self.ical_urls = ical_urls
        self.ical_files = ical_files
        self.date_format = date_format
        self.time_format = time_format

        # Additional config
        self.timezone = get_system_tz()

        # give an OK message
        print(f'{__name__} loaded')

    def initialize(self, config, module_config):
        # required parameters -> config["ical_urls"] , optional parameters: config.get("ical_urls")
        ical_urls = module_config.get("ical_urls")
        ical_files = module_config.get("ical_files")
        date_format = module_config.get("date_format")
        time_format = module_config.get("time_format")

        return self.__class__(config, ical_urls=ical_urls, ical_files=ical_files, date_format=date_format,
                              time_format=time_format)

    def generate_image(self):
        """Generate image for this module"""

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height

        logger.info(f'Image size: {im_size}')

        # Create an image for black pixels and one for coloured pixels
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        # Calculate the max number of lines that can fit on the image
        line_spacing = 1
        line_height = int(self.font.getsize('hg')[1]) + line_spacing
        line_width = im_width
        max_lines = im_height // line_height
        logger.debug(f'max lines: {max_lines}')

        # Create timeline for agenda
        now = arrow.now()
        today = now.floor('day')

        # Create a list of dates for the next days
        agenda_events = [
            {
                'begin': today.shift(days=+_),
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
        upcoming_events = parser.get_events(today, agenda_events[-1]['begin'],
                                            self.timezone)

        # Sort events by beginning time
        parser.sort()
        # parser.show_events()

        # Set the width for date, time and event titles
        date_width = int(max([self.font.getsize(
            dates['begin'].format(self.date_format, locale=self.language))[0]
                              for dates in agenda_events]) * 1.2)
        logger.debug(f'date_width: {date_width}')

        # Calculate positions for each line
        line_pos = [(0, int(line * line_height)) for line in range(max_lines)]
        logger.debug(f'line_pos: {line_pos}')

        # Check if any events were filtered
        if upcoming_events:
            logger.info('Managed to parse events from urls')

            # Find out how much space the event times take
            time_width = int(max([self.font.getsize(
                events['begin'].format(self.time_format, locale=self.language))[0]
                                  for events in upcoming_events]) * 1.2)
            logger.debug(f'time_width: {time_width}')

            # Calculate x-pos for time
            x_time = date_width
            logger.debug(f'x-time: {x_time}')

            # Find out how much space is left for event titles
            event_width = im_width - time_width - date_width
            logger.debug(f'width for events: {event_width}')

            # Calculate x-pos for event titles
            x_event = date_width + time_width
            logger.debug(f'x-event: {x_event}')

            # Merge list of dates and list of events
            agenda_events += upcoming_events

            # Sort the combined list in chronological order of dates
            by_date = lambda event: event['begin']
            agenda_events.sort(key=by_date)

            # Delete more entries than can be displayed (max lines)
            del agenda_events[max_lines:]

            self._agenda_events = agenda_events

            cursor = 0
            for _ in agenda_events:
                title = _['title']

                # Check if item is a date
                if 'end' not in _:
                    ImageDraw.Draw(im_colour).line(
                        (0, line_pos[cursor][1], im_width, line_pos[cursor][1]),
                        fill='black')

                    write(im_black, line_pos[cursor], (date_width, line_height),
                          title, font=self.font, alignment='left')

                    cursor += 1

                # Check if item is an event
                if 'end' in _:
                    time = _['begin'].format(self.time_format, locale=self.language)

                    # Check if event is all day, if not, add the time
                    if not parser.all_day(_):
                        write(im_black, (x_time, line_pos[cursor][1]),
                              (time_width, line_height), time,
                              font=self.font, alignment='left')

                    write(im_black, (x_event, line_pos[cursor][1]),
                          (event_width, line_height),
                          '• ' + title, font=self.font, alignment='left')
                    cursor += 1

        # If no events were found, write only dates and lines
        else:
            logger.info('no events found')

            cursor = 0
            for _ in agenda_events:
                title = _['title']
                ImageDraw.Draw(im_colour).line(
                    (0, line_pos[cursor][1], im_width, line_pos[cursor][1]),
                    fill='black')

                write(im_black, line_pos[cursor], (date_width, line_height),
                      title, font=self.font, alignment='left')

                cursor += 1

        # return the images ready for the display
        return im_black, im_colour


if __name__ == '__main__':
    print(f'running {__name__} in standalone mode')
    keys = Agenda.__init__.__code__.co_varnames[1:]
    key_docs = {
        key: get_param_docstring(Agenda, key)
        for key in keys
    }
    b = 1
