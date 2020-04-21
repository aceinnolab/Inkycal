#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Third-party (custom) module for Inky-Calendar software.
What it does: displays a random dadjoke from https://icanhazdadjoke.com 
Coded up by: Erik Fredericks
"""
from __future__ import print_function # Required
from configuration import * # Required
import requests

# Any static variables go here. For example, the language.

"""Add a border to increase readability"""
border_top = int(bottom_section_height * 0.05)
border_left = int(bottom_section_width * 0.02)

font = ImageFont.truetype(NotoSans+'.ttf', rss_fontsize)
space_between_lines = 1
line_height = font.getsize('hg')[1] + space_between_lines
line_width = bottom_section_width - (border_left*2)

"""Find out how many lines can fit at max in the bottom section"""
max_lines = (bottom_section_height - (border_top*2)) // (font.getsize('hg')[1]
  + space_between_lines)

"""Calculate the height padding so the lines look centralised"""
y_padding = int( (bottom_section_height % line_height) / 2 )

"""Create a list containing positions of each line"""
line_positions = [(border_left, bottom_section_offset +
  border_top + y_padding + _*line_height ) for _ in range(max_lines)]

url    = "https://icanhazdadjoke.com"
header = {"accept": "text/plain"}

def generate_image(): # Name a function. 
  if bottom_section == "inkycal_dadjoke" and internet_available() == True:
    # Do note that your module will only run when 
    try:                                 # Use a try/except statement to prevent crashing on problems
      clear_image('bottom_section')      # Clear/Erase the previous image. This is required

      # Your code goes here. In this case, 'Hello World! will be printed at the top left corner.'
      #write_text(100, 20, 'Hello there', (0, bottom_section_offset))
      r = requests.get(url, headers=header)
      r.encoding = 'utf-8' # Text coming down wasn't in UTF-8 
      wrapped = text_wrap(r.text, font = font, line_width = line_width)

      for _ in range(len(wrapped)):
        write_text(line_width, line_height, str(wrapped[_]),
          line_positions[_], font = font, alignment= 'left')


      # If you have generated lists or other info which may change, don't forget to delete it
      # For example, if you generated a list named 'list1', use del list1

      custom_image = crop_image(image, 'bottom_section') # Crop the image to the size of the bottom section
      custom_image.save(image_path+'inkycal_dadjoke.png')  # Save the .png image with the same name as the module

      if three_colour_support == True:
        custom_image_col = crop_image(image_col, 'bottom_section')
        custom_image_col.save(image_path+'inkycal_dadjoke_col.png')

      print('Done') # This will help you track the status of the execution. 

    except Exception as e: # If something goes wrong, what should be done?
      """If something went wrong, print a Error message on the Terminal"""
      print('Failed!')
      print('Error in Custom module!')
      print('Reason: ',e)
      pass

def main():        # Anything in the main() function will be executed when this module is imported by another one.
  generate_image() # In this case, the function 'generate_image()' wil be executed, which will generate the image

main() # Required
