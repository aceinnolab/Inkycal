#!python3

"""
Inkycal WallCalendar Module
"""

# pylint: disable=logging-fstring-interpolation

import calendar as cal
import arrow
from datetime import datetime, timedelta
from inkycal.modules.template import inkycal_module
from inkycal.custom import *
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__) 


class WallCalendar(inkycal_module):
    """Calendar class
    Create monthly calendar and show events from given icalendars
    """

    name = "Wall Calendar - Show monthly calendar with events from iCalendars"

    optional = {
        "week_starts_on": {
            "label": "When does your week start? (default=Monday)",
            "options": ["Monday", "Sunday"],
            "default": "Monday",
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
        "mark_previous_days": {
            "label": "Mark previous days? (default = True)",
            "options": [True, False],
            "default": True,
        },
        "number_of_weeks": {
            "label": "Number of weeks to display (default = 4)",
            "default": 4,
        },
        "shade_weekend": {
            "label": "Shade the weekend days? (default = True)",
            "options": [True, False],
            "default": True,
        },
    }

    def __init__(self, config):
        """Initialize inkycal_wallcalendar module"""

        super().__init__(config)
        config = config['config']

        self.ical = None
        self.month_events = None
        self._upcoming_events = None
        self._days_with_events = None

        # optional parameters
        self.weekstart = config['week_starts_on']
        self.date_format = config["date_format"]
        self.time_format = config['time_format']
        self.language = config['language']
        self.mark_previous_days = config['mark_previous_days']
        self.number_of_weeks = config['number_of_weeks']
        self.shade_the_weekend = config['shade_weekend']

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
            fonts['NotoSansUI-Regular'], size=self.fontsize
        )
        self.font = ImageFont.truetype(
            fonts['Caveat-Regular'], size=self.fontsize
        )

        # give an OK message
        print(f'{__name__} loaded')

    @staticmethod
    def flatten(values):
        """Flatten the values."""
        return [x for y in values for x in y]
    
    def shade_weekend(self, image, day_origins, day_width, day_height, sat_index, sun_index, num_rows):
        """Shade the weekend days on the image."""
        for index in [sat_index, sun_index]:
            origin = day_origins[index]
            end = day_origins[index + ((num_rows-1) * 7)]
            x, y = end
            x += day_width
            y += day_height
            end = (x, y)
            image.rectangle([origin, end], fill='#ddd', width=0)
    
    def calculate_max_lines(self, pixel_height, line_height):
        # Calculate the number of lines that fit rounded down
        num_lines = pixel_height // line_height
        
        return num_lines
    
    def calculate_time_width(self, time_string="00:00"):
        # Measure the width of the time string
        text_width = self.font.getbbox(time_string)[2] - self.font.getbbox(time_string)[0]
        
        # Add 10% padding on either side (20% total)
        total_width = text_width * 1.20
        
        return total_width
    
    def calculate_lines_for_events(self, events, max_width, time_width):
        print("calculate_lines_for_events: Started")
        
        def wrapped_lines(text, max_line_width):
            words = text.split()
            lines = 0
            
            while words:
                line = ''
                while words:
                    word = words[0]
                    new_line = line + word + ' '
                    new_line_width = self.font.getbbox(new_line)[2]
            
                    if new_line_width <= max_line_width:
                        # Add word to line and remove it from the list
                        line = new_line
                        words.pop(0)
                    else:
                        # If the line is empty, start truncating the word
                        if not line:
                            truncated_word = truncate_word(word, max_line_width)
                            line = truncated_word + ' '
                            words.pop(0)
                        break  # Move to the next line if the line is not empty
            
                lines += 1
            
            return lines
        
        def truncate_word(word, max_width):
            while word:
                ellipsis_width = self.font.getbbox('...')[2]
                truncated_word_width = self.font.getbbox(word)[2] + ellipsis_width
                if truncated_word_width <= max_width:
                    return word + '...'
                word = word[:-1]  # Remove the last character
            
            return '...'  # Return ellipsis if the word is too short to fit
        
        # Iterate through each event in the list.
        for event in events:
            print(f"Processing event: '{event['title']}'")
            # Calculate the number of lines required for the event's title and store it in the event dictionary.
            if event['is_all_day']:
                event['lines_required'] = wrapped_lines(event['title'], max_width + time_width)
            else:
                event['lines_required'] = wrapped_lines(event['title'], max_width)
            print(f"Lines required for event '{event['title']}': {event['lines_required']}")
        
        print("calculate_lines_for_events: Finished")

        
        # Iterate through each event in the list.
        for event in events:
            # Calculate the number of lines required for the event's title and store it in the event dictionary.
            if event['is_all_day']:
                event['lines_required'] = wrapped_lines(event['title'], max_width + time_width)
            else:
                event['lines_required'] = wrapped_lines(event['title'], max_width)

    def mark_all_day_events(self, events):
        for event in events.copy():  # Create a copy for iteration
            start_time = event['begin']
            end_time = event['end']
            
            print(f"mark_all_day_events: Processing event '{event['title']}' from {start_time} to {end_time}")

            # Events spanning more than one day will be converted to all-day events including the first and last days

            # Check if the event spans more than one day
            if end_time.date() > start_time.date():
                # Check if the event ends exactly at the start of the next day - 
                # because "all-day" events actually end at the start of the next day
                if end_time.hour == 0 and end_time.minute == 0 and \
                   end_time.day == start_time.shift(days=1).day:
                    # Adjust the end time to the end of the current day
                    end_time = end_time.shift(days=-1).ceil('day')
                    event['end'] = end_time
                    event['is_all_day'] = True
                    print(f"Adjusted end time for all-day event '{event['title']}' to {end_time}")
                else:
                    events.remove(event)  # Remove the original event
                    current_time = start_time
                    while current_time.date() <= end_time.date():
                        new_event = event.copy()  # Copy the original event
                        new_event['begin'] = current_time.floor('day')  # Start at midnight of the current day
                        new_event['end'] = current_time.ceil('day')  # End at midnight of the next day
                        new_event['is_all_day'] = True  # Mark as an all-day event
                        events.append(new_event)
                        print(f"Created new all-day event '{new_event['title']}' from {new_event['begin']} to {new_event['end']}")
                        current_time = current_time.shift(days=1)  # Move to the next day
            else:
                event['is_all_day'] = False
    
    def allocate_lines(self, events, max_lines_per_day):
        total_required_lines = sum(event['lines_required'] for event in events)

        if total_required_lines <= max_lines_per_day:
            for event in events:
                event['lines_allocated'] = event['lines_required']
        else:
            self.allocate_truncated_lines(events, max_lines_per_day)

    def allocate_truncated_lines(self, events, max_lines):
        current_time = arrow.now().datetime

        # Sort events by priority (e.g., starting time, then all-day)
        events.sort(key=lambda x: (x['begin'], not x['is_all_day']))
        
        # Allocate no lines to all events
        for event in events:
            event['lines_allocated'] = 0
        
        # If the total number of events is greater than the max lines, allocate zero lines to past events
        if len(events) > max_lines:
            for event in events:
                if event['begin'] < current_time:
                    event['lines_allocated'] = 0
                else:
                    event['lines_allocated'] = 1
                    max_lines -= 1

                if max_lines <= 1:
                    break
        else:
            for event in events:
                event['lines_allocated'] = 1
                max_lines -= 1

        # Allocate additional lines to future events if space is available
        for event in events:
            if max_lines > 0 and event['lines_required'] > 1 and event['lines_allocated'] > 0:
                additional_lines = min(max_lines, event['lines_required'] - 1)
                event['lines_allocated'] += additional_lines
                max_lines -= additional_lines
    
    def write_allday_event_title(self, image, origin, event, day_width, line_height, space_above_event, day_width_padding):
        x, y = origin  
        x += 2
        y += space_above_event  # Increase y by space_above_event
        new_origin = (int(x), int(y))
        height = event['lines_allocated'] * line_height
        end = (int(x + day_width - 3), int(y + height))
        draw_background = ImageDraw.Draw(image)
        draw_background.rectangle([new_origin, end], fill='#fff', outline='#000', width=0)
        write(
            image,
            new_origin,  # tuple of xy coordinates
            (int(day_width), int(height)),  # size of box
            event['title'],  # string containing event title
            font=self.font,
            autofit=True,
            alignment='center',
            colour='black'
        )
    
    def write_skipped_event_count(self, image, origin, skipped_count, day_width, line_height, space_above_event, day_width_padding):
        x, y = origin  
        x += 2
        y += space_above_event  # Increase y by space_above_event
        new_origin = (int(x), int(y))
        height = line_height
        write(
            image,
            new_origin,  # tuple of xy coordinates
            (int(day_width), int(height)),  # size of box
            str(skipped_count) + " more events...",  # string 
            font=self.font,
            autofit=True,
            alignment='center',
            colour='black'
        )

    def write_event_time(self, image, origin, event, time_width, line_height, space_above_event, day_width_padding):
        x, y = origin  
        x += day_width_padding
        y += space_above_event  # Increase y by space_above_event
        new_origin = (int(x), int(y))
        write(
            image,
            new_origin,  # tuple of xy coordinates
            (int(time_width), int(line_height*1.2)),  # size of box
            event['begin'].format('HH:mm'),  # string containing event time
            font=self.font,
            autofit=False,
            alignment='left'
        )
    
    def write_event_title(self, image, origin, event, time_width, width_for_event_title, line_height, space_above_event, day_width_padding):
        print(f"write_event_title: Starting for event '{event['title']}'")
        
        words = event['title'].split()
        lines = []
        allocated_lines = event['lines_allocated']  # Number of lines allocated for this event
        current_line = 1  # Initialize a counter for the current line
        
        print(f"write_event_title: Words to process: {words}")
        print(f"write_event_title: Allocated lines: {allocated_lines}")
        
        while words:
            line = ''
            print(f"write_event_title: Starting new line. Current line: {current_line}")
        
            # Add words to the line until the maximum line width is reached.
            while words and (self.font.getbbox(line + words[0])[2] <= width_for_event_title):
                print(f"write_event_title: Adding '{words[0]}' to line")
                line += words.pop(0) + ' '

            # If the line is empty and adding the word exceeds the maximum line width
            if not line and words and (self.font.getbbox(words[0])[2] > width_for_event_title):
                print(f"write_event_title: Word '{words[0]}' exceeds maximum line width, truncating with ellipsis")
                word = words.pop(0)
                while self.font.getbbox(line + word + '...')[2] > width_for_event_title:
                    word = word[:-1]  # Remove one letter at a time
                line = word + '...'

            if current_line == allocated_lines and words:
                print(f"write_event_title: Last allocated line reached, adding ellipsis")
                line = line.rstrip() + '...'
            
            lines.append(line)
            print(f"write_event_title: Completed line '{line}'")
            current_line += 1
        
            if current_line > allocated_lines:
                print("write_event_title: Exceeded allocated lines, breaking")
                break
        
        print(f"write_event_title: Final lines: {lines}")
        
        # Loop through the lines, but only up to the number of allocated lines
        event_line_offset = 0
        for i, line in enumerate(lines):
            if i >= allocated_lines:
                print(f"write_event_title: Skipping line {i} as it exceeds allocated lines")
                break
        
            x, y = origin
            x += day_width_padding + time_width
            y += space_above_event + event_line_offset
            new_origin = (int(x), int(y))
            print(f"write_event_title: Writing line '{line}' at {new_origin}")
        
            # The 'write' function call is assumed to be a custom function. Add debug prints there too if necessary.
            write(
                image,
                new_origin,
                (int(width_for_event_title), int(line_height*1.2)),
                line,
                font=self.font,
                autofit=False,
                alignment='left'
            )
            event_line_offset += int(line_height)
        
        print("write_event_title: Completed writing event title")

                                    
    def generate_image(self):
        """Generate an image for this module."""
        
        # Set the number of weeks to display in the calendar
        num_weeks = self.number_of_weeks
        date_height = 30
        day_width_padding = 5
        
        # Calculate the image dimensions taking into account padding
        im_width = int(self.height - (2 * self.padding_left))
        im_height = int(self.width - (2 * self.padding_top))
        im_size = im_width, im_height  # Tuple representing the image size
        now = arrow.now(tz=self.timezone)  # Get the current time based on timezone
        logger.info(f'Image size: {im_size}')  # Log the image size for debugging
        
        # Create two images, one for black pixels and one for colored pixels
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')
        
        # Calculate the heights for different sections of the calendar
        month_name_height = int(im_height * 0.10)  # Height for the month name
        day_name_height = int(im_height * 0.05)    # Height for the day names
        grid_height = im_height * 0.85             # Height for the main grid
        day_width = im_width / 7                   # Width of each day cell
        day_height = grid_height / num_weeks       # Height of each day cell
        
        # Create drawing contexts for both images
        draw = ImageDraw.Draw(im_black)
        draw_colour = ImageDraw.Draw(im_colour)
        
        # Write the current month's name on the black image
        write(
            im_black,
            (0, 0),
            (im_width, month_name_height),
            str(now.format('MMMM', locale=self.language)),
            font=self.num_font,
            autofit=True,
        )
        
        # Set the first weekday of the calendar based on the configuration
        if self.weekstart == "Monday":
            cal.setfirstweekday(cal.MONDAY)
            weekstart = now.shift(days=-now.weekday())
            saturday_index = 5  # Index of Saturday when week starts on Monday
            sunday_index = 6    # Index of Sunday when week starts on Monday
        else:
            cal.setfirstweekday(cal.SUNDAY)
            weekstart = now.shift(days=-now.isoweekday())
            saturday_index = 6  # Index of Saturday when week starts on Sunday
            sunday_index = 0    # Index of Sunday when week starts on Sunday
        
        # Generate names of weekdays in the specified language
        weekday_names = [
            weekstart.shift(days=+_).format('ddd', locale=self.language)
            for _ in range(7)
        ]
        # Generate a list of dates
        current_dates = [weekstart + timedelta(days=i) for i in range(num_weeks*7)]
        
        # Calculate the origin points (top-left corners) for each day cell in the grid
        day_origins = []
        for row in range(num_weeks):  # Iterate over each row (week)
            for col in range(7):  # Iterate over each column (day)
                x = int(col * day_width)  # X-coordinate of the cell
                y = int((row * day_height) + (im_height * 0.15))  # Y-coordinate of the cell
                day_origins.append((x, y))  # Add the origin point to the list
        
        # Calculate the start and end points for shading the Sunday column
        if self.shade_the_weekend:
            self.shade_weekend(draw, day_origins, day_width, day_height, saturday_index, sunday_index, num_weeks)
        
        # Write the names of the weekdays on the black image
        for index in range(7):
            write(
                im_black,
                (int(index * day_width), int(im_height * 0.1)),
                (int(day_width), int(day_name_height)),
                weekday_names[index],
                font=self.font,
                autofit=True,
                fill_height=0.5,
            )
        
        # Draw horizontal and vertical lines to create the grid
        start_height = int(im_height * 0.15)
        height_range = im_height - start_height
        horizontal_lines = num_weeks + 1
        vertical_lines = 8
        
        # Drawing horizontal lines
        for i in range(horizontal_lines - 1):        
            y = start_height + i * (height_range / (horizontal_lines - 1))
            draw.line(((0, y), (im_width, y)), fill='black', width=2)
        draw.line(((0, im_height - 2), (im_width, im_height - 2)), fill='black', width=2)
        
        # Drawing vertical lines
        for i in range(vertical_lines - 1):
            x = i * day_width
            draw.line(((x, im_height*0.15), (x, im_height)), fill='black', width=2)
        draw.line(((im_width - 2, im_height*0.15), (im_width - 2, im_height)), fill='black', width=2)
        
        # Write the day numbers 
        for index in range(len(day_origins)):
            date_str = current_dates[index].strftime('%-d')  # Get day number as a string
            x, y = day_origins[index]  
            x += 5 
            new_origin = (x, y)
            # Write the day number in the adjusted position
            write(
                im_black,
                new_origin,  # tuple of xy coordinates
                (int(day_width), date_height),  # size of box
                date_str,  # string containing the day of the month
                font=self.num_font,
                autofit=True,
                fill_height=0.8,
                alignment='left'
            )
        

        events_allowed_height = day_height - date_height
        line_height = self.font.getbbox("AWgp")[3] * 1.05
        max_number_of_lines = self.calculate_max_lines(events_allowed_height, line_height)
        time_width = self.calculate_time_width()
        width_for_event_title = day_width - time_width - (day_width_padding * 2)
        
        from inkycal.modules.ical_parser import iCalendar
        # fetch events from given icalendars
        self.ical = iCalendar()
        parser = self.ical
        
        if self.ical_urls:
            parser.load_url(self.ical_urls)
        if self.ical_files:
            parser.load_from_file(self.ical_files)
            
        month_events = parser.get_events(current_dates[0], current_dates[-1], self.timezone)
        parser.sort()

        # Mark all-day events before processing individual days
        self.mark_all_day_events(month_events)

        self.month_events = month_events

        combined_data = []
        for index, date in enumerate(current_dates):
            origin = day_origins[index]
            # Find events starting on this date
            events_on_this_day = [event for event in self.month_events if event['begin'].format('YYYY-MM-DD') == date.format('YYYY-MM-DD')]
            self.calculate_lines_for_events(events_on_this_day, width_for_event_title, time_width)
            self.allocate_lines(events_on_this_day, max_number_of_lines)
            # Add the combined data to the array
            combined_data.append({'date': date, 'origin': origin, 'events': events_on_this_day})
        
        for data in combined_data:
            print(f"Date: {data['date']}, Origin: {data['origin']}, Events: {data['events']}")
            space_above_event = date_height
            data['future_skipped_count'] = 0
            
            # Sort the events list
            data['events'] = sorted(data['events'], key=lambda e: (not e['is_all_day'], e['begin'] if not e['is_all_day'] else e['title']))

            for event in data['events']:
                if event['is_all_day']:
                    self.write_allday_event_title(
                        im_colour, 
                        data['origin'], 
                        event,
                        day_width, 
                        line_height, 
                        space_above_event,
                        day_width_padding
                    )
                    space_above_event += event['lines_allocated'] * line_height
                
                elif event['lines_allocated'] != 0:
                    self.write_event_time(
                        im_black, 
                        data['origin'], 
                        event, 
                        time_width, 
                        line_height, 
                        space_above_event,
                        day_width_padding
                    )
                    self.write_event_title(
                        im_black, 
                        data['origin'], 
                        event, 
                        time_width,
                        width_for_event_title, 
                        line_height, 
                        space_above_event,
                        day_width_padding
                    )
                    space_above_event += event['lines_allocated'] * line_height
                
                elif event['lines_allocated'] == 0 and event['begin'] > arrow.now():
                    print(f"Counting event '{event['title']}' as it has no allocated lines and begins in the future")
                    data['future_skipped_count'] += 1
                
                if data['future_skipped_count'] > 0:
                    self.write_skipped_event_count(
                        im_black, 
                        data['origin'], 
                        data['future_skipped_count'], 
                        day_width, 
                        line_height, 
                        space_above_event, 
                        day_width_padding
                    )
                
                
        if self.mark_previous_days:
            # Draw a cross on days that are in the past
            for index in range(len(day_origins)):
                if current_dates[index] < arrow.now().floor('day'):
                    origin_x, origin_y = day_origins[index]
                    end_x = origin_x + day_width
                    end_y = origin_y + day_height
                    # Draw a line from top-left to bottom-right
                    draw_colour.line((day_origins[index], (end_x, end_y)), fill='black', width=2)
                    start_x = origin_x
                    start_y = origin_y + day_height
                    end_x = origin_x + day_width
                    end_y = origin_y
                    # Draw a line from bottom-left to top-right
                    draw_colour.line(((start_x, start_y), (end_x, end_y)), fill='black', width=2)
                                   
        # Rotate the images by 90 degrees
        im_black = im_black.rotate(90, expand=True)
        im_colour = im_colour.rotate(90, expand=True)
        
        # Return the final images
        return im_black, im_colour


if __name__ == '__main__':
    print(f'running {__name__} in standalone mode')
