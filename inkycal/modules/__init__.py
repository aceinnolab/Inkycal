from enum import Enum


class InkycalModuleImporter(Enum):
    Agenda = "from inkycal.modules.inkycal_agenda import Agenda"
    Calendar = "from inkycal.modules.inkycal_calendar import Calendar"
    Feeds = "from inkycal.modules.inkycal_feeds import Feeds"
    Inkyimage = "from inkycal.modules.inky_image import Inkyimage"
    Jokes = "from inkycal.modules.inkycal_jokes import Jokes"
    Inkyserver = "from inkycal.modules.inkycal_server import Inkyserver"
    Slideshow = "from inkycal.modules.inkycal_slideshow import Slideshow"
    Stocks = "from inkycal.modules.inkycal_stocks import Stocks"
    TextToDisplay = "from inkycal.modules.inkycal_textfile_to_display import TextToDisplay"
    Tindie = "from inkycal.modules.inkycal_tindie import Tindie"
    Todoist = "from inkycal.modules.inkycal_todoist import Todoist"
    Weather = "from inkycal.modules.inkycal_weather import Weather"
    Webshot = "from inkycal.modules.inkycal_webshot import Webshot"
    Xkcd = "from inkycal.modules.inkycal_xkcd import Xkcd"
