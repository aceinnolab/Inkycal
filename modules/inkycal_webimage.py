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


def generate_image(): # Name a function. 
  if middle_section == "inkycal_webimage":  # For which section is this module? In this case it's for the bottom section.

    # Do note that your module will only run when 
    try:                                 # Use a try/except statement to prevent crashing on problems
      # clear_image('middle_section')      # Clear/Erase the previous image. This is required

      url = webimage_url.replace('{model}', model).replace('{width}',str(middle_section_width)).replace('{height}',str(middle_section_height))
      myfile = requests.get(url)
      open(image_path+'inkycal_webimage.png', 'wb').write(myfile.content)

      print('inkycal_web_image done') # This will help you track the status of the execution. 

    except Exception as e: # If something goes wrong, what should be done?
      """If something went wrong, print a Error message on the Terminal"""
      print('Failed!')
      print('Error in inkycal_web_image!')
      print('Reason: ',e)
      pass

def main():        # Anything in the main() function will be executed when this module is imported by another one.
  generate_image() # In this case, the function 'generate_image()' wil be executed, which will generate the image

main() # Required
