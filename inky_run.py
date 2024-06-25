"""Basic Inkycal run script.

Assumes that the settings.json file is in the /boot directory.
set render=True to render the display, set render=False to only run the modules.
"""
import asyncio

from inkycal import Inkycal


async def dry_run():
    # create an instance of Inkycal
    # If your settings.json file is not in /boot, use the full path:
    # inky = Inkycal('path/to/settings.json', render=True)
    inky = Inkycal(render=False)
    await inky.run(run_once=True)  # dry-run without rendering anything on the display


async def clear_display():
    print("loading Inkycal and display driver...")
    inky = Inkycal(render=True)  # Initialise Inkycal
    print("clearing display...")
    inky.calibrate(cycles=1)  # Calibrate the display
    print("clear complete...")
    print("finished!")


async def run():
    # create an instance of Inkycal
    # If your settings.json file is not in /boot, use the full path:
    # inky = Inkycal('path/to/settings.json', render=True)

    # when using experimental PiSugar support:
    # inky = Inkycal(render=True, use_pi_sugar=True)
    inky = Inkycal(render=True)
    await inky.run()  # If there were no issues, you can run Inkycal nonstop


if __name__ == "__main__":
    asyncio.run(run())
