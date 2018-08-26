import epd7in5b
from PIL import Image, ImageDraw, ImageFont, ImageOps
import calendar,  pyowm
from ics import Calendar, Event
from datetime import datetime
from time import sleep
from urllib.request import urlopen 
import arrow

epd = epd7in5b.EPD()
epd.init()

url ="https://calendar.yahoo.com/jmuj6o2qum5wwa7aboeb3qxss5hssod4rlmbev5g/c4a110ace0d020e426cea69a2a873a19/ycal.ics?id=131"
#Enter your ical url above
c = Calendar(urlopen(url).read().decode('iso-8859-1'))
e = Event()
open = Image.open
EPD_WIDTH = 640
EPD_HEIGHT = 384
fpath = '/usr/share/fonts/truetype/Assistant/Assistant-Bold.otf'
fontsmall = ImageFont.truetype(fpath, 20)
fontbig = ImageFont.truetype(fpath, 34)

path = './dev-only/'

background = open(path+'background.bmp')
template =  open(path+'event.bmp')

positions = {
'A1': (517,11), 'A2': (462,11), 'A3': (407,11), 'A4': (352,11), 'A5': (297,11),
'A6': (242,11), 'A7': (187,11), 'A8': (132,11), 'A9': (77,11), 'A10': (22,11),

'B1': (515,71), 'B2': (460, 71), 'B3': (460, 71), 'B4': (460, 71), 'B5': (460, 71),
'B6': (460, 71), 'B7': (460, 71), 'B8': (460, 71), 'B9': (460, 71), 'B10': (460, 71),    

'C1':(542,313), 'C2':(487,313), 'C3':(432,313), 'C4':(377,313), 'C5':(322,313),
'C6':(267,313), 'C7':(212,313), 'C8':(157,313), 'C9':(102,313), 'C10':(47,313) 
}
def main():
    for i in range(1):
        
        time = datetime.now()

        for i in range(1):
            image = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), 255)
            draw = (ImageDraw.Draw(image)).bitmap

            print('Today is:',time.strftime('%a %-d %b %y'))
            print('The time is ', time.strftime('%H:%M'))
    
            edaylist = []
            for events in c.events:
                if str(time.year) in str((events.begin).format('YYYY')):
                    if str(time.month) in str((events.begin).format('M')):
                        edaylist.append((events.begin).format('D'))

            print('In this month, you have',len(edaylist),'Events')
            print(edaylist)

            enamelist = []
            for events in c.events:
                if str(time.year) in str((events.begin).format('YYYY')):
                    if str(time.month) in str((events.begin).format('M')):
                        if str(time.month) in str((events.begin).format('M')):
                            enamelist.append(str(events.name))

            for items in edaylist:
                #date
                txt = (events.begin).format('D')
                w,h = fontbig.getsize(txt)
                space = Image.new('1', (50,50), color=255)
                date = ImageDraw.Draw(space)
                date.text((int((50-w)/2),int((50-h)/2)), txt, fill=0,font=fontbig)
                rotate = space.rotate(270,  expand=1)
                image.paste(rotate, positions['A'+len])#(517,11))
            

            #print(enamelist)

            #for items  in enamelist:
                #draw(positions['A'+events

            etimelist = []
            for events in c.events:
                if str(time.year) in str((events.begin).format('YYYY')):
                    if str(time.month) in str((events.begin).format('M')):
                        etimelist.append(events.begin.format('HH:mm'))
            print(etimelist)

            # name
            txt = enamelist[0]
            w,h = fontsmall.getsize(txt) #works!
            space = Image.new('1', (234,50), color=255)
            name = ImageDraw.Draw(space)
            name.text((int((234-w)/2),int((50-h)/2)), txt, fill=0, font = fontsmall)
            rotate = space.rotate(270,  expand=1)
            image.paste(rotate, (515,71))

            # time
            txt = etimelist[0]
            w,h = fontsmall.getsize(txt)
            space = Image.new('1', (60,25), color=255) #use L and 127 to show 
            date = ImageDraw.Draw(space)
            date.text((int((60-w)/2),int((25-h)/2)), txt,  fill=0 ,font=fontsmall)
            rotate = space.rotate(270,  expand=1)
            image.paste(rotate, (542,313))

            draw((0,0), background)
            draw((515,0), template)

            del edaylist[:]
            del enamelist[:]
            del etimelist[:]
            epd.display_frame(epd.get_frame_buffer(image))

if __name__ == '__main__':
    main()
