"""Logging configuration for Inkycal."""
import logging
import os
from logging.handlers import RotatingFileHandler

from inkycal.settings import Settings

# On the console, set a logger to show only important logs
# (level ERROR or higher)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

settings = Settings()

if not os.path.exists(settings.LOG_PATH):
    os.mkdir(settings.LOG_PATH)


# Save all logs to a file, which contains more detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s |  %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    handlers=[
        stream_handler,  # add stream handler from above
        RotatingFileHandler(  # log to a file too
            settings.INKYCAL_LOG_PATH,  # file to log
            maxBytes=2*1024*1024,  # 2MB max filesize
            backupCount=5  # create max 5 log files
        )
    ]
)

# Show less logging for PIL module
logging.getLogger("PIL").setLevel(logging.WARNING)