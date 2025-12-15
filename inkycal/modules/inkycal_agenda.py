"""
Inkycal Agenda Module
Copyright by aceinnolab
"""
import logging

import arrow
from PIL import Image, ImageDraw

from inkycal.modules.template import InkycalModule
from inkycal.utils.canvas import Canvas
from inkycal.utils.enums import FONTS
from inkycal.utils.functions import get_system_tz
from inkycal.utils.ical_parser import iCalendar

logger = logging.getLogger(__name__)


class Agenda(InkycalModule):
    """Agenda class
    Create agenda and show events from given icalendars
    """

    name = "Agenda - Display upcoming events from given iCalendars"

    requires = {
        "ical_urls": {
            "label": "iCalendar URL/s, separate multiple ones with a comma",
        },

    }

    optional = {
        "ical_files": {
            "label": "iCalendar filepaths, separated with a comma",
        },

        "date_format": {
            "label": "Use an arrow-supported token for custom date formatting " +
                     "see https://arrow.readthedocs.io/en/stable/#supported-tokens, e.g. ddd D MMM",
            "default": "ddd D MMM",
        },

        "time_format": {
            "label": "Use an arrow-supported token for custom time formatting " +
                     "see https://arrow.readthedocs.io/en/stable/#supported-tokens, e.g. HH:mm",
            "default": "HH:mm",
        },

    }

    def __init__(self, config):
        """Initialize inkycal_agenda module"""

        super().__init__(config)

        config = config['config']

        # Check if all required parameters are present
        for param in self.requires:
            if param not in config:
                raise Exception(f'config is missing {param}')

        # module specific parameters
        self.date_format = config['date_format']
        self.time_format = config['time_format']
        self.language = config['language']

        # Check if ical_files is an empty string
        if config['ical_urls'] and isinstance(config['ical_urls'], str):
            self.ical_urls = config['ical_urls'].split(',')
        else:
            self.ical_urls = config['ical_urls']

        # Check if ical_files is an empty string
        if config['ical_files'] and isinstance(config['ical_files'], str):
            self.ical_files = config['ical_files'].split(',')
        else:
            self.ical_files = config['ical_files']

        # Additional config
        self.timezone = get_system_tz()

        self.icon_font = FONTS.material_icons

        # give an OK message
        logger.debug(f'{__name__} loaded')

    def generate_image(self):
        """Generate image for this module"""

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height

        logger.debug(f'Image size: {im_size}')

        canvas = Canvas(im_size, self.font, self.fontsize)

        # Calculate the max number of lines that can fit on the image
        line_spacing = 1

        line_height = canvas.get_line_height() + line_spacing
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
                    self.date_format, locale=self.language)
            }
            for _ in range(max_lines)]

        # Load icalendar from config
        ical = iCalendar()

        if self.ical_urls:
            ical.load_url(self.ical_urls)

        if self.ical_files:
            ical.load_from_file(self.ical_files)

        # Load events from all icalendar in timerange
        upcoming_events = ical.get_events(today, agenda_events[-1]['begin'],
                                            self.timezone)

        # Sort events by beginning time
        ical.sort()
        # parser.show_events()

        # Set the width for date, time and event titles
        date_strings = [date['begin'].format(self.date_format, locale=self.language) for date in agenda_events]
        longest_date = max(date_strings, key=len)

        date_width = canvas.get_text_width(longest_date)
        logger.debug(f'date_width: {date_width}')

        # Calculate positions for each line
        line_pos = [(0, int(line * line_height)) for line in range(max_lines)]
        logger.debug(f'line_pos: {line_pos}')

        # Check if any events were filtered
        if upcoming_events:
            logger.info('Managed to parse events from urls')

            # Find out how much space the event times take
            time_width = int(max([canvas.get_text_width(
                events['begin'].format(self.time_format, locale=self.language))
                for events in upcoming_events]) + 10)
            logger.debug(f'time_width: {time_width}')

            # Calculate x-pos for time
            x_time = int(date_width/3)
            logger.debug(f'x-time: {x_time}')

            # Find out how much space is left for event titles
            event_width = im_width - time_width 
            logger.debug(f'width for events: {event_width}')

            # Calculate x-pos for event titles
            x_event = int(date_width/3) + time_width
            logger.debug(f'x-event: {x_event}')

            # Merge list of dates and list of events
            agenda_events += upcoming_events

            # Sort the combined list in chronological order of dates
            by_date = lambda event: event['begin']
            agenda_events.sort(key=by_date)

            # Delete more entries than can be displayed (max lines)
            del agenda_events[max_lines:]

            cursor = 0
            for _ in agenda_events:
                title = _['title']

                # Check if item is a date
                if 'end' not in _:
                    ImageDraw.Draw(canvas.image_colour).line(
                        (0, line_pos[cursor][1], im_width, line_pos[cursor][1]),
                        fill='black')

                    canvas.write(
                        xy=line_pos[cursor],
                        box_size=(date_width, line_height),
                        text=title,
                        alignment="left")

                    cursor += 1

                # Check if item is an event
                if 'end' in _:
                    time = _['begin'].format(self.time_format, locale=self.language)

                    # Check if event is all day, if not, add the time
                    if not ical.all_day(_):
                        canvas.write(
                            xy=(x_time, line_pos[cursor][1]),
                            box_size=(time_width, line_height),
                            text=time,
                            alignment="right")
                    else:
                        canvas.set_font(font=self.icon_font, font_size=self.fontsize)

                        canvas.write(
                            xy=(x_time, line_pos[cursor][1]),
                            box_size=(time_width, line_height),
                            text="\ue878",
                            alignment="right")

                    canvas.set_font(font=self.font, font_size=self.fontsize)
                    canvas.write(
                        xy=(x_event, line_pos[cursor][1]),
                        box_size=(event_width, line_height),
                        text=' • ' + title,
                        alignment="left")
                    cursor += 1

        # If no events were found, write only dates and lines
        else:
            logger.info('no events found')

            cursor = 0
            for _ in agenda_events:
                title = _['title']
                ImageDraw.Draw(canvas.image_colour).line(
                    (0, line_pos[cursor][1], im_width, line_pos[cursor][1]),
                    fill='black')

                canvas.write(
                    xy=line_pos[cursor],
                    box_size=(date_width, line_height),
                    text=title,
                    alignment="left")
                cursor += 1

        # return the images ready for the display
        return canvas.image_black, canvas.image_colour
