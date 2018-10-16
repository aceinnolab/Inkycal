"""
Calibration module for the 2-Colour E-Paper Calendar display. Running this script
helps to 'flush' all the pixels and retain the colour on the display.
"""
import epd7in5
from PIL import Image, ImageDraw, ImageFont
EPD_WIDTH = 640
EPD_HEIGHT = 384
epd = epd7in5.EPD()

def calibration():
    for i in range(2):
        epd.init()
        black = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 0)
        print('calibrating black...')
        ImageDraw.Draw(black)
        epd.display_frame(epd.get_frame_buffer(black))
        
        white = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)
        ImageDraw.Draw(white)
        print('calibrating white...')
        epd.display_frame(epd.get_frame_buffer(white))
        epd.sleep()
    print('Cycle complete!')

def main():
    for i in range(1):
        calibration()

if __name__ == '__main__':
    main()
