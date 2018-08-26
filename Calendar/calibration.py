import epd7in5b
from PIL import Image, ImageDraw, ImageFont

EPD_WIDTH = 640
EPD_HEIGHT = 384

def calibration():
    for i in range(2):
        epd = epd7in5b.EPD()
        epd.init()
        black = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), 0)
        print('calibrating black...')
        ImageDraw.Draw(black)
        epd.display_frame(epd.get_frame_buffer(black))
        #print(epd.get_frame_buffer(black))
        red = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), 127)
        ImageDraw.Draw(red)
        print('calibrating red...')
        epd.display_frame(epd.get_frame_buffer(red))
        white = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), 255)
        ImageDraw.Draw(white)
        print('calibrating white...')
        epd.display_frame(epd.get_frame_buffer(white))

    print('Cycle complete!')

def main():
    epd = epd7in5b.EPD()
    epd.init()

    for i in range(1):
        calibration()

if __name__ == '__main__':
    main()
