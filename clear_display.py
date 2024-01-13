"""
Clears the display of any content.
"""
from inkycal import Inkycal

print("loading Inkycal and display driver...")
inky = Inkycal(render=True)  # Initialise Inkycal
print("clearing display...")
inky.calibrate(cycles=1)  # Calibrate the display
print("clear complete...")

print("finished!")
