#!/usr/bin/python3
# -*- coding: utf-8 -*-
from settings import display_colours
from PIL import Image, ImageDraw


EPD_WIDTH = 640
EPD_HEIGHT = 384

def calibration():
    if display_colours == "bwr":
        import epd7in5b
        epd = epd7in5b.EPD()
    if display_colours == "bw":
        import epd7in5
        epd = epd7in5.EPD()
    for i in range(2):
        epd.init()
        black = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 'black')
        print('calibrating black...')
        ImageDraw.Draw(black)
        epd.display_frame(epd.get_frame_buffer(black))
        if display_colours == "bwr":
            red = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), 'red')
            ImageDraw.Draw(red)
            print('calibrating red...')
            epd.display_frame(epd.get_frame_buffer(red))
        white = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 'white')
        ImageDraw.Draw(white)
        print('calibrating white...')
        epd.display_frame(epd.get_frame_buffer(white))
        epd.sleep()
    print('Calibration complete')

def main():
    for i in range(1):
        calibration()

if __name__ == '__main__':
    main()
