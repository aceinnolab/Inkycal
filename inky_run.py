"""Basic Inkycal run script.

Assumes that the settings.json file is in the /boot directory.
set render=True to render the display, set render=False to only run the modules.
"""
import asyncio
from inkycal import Inkycal

inky = Inkycal(render=True)  # Initialise Inkycal
# If your settings.json file is not in /boot, use the full path: inky = Inkycal('path/to/settings.json', render=True)
inky.run(run_once=True)  # test if Inkycal can be run correctly, running this will show a bit of info for each module
asyncio.run(inky.run())  # If there were no issues, you can run Inkycal nonstop
