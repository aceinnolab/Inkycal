#!python3

"""
Inkycal Calendar Module
Copyright by aceinnolab
"""
import calendar
import locale

import arrow

from inkycal.custom import *
from inkycal.custom.canvas import Canvas
from inkycal.custom.flexbox import Flexbox
from inkycal.modules.template import inkycal_module

logger = logging.getLogger(__name__)


class Calendar(inkycal_module):
    """Calendar class
    Create monthly calendar and show events from given icalendars
    """

    def __init__(self, config, week_start: str = "Monday", show_events: bool = True, date_format: str = "D MMM",
                 time_format="HH:mm",):
        """Initialize inkycal_calendar module"""

        super().__init__(config)
        self.week_start = week_start
        self.show_events = show_events
        self.date_format = date_format
        self.time_format = time_format
        self.language = config["language"]

        # Additional config
        self.timezone = get_system_tz()
        self.num_font = ImageFont.truetype(
            fonts['NotoSans-SemiCondensed'], size=self.fontsize)

        # give an OK message
        print(f'{__name__} loaded')



    @staticmethod
    def load_icalendar_from_url(ical_url:str, date_start:arrow.arrow, date_end:arrow.arrow, timezone:str) -> dict:

        ical = iCalendar()

        if not ical_url.startswith("http"):
            raise AssertionError(f"The provided URL to iCalendar does not seem to be valid: {ical_url}")

        ical.load_url(ical_url)

        # Get events between date_start and date_end
        events_in_timerange = ical.get_events(date_start, date_end, timezone)
        ical.sort()
        return events_in_timerange

    @staticmethod
    def load_icalendar_from_file(ical_file: str, date_start:arrow.arrow, date_end:arrow.arrow, timezone:str) -> dict:

        ical = iCalendar()

        if not os.path.exists(ical_file):
            raise FileNotFoundError(f"No iCalendar file could be found in the provided location: {ical_file}")

        ical.load_from_file(ical_file)

        # Get events between date_start and date_end
        events_in_timerange = ical.get_events(date_start, date_end, timezone)
        ical.sort()
        return events_in_timerange



    def generate_month_name_canvas(self, month_name:str, row_height:int) -> Image:
        flexbox = Flexbox(
            width=self.width,
            height=row_height,
            padding=1, num_rows=1, num_cols=1,
            font_size=12, font_path=self.font.path, border_radius=1, show_border=True
        )
        flexbox.add_text(text=month_name, row=1, col=1)

        return flexbox.image

    def generate_seven_col_row(self, content:list, row_height:int) -> Image:
        flexbox = Flexbox(
            width=self.width,
            height=row_height,
            padding=1, num_rows=1, num_cols=len(content),
            font_size=12, font_path=self.num_font.path, border_radius=1, show_border=True
        )
        for index, item in enumerate(content, start=1):
            flexbox.add_text(text=str(item) if item != 0 else "", row=1, col=index)

        return flexbox.image

    @staticmethod
    def generate_monthly_calendar(year, month):
        # Create a Calendar object
        cal = calendar.Calendar()
        cal.setfirstweekday(0)

        month_cal = cal.monthdayscalendar(year, month)
        current_date = int(arrow.now().format("D"))
        month_calendar = []
        found = False
        for week in month_cal:
            if current_date not in week and not found:
                found = True
                continue
            else:
                month_calendar.append(week)

        month_calendar.insert(0, arrow.now().format("MMMM"))
        next_month = cal.monthdayscalendar(year, month + 1 if month + 1 <= 12 else 0)
        next_month.insert(0, arrow.now().shift(months=1).format("MMMM"))

        month_calendar.extend(next_month)

        return month_calendar

    @staticmethod
    def get_weekday_names(language, week_start_day=0):
        # Set the desired locale using the ISO two-letter language/country code
        locale_name = f"{language}_{language.upper()}"
        locale.setlocale(locale.LC_TIME, locale_name)

        # Get the weekday names based on the specified week start day
        weekday_names = []
        for i in range(7):
            weekday = (week_start_day + i) % 7
            weekday_names.append(locale.nl_langinfo(locale.DAY_1 + weekday))

        return weekday_names

    def generate_image(self):
        """Generate image for this module"""

        canvas = Canvas(width=self.width, height=self.height)

        weekday_names = [arrow.now().shift(days=i).format("dddd", locale=self.language) for i in range(7)]
        weekday_to_int = {weekday: index for index, weekday in enumerate(weekday_names)}

        now = arrow.now(tz=self.timezone)
        line_height = self.font.getbbox("hg")[-1]

        weekdays_height = 30
        calendar_height = self.height - weekdays_height

        # allocate 40% of space for events below the calendar if height is bigger than 500px
        # allocate 20% of space for events below the calendar if height is smaller than 500px
        # if events should not be shown, allocate the entire space for the calendar
        if self.show_events:
            if self.height >= 500:
                calendar_height = int(self.height * 0.4) - weekdays_height
            else:
                calendar_height = int(self.height * 0.2) - weekdays_height

        start_date = arrow.get(self.week_start, "dddd")
        weekday_names = [start_date.shift(days=i).format("ddd", locale=self.language) for i in range(7)]
        weekday_im = self.generate_seven_col_row(weekday_names, weekdays_height)
        canvas.paste_image(weekday_im)

        # dynamic row calendar
        canvas_calendar = Flexbox(
            width=self.width, height=calendar_height,
            padding=1, num_rows=calendar_height // 50,
            num_cols=1, font_size=12, font_path=self.font.path,
            border_radius=1, show_border=True
        )

        if canvas_calendar.num_rows <= 1:
            raise AssertionError("calendar space is too small. Please increase the height of this module")


        monthly = self.generate_monthly_calendar(arrow.now().year, int(arrow.now().format("M")))[:canvas_calendar.num_rows]

        for item in monthly:
            if isinstance(item, str):
                im = self.generate_month_name_canvas(item, canvas_calendar.row_height)
            else:
                im = self.generate_seven_col_row(item, canvas_calendar.row_height)
            canvas.paste_image(image=im)

        wip = "here"




        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height

        logger.info(f'Image size: {im_size}')

        # Create an image for black pixels and one for coloured pixels
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        # Allocate space for month-names, weekdays etc.
        month_name_height = int(im_height * 0.10)
        weekdays_height = int(self.font.getsize('hg')[1] * 1.25)
        logger.debug(f"month_name_height: {month_name_height}")
        logger.debug(f"weekdays_height: {weekdays_height}")

        if self.show_events:
            logger.debug("Allocating space for events")
            calendar_height = int(im_height * 0.6)
            events_height = im_height - month_name_height - weekdays_height - calendar_height
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
        grid_start_y = (month_name_height + weekdays_height + y_spacing_calendar)
        grid_start_x = x_spacing_calendar

        grid_coordinates = [(grid_start_x + icon_width * x, grid_start_y + icon_height * y)
                            for y in range(calendar_rows) for x in range(calendar_cols)]

        weekday_pos = [(grid_start_x + icon_width * _, month_name_height) for _ in
                       range(calendar_cols)]

        now = arrow.now(tz=self.timezone)

        # Set weekstart of calendar to specified weekstart
        if self.week_start == "Monday":
            cal.setfirstweekday(cal.MONDAY)
            weekstart = now.shift(days=- now.weekday())
        else:
            cal.setfirstweekday(cal.SUNDAY)
            weekstart = now.shift(days=- now.isoweekday())

        # Write the name of current month
        write(im_black, (0, 0), (im_width, month_name_height),
              str(now.format('MMMM', locale=self.language)), font=self.font,
              autofit=True)

        # Set up weeknames in local language and add to main section
        weekday_names = [weekstart.shift(days=+_).format('ddd', locale=self.language)
                         for _ in range(7)]
        logger.debug(f'weekday names: {weekday_names}')

        for _ in range(len(weekday_pos)):
            write(
                im_black,
                weekday_pos[_],
                (icon_width, weekdays_height),
                weekday_names[_],
                font=self.font,
                autofit=True,
                fill_height=1.0
            )

        # Create a calendar template and flatten (remove nestings)
        flatten = lambda z: [x for y in z for x in y]
        calendar_flat = flatten(cal.monthcalendar(now.year, now.month))
        # logger.debug(f" calendar_flat: {calendar_flat}")

        # Map days of month to co-ordinates of grid -> 3: (row2_x,col3_y)
        grid = {}
        for i in calendar_flat:
            if i != 0:
                grid[i] = grid_coordinates[calendar_flat.index(i)]
        # logger.debug(f"grid:{grid}")

        # remove zeros from calendar since they are not required
        calendar_flat = [num for num in calendar_flat if num != 0]

        # Add the numbers on the correct positions
        for number in calendar_flat:
            if number != int(now.day):
                write(im_black, grid[number], (icon_width, icon_height),
                      str(number), font=self.num_font, fill_height=0.5, fill_width=0.5)

        # Draw a red/black circle with the current day of month in white
        icon = Image.new('RGBA', (icon_width, icon_height))
        current_day_pos = grid[int(now.day)]
        x_circle, y_circle = int(icon_width / 2), int(icon_height / 2)
        radius = int(icon_width * 0.2)
        ImageDraw.Draw(icon).ellipse(
            (x_circle - radius, y_circle - radius, x_circle + radius, y_circle + radius),
            fill='black', outline=None)
        write(icon, (0, 0), (icon_width, icon_height), str(now.day),
              font=self.num_font, fill_height=0.5, colour='white')
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
            from inkycal.custom.ical_parser import iCalendar

            # find out how many lines can fit at max in the event section
            line_spacing = 0
            max_event_lines = events_height // (self.font.getsize('hg')[1] +
                                                line_spacing)

            # generate list of coordinates for each line
            events_offset = im_height - events_height
            event_lines = [(0, events_offset + int(events_height / max_event_lines * _))
                           for _ in range(max_event_lines)]

            # logger.debug(f"event_lines {event_lines}")

            # timeline for filtering events within this month
            month_start = arrow.get(now.floor('month'))
            month_end = arrow.get(now.ceil('month'))

            # fetch events from given icalendars
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

            # find out on which days of this month events are taking place
            days_with_events = [int(events['begin'].format('D')) for events in
                                month_events]

            # remove duplicates (more than one event in a single day)
            list(set(days_with_events)).sort()
            self._days_with_events = days_with_events

            # Draw a border with specified parameters around days with events
            for days in days_with_events:
                if days in grid:
                    draw_border(
                        im_colour,
                        grid[days],
                        (icon_width, icon_height),
                        radius=6,
                        thickness=1,
                        shrinkage=(0.4, 0.2)
                    )

            # Filter upcoming events until 4 weeks in the future
            parser.clear_events()
            upcoming_events = parser.get_events(now, now.shift(weeks=4),
                                                self.timezone)
            self._upcoming_events = upcoming_events

            # delete events which won't be able to fit (more events than lines)
            upcoming_events = upcoming_events[:max_event_lines]

            # Check if any events were found in the given timerange
            if upcoming_events:

                # Find out how much space (width) the date format requires
                lang = self.language

                date_width = int(max([self.font.getsize(
                    events['begin'].format(self.date_format, locale=lang))[0]
                                      for events in upcoming_events]) * 1.1)

                time_width = int(max([self.font.getsize(
                    events['begin'].format(self.time_format, locale=lang))[0]
                                      for events in upcoming_events]) * 1.1)

                line_height = self.font.getsize('hg')[1] + line_spacing

                event_width_s = im_width - date_width - time_width
                event_width_l = im_width - date_width

                # Display upcoming events below calendar
                tomorrow = now.shift(days=1).floor('day')
                in_two_days = now.shift(days=2).floor('day')

                cursor = 0
                for event in upcoming_events:
                    if cursor < len(event_lines):
                        name = event['title']
                        date = event['begin'].format(self.date_format, locale=lang)
                        time = event['begin'].format(self.time_format, locale=lang)
                        # logger.debug(f"name:{name}   date:{date} time:{time}")

                        if now < event['end']:
                            write(im_colour, event_lines[cursor], (date_width, line_height),
                                  date, font=self.font, alignment='left')

                            # Check if event is all day
                            if parser.all_day(event):
                                write(im_black, (date_width, event_lines[cursor][1]),
                                      (event_width_l, line_height), name, font=self.font,
                                      alignment='left')
                            else:
                                write(im_black, (date_width, event_lines[cursor][1]),
                                      (time_width, line_height), time, font=self.font,
                                      alignment='left')

                                write(im_black, (date_width + time_width, event_lines[cursor][1]),
                                      (event_width_s, line_height), name, font=self.font,
                                      alignment='left')
                            cursor += 1
            else:
                symbol = '- '
                while self.font.getsize(symbol)[0] < im_width * 0.9:
                    symbol += ' -'
                write(im_black, event_lines[0],
                      (im_width, self.font.getsize(symbol)[1]), symbol,
                      font=self.font)

        # return the images ready for the display
        return im_black, im_colour


if __name__ == '__main__':
    print(f'running {__name__} in standalone mode')
