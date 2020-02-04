#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Third-party (custom) module for Inky-Calendar software.
What it does: obtains an image from a URL. As restriction to this image apply, only use images that have been generated for inkycal.
Copyright by Robert Sirre
"""
from __future__ import print_function # Required
from configuration import * # Required
import requests

# Any static variables go here. For example, the language.
print('Web image module initialized')

def generate_image(): # Name a function. 
  if middle_section == "inkycal_webimage":  # For which section is this module? In this case it's for the bottom section.
    
    print('Generating image')

    # Do note that your module will only run when 
    try:                                 # Use a try/except statement to prevent crashing on problems
      # clear_image('middle_section')      # Clear/Erase the previous image. This is required

      # Your code goes here. In this case, 'Hello World! will be printed at the top left corner.'
      #write_text(100, 20, 'Hello World!', (0, bottom_section_offset))

      url = 'http://inkycal.robertsirre.nl/Panel?token=mydummytoken&panel=epd_7_in_5_v2_colour'

      print('Obtaining url: ' + url )

      myfile = requests.get(url)

      print('File obtained, saving...')

      open(image_path+'inkycal_webimage.png', 'wb').write(myfile.content)

      # If you have generated lists or other info which may change, don't forget to delete it
      # For example, if you generated a list named 'list1', use del list1

      # custom_image = crop_image(image, 'bottom_section') # Crop the image to the size of the bottom section
      # custom_image.save(image_path+'inkycal_web_image.png')  # Save the .png image with the same name as the module
      print('Done') # This will help you track the status of the execution. 

    except Exception as e: # If something goes wrong, what should be done?
      """If something went wrong, print a Error message on the Terminal"""
      print('Failed!')
      print('Error in inkycal_web_image!')
      print('Reason: ',e)
      pass

def main():        # Anything in the main() function will be executed when this module is imported by another one.
  generate_image() # In this case, the function 'generate_image()' wil be executed, which will generate the image

main() # Required
