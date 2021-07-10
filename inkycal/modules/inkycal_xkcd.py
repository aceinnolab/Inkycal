#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
xkcd Module for Inky-Calendar Project
by https://github.com/worstface
"""
from inkycal.modules.template import inkycal_module
from inkycal.custom import *
from dateutil.parser import *
from dateutil.tz import *
from datetime import *
import os

from inkycal.modules.inky_image import Inkyimage as Images

try:
  import xkcd
except ImportError:
  print('xkcd is not installed! Please install with:')
  print('pip3 install xkcd')

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)

class Xkcd(inkycal_module):

  name = "xkcd - Displays comics from xkcd.com by Randall Munroe"

  # required parameters
  requires = {

    "mode": {
        "label":"Please select the mode",
        "options": ["latest", "random"],
        "default": "latest"      
        },
    "palette": {
        "label":"Which color palette should be used for the comic images?",
        "options": ["bw", "bwr", "bwy"]
        },
    "alt": {
        "label": "Would you like to add the alt text below the comic? If XKCD is not the only module you are showing, I recommend setting this to 'no'",
        "options": ["yes", "no"],
        "default": "no"
        },        
    "filter": {
        "label": "Would you like to add a scaling filter? If the is far too big to be shown in the space you've allotted for it, the module will try to find another image for you. This only applies in random mode. If XKCD is not the only module you are showing, I recommend setting this to 'no'.",
        "options": ["yes", "no"],
        "default": "no"
        }
    }

  def __init__(self, config):

    super().__init__(config)

    config = config['config']
   
    self.mode = config['mode']
    self.palette = config['palette']
    self.alt = config['alt']
    self.scale_filter = config['filter']

    # give an OK message
    print(f'{filename} loaded')
    
  def generate_image(self):
    """Generate image for this module"""   

    # Create tmp path
    tmpPath = '/tmp/inkycal_xkcd/'

    try:
        os.mkdir(tmpPath)
    except OSError:
        print ("Creation of tmp directory %s failed" % path)
    else:
        print ("Successfully created tmp directory %s " % path)

    # Define new image size with respect to padding
    im_width = int(self.width - (2 * self.padding_left))
    im_height = int(self.height - (2 * self.padding_top))
    im_size = im_width, im_height
    logger.info('image size: {} x {} px'.format(im_width, im_height))

    # Create an image for black pixels and one for coloured pixels (required)
    im_black = Image.new('RGB', size = im_size, color = 'white')
    im_colour = Image.new('RGB', size = im_size, color = 'white')

    # Check if internet is available
    if internet_available() == True:
      logger.info('Connection test passed')
    else:
      raise Exception('Network could not be reached :/')

    # Set some parameters for formatting feeds
    line_spacing = 1
    line_height = self.font.getsize('hg')[1] + line_spacing
    line_width = im_width
    max_lines = (im_height // (self.font.getsize('hg')[1] + line_spacing))

    logger.debug(f"max_lines: {max_lines}")

    # Calculate padding from top so the lines look centralised
    spacing_top = int( im_height % line_height / 2 )

    # Calculate line_positions
    line_positions = [(0, spacing_top + _ * line_height ) for _ in range(max_lines)]

    logger.debug(f'line positions: {line_positions}')
      
    logger.info(f'getting xkcd comic...')
    
    if self.mode == 'random':
        if self.scale_filter == 'no':
            xkcdComic = xkcd.getRandomComic()
            xkcdComic.download(output=tmpPath, outputFile='xkcdComic.png')
        else:
            perc = (2.1,0.4)
            url = "test variable, not a real comic"
            while max(perc) > 1.75:
                print("looking for another comic, old comic was: ",perc, url)
                xkcdComic = xkcd.getRandomComic()
                xkcdComic.download(output=tmpPath, outputFile='xkcdComic.png')
                actual_size = Image.open(tmpPath+'/xkcdComic.png').size
                perc = (actual_size[0]/im_width,actual_size[1]/im_height)
                url = xkcdComic.getImageLink()
            print("found one! perc: ",perc, url)
    else:
        xkcdComic = xkcd.getLatestComic()
        xkcdComic.download(output=tmpPath, outputFile='xkcdComic.png')

    logger.info(f'got xkcd comic...')
    title_lines = []
    title_lines.append(xkcdComic.getTitle())
    
    altOffset = int(line_height*1)
    
    if self.alt == "yes":
        alt_text = xkcdComic.getAltText() # get the alt text, too (I break it up into multiple lines later on)
   
        # break up the alt text into lines
        alt_lines = []
        current_line = ""
        for _ in alt_text.split(" "):
            # this breaks up the alt_text into words and creates each line by adding
            # one word at a time until the line is longer than the width of the module
            # then it appends the line to the alt_lines array and starts testing a new line
            if self.font.getsize(current_line + _ + " ")[0] < im_width:
                current_line = current_line + _ + " "
            else:
                alt_lines.append(current_line)
                current_line = _ + " "
        alt_lines.append(current_line) # this adds the last line to the array (or the only line, if the alt text is really short)
        altHeight = int(line_height*len(alt_lines)) + altOffset
    else:
        altHeight = 0 # this is added so that I don't need to add more "if alt is yes" conditionals when centering below. Now the centering code will work regardless of whether they want alttext or not
      
    comicSpaceBlack = Image.new('RGBA', (im_width, im_height), (255,255,255,255))  
    comicSpaceColour = Image.new('RGBA', (im_width, im_height), (255,255,255,255)) 
      
    im = Images()
    im.load(tmpPath+'xkcdComic.png')
    im.remove_alpha()
    
    imageAspectRatio = im_width / im_height
    comicAspectRatio = im.image.width / im.image.height
        
    if comicAspectRatio > imageAspectRatio:
        imageScale = im_width / im.image.width
    else:
        imageScale = im_height / im.image.height        
        
    comicHeight = int(im.image.height * imageScale)      
    
    headerHeight = int(line_height*3/2)    
    
    if comicHeight + (headerHeight+altHeight) > im_height:
        comicHeight -= (headerHeight+altHeight)
    
    im.resize( width=int(im.image.width * imageScale), height= comicHeight)        
    
    im_comic_black, im_comic_colour = im.to_palette(self.palette)  

    headerCenterPosY = int((im_height/2)-((im.image.height+headerHeight+altHeight)/2))
    comicCenterPosY = int((im_height/2)-((im.image.height+headerHeight+altHeight)/2)+headerHeight)
    altCenterPosY = int((im_height/2)-((im.image.height+headerHeight+altHeight)/2)+headerHeight+im.image.height)
    
    centerPosX = int((im_width/2)-(im.image.width/2))
    
    comicSpaceBlack.paste(im_comic_black, (centerPosX, comicCenterPosY))
    im_black.paste(comicSpaceBlack)
    
    comicSpaceColour.paste(im_comic_colour, (centerPosX, comicCenterPosY))
    im_colour.paste(comicSpaceColour)
    
    im.clear()
    logger.info(f'added comic image')    
   
    # Write the title on the black image 
    write(im_black, (0, headerCenterPosY), (line_width, line_height),
              title_lines[0], font = self.font, alignment= 'center')    
    
    if self.alt == "yes":
        # write alt_text
        for _ in range(len(alt_lines)):
          write(im_black, (0, altCenterPosY+_*line_height + altOffset), (line_width, line_height),
                    alt_lines[_], font = self.font, alignment='left')

    # Save image of black and colour channel in image-folder
    return im_black, im_colour  

if __name__ == '__main__':
  print(f'running {filename} in standalone/debug mode')
