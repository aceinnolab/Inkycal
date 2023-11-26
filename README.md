# Inkycal-based full screen weather display (scraper solution)

This fork of <https://github.com/aceinnolab/Inkycal/> was used to try out a webscraper approach for a openweathermap-based full screen weather display on a 7in5 waveshare v2 colour epd.
It didn't prove particularly robust, so I've decided to not further develop it.
I'll leave it here in case someone wants to try and play around with it a little.

Since Selenium doesn't run on Pi Zero, I had to run the scraper part as a cron job on my Pi 4 and scp the resulting image to the Pi Zero that's connected to the e-paper display.

For further information see the official Inkycal repo.
