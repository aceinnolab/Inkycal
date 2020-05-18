#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Agenda module for Inky-Calendar Project
Copyright by aceisace
"""

from inkycal.custom import *
import calendar as cal
import arrow
from ical_parser import icalendar

size = (400, 520)
config = {'week_starts_on': 'Monday', 'ical_urls': ['https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics']}


class agenda:
  """Agenda class
  Create agenda and show events from given icalendars
  """
  logger = logging.getLogger(__name__)
  logging.basicConfig(level=logging.DEBUG)

  def __init__(self, section_size, section_config):
    """Initialize inkycal_agenda module"""
    self.name = os.path.basename(__file__).split('.py')[0]
    self.config = section_config
    self.width, self.height = section_size
    self.background_colour =  'white'
    self.font_colour = 'black'
    self.fontsize = 12
    self.font = ImageFont.truetype(
      fonts['NotoSans-SemiCondensed'], size = self.fontsize)
    self.padding_x = 0.02 #rename to margin?
    self.padding_y = 0.05

    # Section specific config
    # Format for formatting dates
    self.date_format = 'D MMM'
    # Fromat for formatting event timings
    self.event_format = "HH:mm" #use auto for 24/12 hour format?
    self.language = 'en' # Grab from settings file?
    self.timezone = get_system_tz()
    # urls of icalendars
    self.ical_urls = config['ical_urls']
    # filepaths of icalendar files
    self.ical_files = []
    print('{0} loaded'.format(self.name))

  def set(self, **kwargs):
    """Manually set some parameters of this module"""

    for key, value in kwargs.items():
      if key in self.__dict__:
        setattr(self, key, value)
      else:
        print('{0} does not exist'.format(key))
        pass

  def get(self, **kwargs):
    """Manually get some parameters of this module"""

    for key, value in kwargs.items():
      if key in self.__dict__:
        getattr(self, key, value)
      else:
        print('{0} does not exist'.format(key))
        pass

  def get_options(self):
    """Get all options which can be changed"""

    return self.__dict__

  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding
    im_width = int(self.width - (self.width * 2 * self.padding_x))
    im_height = int(self.height - (self.height * 2 * self.padding_y))
    im_size = im_width, im_height

    logging.info('Image size: {0}'.format(im_size))

    # Create an image for black pixels and one for coloured pixels
    im_black = Image.new('RGB', size = im_size, color = self.background_colour)
    im_colour = Image.new('RGB', size = im_size, color = 'white')

    # Calculate the max number of lines that can fit on the image
    line_spacing = 1
    line_height = int(self.font.getsize('hg')[1]) + line_spacing
    line_width = im_width
    max_lines = im_height // line_height
    logging.debug(('max lines:',max_lines))

    # Create timeline for agenda
    now = arrow.now()
    today = now.floor('day')

    # Create a list of dates for the next days
    agenda_events = [
      {'begin':today.shift(days=+_),
       'title': today.shift(days=+_).format(
         self.date_format,locale=self.language)}
      for _ in range(max_lines)]

    # Load icalendar from config
    parser = icalendar()
    if self.ical_urls:
      parser.load_url(self.ical_urls)
    if self.ical_files:
      parser.load_from_file(self.ical_files)

    # Load events from all icalendar in timerange
    upcoming_events = parser.get_events(today, agenda_events[-1]['begin'])

    # Sort events by beginning time
    parser.sort()
    # parser.show_events()
      
    # Set the width for date, time and event titles
    date_width = int(max([self.font.getsize(
          dates['begin'].format(self.date_format, locale=self.language))[0]
          for dates in agenda_events]) * 1.05)
    logging.debug(('date_width:', date_width))

    # Check if any events were filtered
    if upcoming_events:
      
      # Find out how much space the event times take
      time_width = int(max([self.font.getsize(
          events['begin'].format(self.event_format, locale=self.language))[0]
          for events in upcoming_events]) * 1.05)
      logging.debug(('time_width:', time_width))

      # Calculate x-pos for time
      x_time = date_width
      logging.debug(('x-time:', x_time))

      # Find out how much space is left for event titles
      event_width = im_width - time_width - date_width
      logging.debug(('width for events:', event_width))

      # Calculate x-pos for event titles
      x_event = date_width + time_width
      logging.debug(('x-event:', x_event))

      # Calculate positions for each line
      line_pos = [(0, int(line * line_height)) for line in range(max_lines)]
      logging.debug(('line_pos:', line_pos))

      # Merge list of dates and list of events
      agenda_events += upcoming_events

      # Sort the combined list in chronological order of dates
      by_date = lambda event: event['begin']
      agenda_events.sort(key = by_date)

      # Delete more entries than can be displayed (max lines)
      del agenda_events[max_lines:]

      #print(agenda_events)

      cursor = 0
      for _ in agenda_events:
        title = _['title']

        # Check if item is a date
        if not 'end' in _:
          ImageDraw.Draw(im_colour).line(
            (0, line_pos[cursor][1], im_width, line_pos[cursor][1]),
          fill = 'black')
          
          write(im_black, line_pos[cursor], (date_width, line_height),
              title, font = self.font, alignment='left')

          cursor += 1

        # Check if item is an event
        if 'end' in _:
          time = _['begin'].format(self.event_format)

          # ad-hoc! Don't display event begin time if all day
          # TODO: modifiy ical-parser to somehow tell if event is all day
          # Maybe event.duration = arrow(end-start).days?
          if time != '00:00':
            write(im_black, (x_time, line_pos[cursor][1]),
                (time_width, line_height), time,
                font = self.font, alignment='left')
  
          write(im_black, (x_event, line_pos[cursor][1]),
                (event_width, line_height),
                '• '+title, font = self.font, alignment='left')
          cursor += 1
          
############################################################################
# Exception handling
############################################################################

    else:
      cursor = 0
      for _ in agenda_events:
        title = _['title']
        ImageDraw.Draw(im_colour).line(
            (0, line_pos[cursor][1], im_width, line_pos[cursor][1]),
            fill = 'black')
          
        write(im_black, line_pos[cursor], (date_width, line_height),
              title, font = self.font, alignment='left')

        cursor += 1

      logging.info('no events found')


    # Save image of black and colour channel in image-folder
    im_black.save(images+self.name+'.png')
    im_colour.save(images+self.name+'_colour.png')

if __name__ == '__main__':
  print('running {0} in standalone mode'.format(
    os.path.basename(__file__).split('.py')[0]))

  # remove below line later!
  a = agenda(size, config).generate_image()
