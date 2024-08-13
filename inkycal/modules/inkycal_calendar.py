"""
Inkycal Calendar Module
Copyright by aceinnolab
"""

# pylint: disable=logging-fstring-interpolation

import calendar as cal

from inkycal.custom import *
from inkycal.modules.template import inkycal_module

logger = logging.getLogger(__name__)


class Calendar(inkycal_module):
    """Calendar class
    Create monthly calendar and show events from given iCalendars
    """

    name = "Calendar - Show monthly calendar with events from iCalendars"

    optional = {
        "week_starts_on": {
            "label": "When does your week start? (default=Monday)",
            "options": ["Monday", "Sunday"],
            "default": "Monday",
        },
        "show_events": {
            "label": "Show parsed events? (default = True)",
            "options": [True, False],
            "default": True,
        },
        "ical_urls": {
            "label": "iCalendar URL/s, separate multiple ones with a comma",
        },
        "ical_files": {
            "label": "iCalendar filepaths, separated with a comma",
        },
        "date_format": {
            "label": "Use an arrow-supported token for custom date formatting "
                     + "see https://arrow.readthedocs.io/en/stable/#supported-tokens, e.g. D MMM",
            "default": "D MMM",
        },
        "time_format": {
            "label": "Use an arrow-supported token for custom time formatting "
                     + "see https://arrow.readthedocs.io/en/stable/#supported-tokens, e.g. HH:mm",
            "default": "HH:mm",
        },
    }

    def __init__(self, config):
        """Initialize inkycal_calendar module"""

        super().__init__(config)
        config = config['config']

        self.ical = None
        self.month_events = None
        self._upcoming_events = None
        self._days_with_events = None

        # optional parameters
        self.week_start = config['week_starts_on']
        self.show_events = config['show_events']
        self.date_format = config["date_format"]
        self.time_format = config['time_format']
        self.language = config['language']

        if config['ical_urls'] and isinstance(config['ical_urls'], str):
            self.ical_urls = config['ical_urls'].split(',')
        else:
            self.ical_urls = config['ical_urls']

        if config['ical_files'] and isinstance(config['ical_files'], str):
            self.ical_files = config['ical_files'].split(',')
        else:
            self.ical_files = config['ical_files']

        # additional configuration
        self.timezone = get_system_tz()
        self.num_font = ImageFont.truetype(
            fonts['NotoSans-SemiCondensed'], size=self.fontsize
        )

        # give an OK message
        logger.debug(f'{__name__} loaded')

    @staticmethod
    def flatten(values):
        """Flatten the values."""
        return [x for y in values for x in y]

    def generate_image(self):
        """Generate image for this module"""

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height
        events_height = 0

        logger.debug(f'Image size: {im_size}')

        # Create an image for black pixels and one for coloured pixels
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        # Allocate space for month-names, weekdays etc.
        month_name_height = int(im_height * 0.10)
        text_bbox_height = self.font.getbbox("hg")
        weekdays_height = int((abs(text_bbox_height[3]) + abs(text_bbox_height[1])) * 1.25)
        logger.debug(f"month_name_height: {month_name_height}")
        logger.debug(f"weekdays_height: {weekdays_height}")

        if self.show_events:
            logger.debug("Allocating space for events")
            calendar_height = int(im_height * 0.6)
            events_height = (
                    im_height - month_name_height - weekdays_height - calendar_height
            )
            logger.debug(f'calendar-section size: {im_width} x {calendar_height} px')
            logger.debug(f'events-section size: {im_width} x {events_height} px')
        else:
            logger.debug("Not allocating space for events")
            calendar_height = im_height - month_name_height - weekdays_height
            logger.debug(f'calendar-section size: {im_width} x {calendar_height} px')

        # Create a 7x6 grid and calculate icon sizes
        calendar_rows, calendar_cols = 6, 7
        icon_width = im_width // calendar_cols
        icon_height = calendar_height // calendar_rows
        logger.debug(f"icon_size: {icon_width}x{icon_height}px")

        # Calculate spacings for calendar area
        x_spacing_calendar = int((im_width % calendar_cols) / 2)
        y_spacing_calendar = int((im_height % calendar_rows) / 2)

        logger.debug(f"x_spacing_calendar: {x_spacing_calendar}")
        logger.debug(f"y_spacing_calendar :{y_spacing_calendar}")

        # Calculate positions for days of month
        grid_start_y = month_name_height + weekdays_height + y_spacing_calendar
        grid_start_x = x_spacing_calendar

        grid_coordinates = [
            (grid_start_x + icon_width * x, grid_start_y + icon_height * y)
            for y in range(calendar_rows)
            for x in range(calendar_cols)
        ]

        weekday_pos = [
            (grid_start_x + icon_width * _, month_name_height)
            for _ in range(calendar_cols)
        ]

        now = arrow.now(tz=self.timezone)

        # Set week-start of calendar to specified week-start
        if self.week_start == "Monday":
            cal.setfirstweekday(cal.MONDAY)
            week_start = now.shift(days=-now.weekday())
        else:
            cal.setfirstweekday(cal.SUNDAY)
            week_start = now.shift(days=-now.isoweekday())

        # Write the name of current month
        write(
            im_black,
            (0, 0),
            (im_width, month_name_height),
            str(now.format('MMMM', locale=self.language)),
            font=self.font,
            autofit=True,
        )

        # Set up week-names in local language and add to main section
        weekday_names = [
            week_start.shift(days=+_).format('ddd', locale=self.language)
            for _ in range(7)
        ]
        logger.debug(f'weekday names: {weekday_names}')

        for index, weekday in enumerate(weekday_pos):
            write(
                im_black,
                weekday,
                (icon_width, weekdays_height),
                weekday_names[index],
                font=self.font,
                autofit=True,
                fill_height=0.9,
            )

        # Create a calendar template and flatten (remove nesting)
        calendar_flat = self.flatten(cal.monthcalendar(now.year, now.month))
        # logger.debug(f" calendar_flat: {calendar_flat}")

        # Map days of month to co-ordinates of grid -> 3: (row2_x,col3_y)
        grid = {}
        for i in calendar_flat:
            if i != 0:
                grid[i] = grid_coordinates[calendar_flat.index(i)]
        # logger.debug(f"grid:{grid}")

        # remove zeros from calendar since they are not required
        calendar_flat = [num for num in calendar_flat if num != 0]

        # ensure all numbers have the same size
        fontsize_numbers = int(min(icon_width, icon_height) * 0.5)
        number_font = ImageFont.truetype(self.font.path, fontsize_numbers)

        # Add the numbers on the correct positions
        for number in calendar_flat:
            if number != int(now.day):
                write(
                    im_black,
                    grid[number],
                    (icon_width, icon_height),
                    str(number),
                    font=number_font,
                )

        # Draw a red/black circle with the current day of month in white
        icon = Image.new('RGBA', (icon_width, icon_height))
        current_day_pos = grid[int(now.day)]
        x_circle, y_circle = int(icon_width / 2), int(icon_height / 2)
        radius = int(icon_width * 0.2)
        ImageDraw.Draw(icon).ellipse(
            (
                x_circle - radius,
                y_circle - radius,
                x_circle + radius,
                y_circle + radius,
            ),
            fill='black',
            outline=None,
        )
        write(
            icon,
            (0, 0),
            (icon_width, icon_height),
            str(now.day),
            font=self.num_font,
            fill_height=0.5,
            colour='white',
        )
        im_colour.paste(icon, current_day_pos, icon)

        # If events should be loaded and shown...
        if self.show_events:

            # If this month requires 5 instead of 6 rows, increase event section height
            if len(cal.monthcalendar(now.year, now.month)) == 5:
                events_height += icon_height

            # If this month requires 4 instead of 6 rows, increase event section height
            elif len(cal.monthcalendar(now.year, now.month)) == 4:
                events_height += icon_height * 2

            # import the ical-parser
            # pylint: disable=import-outside-toplevel
            from inkycal.modules.ical_parser import iCalendar

            # find out how many lines can fit at max in the event section
            line_spacing = 2
            text_bbox_height = self.font.getbbox("hg")
            line_height = text_bbox_height[3] - text_bbox_height[1] + line_spacing
            max_event_lines = events_height // (line_height + line_spacing)

            # generate list of coordinates for each line
            events_offset = im_height - events_height
            event_lines = [
                (0, events_offset + int(events_height / max_event_lines * _))
                for _ in range(max_event_lines)
            ]

            # logger.debug(f"event_lines {event_lines}")

            # timeline for filtering events within this month
            month_start = arrow.get(now.floor('month'))
            month_end = arrow.get(now.ceil('month'))

            # fetch events from given iCalendars
            self.ical = iCalendar()
            parser = self.ical

            if self.ical_urls:
                parser.load_url(self.ical_urls)
            if self.ical_files:
                parser.load_from_file(self.ical_files)

            # Filter events for full month (even past ones) for drawing event icons
            month_events = parser.get_events(month_start, month_end, self.timezone)
            parser.sort()
            self.month_events = month_events

            # Initialize days_with_events as an empty list
            days_with_events = []

            # Handle multi-day events by adding all days between start and end
            for event in month_events:

                # Convert start and end dates to arrow objects with timezone
                start = arrow.get(event['begin'].date(), tzinfo=self.timezone)
                end = arrow.get(event['end'].date(), tzinfo=self.timezone)

                # Use arrow's range function for generating dates
                for day in arrow.Arrow.range('day', start, end):
                    day_num = int(day.format('D'))  # get day number using arrow's format method
                    if day_num not in days_with_events:
                        days_with_events.append(day_num)

            # remove duplicates (more than one event in a single day)
            days_with_events = sorted(set(days_with_events))
            self._days_with_events = days_with_events

            # Draw a border with specified parameters around days with events
            for days in days_with_events:
                if days in grid:
                    draw_border(
                        im_colour,
                        grid[days],
                        (icon_width, icon_height),
                        radius=6
                    )

            # Filter upcoming events until 4 weeks in the future
            parser.clear_events()
            upcoming_events = parser.get_events(now, now.shift(weeks=4), self.timezone)
            self._upcoming_events = upcoming_events

            # delete events which won't be able to fit (more events than lines)
            upcoming_events = upcoming_events[:max_event_lines]

            # Check if any events were found in the given timerange
            if upcoming_events:

                # Find out how much space (width) the date format requires
                lang = self.language

                date_width = int(max((
                    self.font.getlength(events['begin'].format(self.date_format, locale=lang))
                    for events in upcoming_events)) * 1.1
                                 )

                time_width = int(max((
                    self.font.getlength(events['begin'].format(self.time_format, locale=lang))
                    for events in upcoming_events)) * 1.1
                                 )

                text_bbox_height = self.font.getbbox("hg")
                line_height = text_bbox_height[3] + line_spacing

                event_width_s = im_width - date_width - time_width
                event_width_l = im_width - date_width

                # Display upcoming events below calendar TODO: not used?
                # tomorrow = now.shift(days=1).floor('day')
                # in_two_days = now.shift(days=2).floor('day')

                cursor = 0
                for event in upcoming_events:
                    if cursor < len(event_lines):
                        event_duration = (event['end'] - event['begin']).days
                        if event_duration > 1:
                            # Format the duration using Arrow's localization
                            days_translation = arrow.get().shift(days=event_duration).humanize(only_distance=True,
                                                                                               locale=lang)
                            the_name = f"{event['title']} ({days_translation})"
                        else:
                            the_name = event['title']
                        the_date = event['begin'].format(self.date_format, locale=lang)
                        the_time = event['begin'].format(self.time_format, locale=lang)
                        # logger.debug(f"name:{the_name}   date:{the_date} time:{the_time}")

                        if now < event['end']:
                            write(
                                im_colour,
                                event_lines[cursor],
                                (date_width, line_height),
                                the_date,
                                font=self.font,
                                alignment='left',
                            )

                            # Check if event is all day
                            if parser.all_day(event):
                                write(
                                    im_black,
                                    (date_width, event_lines[cursor][1]),
                                    (event_width_l, line_height),
                                    the_name,
                                    font=self.font,
                                    alignment='left',
                                )
                            else:
                                write(
                                    im_black,
                                    (date_width, event_lines[cursor][1]),
                                    (time_width, line_height),
                                    the_time,
                                    font=self.font,
                                    alignment='left',
                                )

                                write(
                                    im_black,
                                    (date_width + time_width, event_lines[cursor][1]),
                                    (event_width_s, line_height),
                                    the_name,
                                    font=self.font,
                                    alignment='left',
                                )
                            cursor += 1
            else:
                symbol = '- '

                while self.font.getlength(symbol) < im_width * 0.9:
                    symbol += ' -'
                write(
                    im_black,
                    event_lines[0],
                    (im_width, line_height),
                    symbol,
                    font=self.font,
                )

        # return the images ready for the display
        return im_black, im_colour
