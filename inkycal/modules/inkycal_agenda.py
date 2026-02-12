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
        
        "columns": {
            "label": "Number of columns to display events in (1 or 2 columns supported)",
            "default": 1,
        }

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
        self.columns = config.get('columns', 1)
        
        # Validate columns
        if self.columns < 1 or self.columns > 2:
            raise ValueError(f"Columns must be 1 or 2, got {self.columns}")

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
        
        # Calculate column layout
        gutter = 10 if self.columns > 1 else 0
        col_width = (im_width - (self.columns - 1) * gutter) // self.columns
        
        lines_per_col = im_height // line_height
        max_lines = lines_per_col * self.columns
        
        logger.debug(f'max lines: {max_lines} ({lines_per_col} per column)')

        # Create timeline for agenda
        now = arrow.now()
        today = now.floor('day')

        # Create a list of dates for the next days
        # We need enough dates to potentially fill all columns
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
        # Ensure date width doesn't exceed column width
        date_width = min(date_width, col_width)
        logger.debug(f'date_width: {date_width}')

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
            event_width = col_width - time_width 
            logger.debug(f'width for events: {event_width}')

            # Calculate x-pos for event titles
            x_event = int(date_width/3) + time_width
            logger.debug(f'x-event: {x_event}')
            
            # Calculate bullet width
            bullet = " • "
            bullet_width = canvas.get_text_width(bullet)
            title_width = event_width - bullet_width

            # Merge list of dates and list of events
            agenda_events += upcoming_events

            # Sort the combined list in chronological order of dates
            by_date = lambda event: event['begin']
            agenda_events.sort(key=by_date)

            # Delete more entries than can be displayed (max lines)
            # We keep them for now, but will stop rendering when full
            # del agenda_events[max_lines:]

            col = 0
            y_pos = 0
            last_date_title = None
            
            for item in agenda_events:
                # Determine type and content
                if 'end' not in item: # Date
                    text = item['title']
                    is_event = False
                    # Dates are assumed to be 1 line
                    item_height = line_height
                    last_date_title = text
                else: # Event
                    text = item['title']
                    is_event = True
                    # Calculate required height for event title
                    lines = canvas.text_wrap(text, title_width)
                    num_lines = max(1, len(lines))
                    item_height = num_lines * line_height

                # Check if fits in current column
                # If it's a date, we want to ensure there's space for at least one more line (the event)
                # to avoid orphaned headers at the bottom of a column
                check_height = item_height
                if not is_event:
                    check_height += line_height

                if y_pos + check_height > im_height:
                    # Move to next column
                    col += 1
                    y_pos = 0
                    
                    # Check if we have run out of columns
                    if col >= self.columns:
                        break
                    
                    # If this is an event and we have a date context, repeat the date header
                    if is_event and last_date_title:
                        x_offset = col * (col_width + gutter)
                        
                        # Draw line
                        ImageDraw.Draw(canvas.image_colour).line(
                            (x_offset, y_pos, x_offset + col_width, y_pos),
                            fill='black')

                        canvas.write(
                            xy=(x_offset, y_pos),
                            box_size=(date_width, line_height),
                            text=last_date_title,
                            alignment="left")
                        
                        y_pos += line_height
                
                # Calculate offsets
                x_offset = col * (col_width + gutter)
                
                if not is_event:
                    # Render Date
                    ImageDraw.Draw(canvas.image_colour).line(
                        (x_offset, y_pos, x_offset + col_width, y_pos),
                        fill='black')

                    canvas.write(
                        xy=(x_offset, y_pos),
                        box_size=(date_width, item_height),
                        text=text,
                        alignment="left")
                else:
                    # Render Event
                    # Time (always 1 line, aligned to top)
                    time = item['begin'].format(self.time_format, locale=self.language)
                    
                    if not ical.all_day(item):
                        canvas.write(
                            xy=(x_offset + x_time, y_pos),
                            box_size=(time_width, line_height),
                            text=time,
                            alignment="right")
                    else:
                        canvas.set_font(font=self.icon_font, font_size=self.fontsize)

                        canvas.write(
                            xy=(x_offset + x_time, y_pos),
                            box_size=(time_width, line_height),
                            text="\ue878",
                            alignment="right")
                        
                        canvas.set_font(font=self.font, font_size=self.fontsize)

                    # Bullet
                    canvas.write(
                        xy=(x_offset + x_event, y_pos),
                        box_size=(bullet_width, line_height),
                        text=bullet,
                        alignment="left")

                    # Title (multi-line)
                    canvas.write(
                        xy=(x_offset + x_event + bullet_width, y_pos),
                        box_size=(title_width, item_height),
                        text=text,
                        alignment="left")
                
                # Advance cursor
                y_pos += item_height

        # If no events were found, write only dates and lines
        else:
            logger.info('no events found')

            col = 0
            y_pos = 0
            
            for item in agenda_events:
                title = item['title']
                item_height = line_height
                
                # Orphan check for dates in empty agenda
                check_height = item_height + line_height
                
                if y_pos + check_height > im_height:
                    col += 1
                    y_pos = 0
                    if col >= self.columns:
                        break
                
                x_offset = col * (col_width + gutter)
                
                ImageDraw.Draw(canvas.image_colour).line(
                    (x_offset, y_pos, x_offset + col_width, y_pos),
                    fill='black')

                canvas.write(
                    xy=(x_offset, y_pos),
                    box_size=(date_width, item_height),
                    text=title,
                    alignment="left")
                
                y_pos += item_height

        # return the images ready for the display
        return canvas.image_black, canvas.image_colour
