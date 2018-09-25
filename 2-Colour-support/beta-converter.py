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

"""
Info: These path contain the bmps that require converting.
1) /home/pi/E-Paper-Master/Calendar/months/
3) /home/pi/E-Paper-Master/Calendar/other/
"""

path = '/home/pi/E-Paper-Master/Calendar/'
#--------------only change the following two lines-----------------#
input_path_1 =  path+'other/'
output_path_1 = path+'other/'
input_path_2 =  path+'months/'
output_path_2 = path+'months/'
#-----------------no need to change anything below-----------------#

import glob, os, errno
from PIL import Image
import PIL.ImageOps

imagenames_1 = []
imagenames_2 = []

print('opening the specified directory...')

os.chdir(input_path_1) #folder containg files
for files in glob.glob('*.bmp'): #find bmp files
    imagenames_1.append(files) #add these files to a list
print('Found these files:', imagenames_1) #print this list

os.chdir(input_path_2) #folder containg files
for files in glob.glob('*.bmp'): #find bmp files
    imagenames_2.append(files) #add these files to a list
print('Found these files:', imagenames_2) #print this list

# 0 is black, 255 is white, 127 is red.
# The following will convert the 'red' parts to white parts.
thresh = 100 # any value below 127 works.
fn = lambda x : 255 if x > thresh else 0

try:
    print('checking if the first output path exists...')
    os.makedirs(output_path_1)
except OSError as e:
    print('Oh, the first output path exists already. Assuming you know what you are doing.')
    print('Will attempt to overwrite all .bmp files')
    if e.errno != errno.EEXIST:
        raise
        
try:
    print('checking if the second output path exists...')
    os.makedirs(output_path_2)
except OSError as e:
    print('Oh, the second output path exists already. Assuming you know what you are doing.')
    print('Will attempt to overwrite all .bmp files')
    if e.errno != errno.EEXIST:
        raise
        
print('attempting to convert images...')   
for files in imagenames_1:
    ((Image.open(input_path_1+files)).convert('L').point(fn, mode='1').save(output_path_1+files))
for files in imagenames_2:
    ((Image.open(input_path_2+files)).convert('L').point(fn, mode='1').save(output_path_2+files))

print('All done!')
print('The bmp have been converted. Good luck!')
