# Converting ttf fonts to the pil format
See https://llbb.wordpress.com/2006/11/24/making-pil-font-for-python-image-library/
```sh
sudo apt-get install otf2bdf
wget https://raw.githubusercontent.com/python-pillow/pillow-scripts/master/Scripts/pilfont.py
otf2bdf -p 16 arial.ttf > arial-pil.bdf
python pilfont.py arial-pil.bdf
```

Then in Inkycal use the new `-pil` font instead of the normal one.
The global `fonts` object in inkycal uses the font name without the file extension as key.
