from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

# remove descriptions of packages
required = [i.split(' ')[0] for i in required]

__project__ = "inkycal"
__version__ = "2.0.4"
__description__ = "Inkycal is a python3 software for syncing icalendar events, weather and news on selected E-Paper displays"
__packages__ = ["inkycal"]
__author__ = "aceinnolab"
__author_email__ = "aceisace63@yahoo.com"
__url__ = "https://github.com/aceinnolab/Inkycal"

__install_requires__ = required

__classifiers__ = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Intended Audience :: Education",
    "Natural Language :: English",
    "Programming Language :: Python :: 3 :: Only",
]

setup(
    name=__project__,
    version=__version__,
    description=__description__,
    packages=__packages__,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    install_requires=__install_requires__,
    classifiers=__classifiers__,
    long_description=long_description,
    long_description_content_type='text/markdown',
)
