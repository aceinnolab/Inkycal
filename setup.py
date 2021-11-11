from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

__project__ = "inkycal"
__version__ = "2.0.0"
__description__ = "Inkycal is a python3 software for syncing icalendar events, weather and news on selected E-Paper displays"
__packages__ = ["inkycal"]
__author__ = "aceisace"
__author_email__ = "aceisace63@yahoo.com"
__url__ = "https://github.com/aceisace/Inkycal"

__install_requires__ = ['pyowm==3.1.1',                   # weather
                        'Pillow>=7.1.1' ,                 # imaging
                        'icalendar==4.0.6',               # iCalendar parsing
                        'recurring-ical-events==0.1.17b0',# parse recurring events
                        'feedparser==6.0.8',              # RSS-feeds
                        # 'numpy>=1.18.2',                  # image pre-processing -> removed for issues with rpi os
                        'arrow==0.17.0',                  # time handling
                        'Flask==1.1.2',                   # webserver
                        'Flask-WTF==0.14.3',              # webforms
                        'todoist-python==8.1.2',          # todoist api
                        'yfinance>=0.1.62',               # yahoo stocks
                        'matplotlib==3.4.2'               # plotting 
                        ]

__classifiers__ = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Intended Audience :: Education",
    "Natural Language :: English",
    "Programming Language :: Python :: 3 :: Only",
]

                
setup(
    name = __project__,
    version = __version__,
    description = __description__,
    packages = __packages__,
    author = __author__,
    author_email  = __author_email__,
    url = __url__,
    install_requires = __install_requires__,
    classifiers = __classifiers__,
    long_description=long_description,
    long_description_content_type='text/markdown',
)
