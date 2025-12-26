from enum import Enum


class InkycalModuleImporter(Enum):
    Agenda = "inkycal.modules.inkycal_agenda.Agenda"
    Calendar = "inkycal.modules.inkycal_calendar.Calendar"
    Feeds = "inkycal.modules.inkycal_feeds.Feeds"
    Inkyimage = "inkycal.modules.inkycal_image.Inkyimage"
    Jokes = "inkycal.modules.inkycal_jokes.Jokes"
    Inkyserver = "inkycal.modules.inkycal_server.Inkyserver"
    Slideshow = "inkycal.modules.inkycal_slideshow.Slideshow"
    Stocks = "inkycal.modules.inkycal_stocks.Stocks"
    TextToDisplay = "inkycal.modules.inkycal_textfile_to_display.TextToDisplay"
    Tindie = "inkycal.modules.inkycal_tindie.Tindie"
    Todoist = "inkycal.modules.inkycal_todoist.Todoist"
    Weather = "inkycal.modules.inkycal_weather.Weather"
    Webshot = "inkycal.modules.inkycal_webshot.Webshot"
    Xkcd = "inkycal.modules.inkycal_xkcd.Xkcd"
