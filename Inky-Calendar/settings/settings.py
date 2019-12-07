ical_urls = ["https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics"]
rss_feeds = ["http://feeds.bbci.co.uk/news/world/rss.xml#"] # Use any RSS feed


update_interval = "60"         # "15" # "30" # "60"
api_key = ""                   # Your openweathermap API-KEY -> "api-key"
location = "Stuttgart, DE"     # "City name, Country code"
week_starts_on = "Monday"      # "Monday" # "Sunday"
calibration_hours = [0,12,18]  # Do not change unless required
display_type = "colour"        # "colour" # "black_and_white"
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

