#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Calibration module for the Black-White and Black-White-Red E-Paper display
Calibration refers to flushing all pixels in a single colour to prevent
ghosting.
"""

from __future__ import print_function
import time
from settings import display_colours
from icon_positions_locations import black, white, red

def calibration():
    """Function for Calibration"""
    import e_paper_drivers
    epd = e_paper_drivers.EPD()
    print('_________Calibration for E-Paper started_________'+'\n')

    for i in range(2):
        epd.init()
        print('Calibrating black...')
        epd.display_frame(epd.get_frame_buffer(black))
        if display_colours == "bwr":
            print('calibrating red...')
            epd.display_frame(epd.get_frame_buffer(red))
        print('Calibrating white...')
        epd.display_frame(epd.get_frame_buffer(white))
        epd.sleep()
        print('Cycle', str(i+1)+'/2', 'complete'+'\n')
        print('Calibration complete')

def main():
    """Added timer"""
    start = time.time()
    calibration()
    end = time.time()
    print('Calibration complete in', int(end - start), 'seconds')

if __name__ == '__main__':
    main()
