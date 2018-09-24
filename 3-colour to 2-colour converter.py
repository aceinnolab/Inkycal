"""
This is a python image converter specific for the E-Paper-Calendar
on github by aceisace from the link below.
(https://github.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather)

It will convert the 3-colour .bmp's to 2-colour .bmp's so that they can be
used even with the 2-Colour 7.5" E-Paper Display from waveshare.

Please use with caution. If the input and output paths are the same, the
convertr will overwrite all .bmp files. It's highly recommended to make a
backup of the entire 'Calendar" folder first.

Copyright by Ace-Laboratory
"""

#--------------only change the following two lines-----------------#
input_path =  '/home/pi/E-Paper-Master/Calendar/other/'
output_path = '/home/pi/E-Paper-Master/Calendar/other/'
#-----------------no need to change anything below-----------------#


"""
Info: These path contain the bmps that require converting.
1) /home/pi/E-Paper-Master/Calendar/months/
3) /home/pi/E-Paper-Master/Calendar/other/
"""
import glob, os, errno
from PIL import Image
import PIL.ImageOps

imagenames = []

print('opening the specified directory...')

os.chdir(input_path) #folder containg files
for files in glob.glob('*.bmp'): #find bmp files
    imagenames.append(files) #add these files to a list

print('Found these files:', imagenames) #print this list

# 0 is black, 255 is white, 127 is red.
# The following will convert the 'red' parts to white parts.
thresh = 100 # any value below 127 works.
fn = lambda x : 255 if x > thresh else 0

try:
    print('checking if the output path exists...')
    os.makedirs(output_path)
except OSError as e:
    print('Oh, the output path exists already.')
    print('Will attempt to overwrite all files')
    if e.errno != errno.EEXIST:
        raise

print('attempting to convert images...')   
for files in imagenames:
    ((Image.open(input_path+files)).convert('L').point(fn, mode='1').save(output_path+files))

print('All done!')
print('You can find your converted files in: ',output_path)
