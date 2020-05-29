from inkycal.modules.inkycal_rss import rss
from inkycal.modules.inkycal_calendar import calendar
from inkycal.modules.inkycal_agenda import agenda

# Test rss module:
rss_size = (384, 160)
rss_config = {'rss_urls': ['http://feeds.bbci.co.uk/news/world/rss.xml#']}
rss = rss(rss_size, rss_config)
rss.generate_image()



# Test calendar module:

calendar_size = (400, 520)
calendar_config = {'week_starts_on': 'Monday', 'ical_urls': ['https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics']}
calendar = calendar(calendar_size, calendar_config)
calendar.generate_image()


# Test agenda module:

agenda_size = (400, 520)
agenda_config = {'week_starts_on': 'Monday', 'ical_urls': ['https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics']}
agenda = agenda(agenda_size, agenda_config)
agenda.generate_image()
