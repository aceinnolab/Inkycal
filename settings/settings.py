ical_urls = ["https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics"] #iCal URLs
rss_feeds = ["http://feeds.bbci.co.uk/news/world/rss.xml#"] # Use any RSS feed
update_interval = "60"                # "10" # "15" # "20" # "30" # "60"
api_key = ""                          # Your openweathermap API-KEY -> "api-key"
location = "Stuttgart, DE"            # "City name, Country code"
week_starts_on = "Monday"             # 'Sunday' # Monday
calibration_hours = [0,12,18]         # Do not change unlesss you know what you are doing
model = "epd_7_in_5_v2_colour"        # Choose the E-Paper model (see below)
language = "en"                       # "en" # "de" # "fr" # "jp" etc.
units = "metric"                      # "metric" # "imperial"
hours = "24"                          # "24" # "12"
top_section = "inkycal_weather"       # "inkycal_weather"
middle_section = "inkycal_calendar"   # "inkycal_agenda" #"inkycal_calendar"
bottom_section = "inkycal_rss"        # "inkycal_rss" # "inkycal_dadjoke"

"""Adding multiple iCalendar URLs or RSS feed URLs"""
# Single URL:
# ical_urls/rss_feeds = ["url1"]

# Multiple URLs:
# ical_urls/rss_feeds = ["url1", "url2", "url3"]

# URLs should have this sign (") on both side -> "url1"
# If more than one URL is used, separate each one with a comma -> "url1", "url2"

########################
# inkycal_image config:
#
# inkycal_image_path
# The url or file path to obtain the image from.
# The following parameters within accolades ({}) will be substituted:
# - model
# - width
# - height
#
# Samples :
# The inkycal logo:
# inkycal_image_path = 'https://github.com/aceisace/Inky-Calendar/raw/master/Gallery/Inky-Calendar-logo.png'
#
# A dynamic image with a demo-calendar
# inkycal_image_path = 'https://inkycal.robertsirre.nl/panel/test/{model}/image?width={width}&height={height}'
#
# Dynamic image with configurable calendars (see https://inkycal.robertsirre.nl/ and parameter inkycal_image_path_body)
# inkycal_image_path = 'https://inkycal.robertsirre.nl/panel/calendar/{model}?width={width}&height={height}'

inkycal_image_path  ='/home/pi/Inky-Calendar/images/canvas.png'

# Optional: inkycal_image_path_body
# Allows obtaining complexer configure images.
# When inkycal_image_path starts with `http` and inkycal_image_path_body is specified, the image is obtained using POST instead of GET.
# NOTE: structure of the body depends on the web-based image service
# inkycal_image_path_body = [
#   'https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics',
#   'https://www.calendarlabs.com/ical-calendar/ics/101/Netherlands_Holidays.ics'
# ]
########################

"""Supported E-Paper models"""
# epd_7_in_5_v2_colour # 7.5" high-res black-white-red/yellow
# epd_7_in_5_v2        # 7.5" high-res black-white
# epd_7_in_5_colour    # 7.5" black-white-red/yellow
# epd_7_in_5           # 7.5" black-white
# epd_5_in_83_colour   # 5.83" black-white-red/yellow
# epd_5_in_83          # 5.83" black-white
# epd_4_in_2_colour    # 4.2" black-white-red/yellow
# epd_4_in_2           # 4.2" black-white
