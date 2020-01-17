ical_urls = ["https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics"]
rss_feeds = ["http://feeds.bbci.co.uk/news/world/rss.xml#"] # Use any RSS feed


update_interval = "60"         # "15" # "30" # "60"
api_key = ""                   # Your openweathermap API-KEY -> "api-key"
location = "Stuttgart, DE"     # "City name, Country code"
week_starts_on = "Monday"      # "Monday" # "Sunday"
model = "epd_7_in_5_v2_colour" # Choose the E-Paper model (see below)
language = "en"                # "en" # "de" # "fr" # "jp" etc.
units = "metric"               # "metric" # "imperial"
hours = "24"                   # "24" # "12"
top_section = "Weather"        # "Weather"
middle_section = "Calendar"    # "Agenda" #"Calendar"
bottom_section = "RSS"         # "RSS"


"""Adding multiple iCalendar URLs or RSS feed URLs"""
# Single URL:
# ical_urls/rss_feeds = ["url1"]

# Multiple URLs:
# ical_urls/rss_feeds = ["url1", "url2", "url3"]

# URLs should have this sign (") on both side -> "url1"
# If more than one URL is used, separate each one with a comma -> "url1", "url2"

"""Supported E-Paper models"""
# epd_7_in_5_v2_colour # 7.5" high-res black-white-red/yellow
# epd_7_in_5_v2        # 7.5" high-res black-white
# epd_7_in_5_colour    # 7.5" black-white-red/yellow
# epd_7_in_5           # 7.5" black-white
# epd_5_in_83_colour   # 5.83" black-white-red/yellow
# epd_5_in_83          # 5.83" black-white
# epd_4_in_2_colour    # 4.2" black-white-red/yellow
# epd_4_in_2           # 4.2" black-white
