/*****************************************************************************
* | File      	:   GUI_BMPfile.h
* | Author      :   Waveshare team
* | Function    :   Hardware underlying interface
* | Info        :
*                Used to shield the underlying layers of each master
*                and enhance portability
*----------------
* |	This version:   V2.0
* | Date        :   2018-11-12
* | Info        :   
* 1.Change file name: GUI_BMP.h -> GUI_BMPfile.h
* 2.fix: GUI_ReadBmp()
*   Now Xstart and Xstart can control the position of the picture normally, 
*   and support the display of images of any size. If it is larger than 
*   the actual display range, it will not be displayed.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
******************************************************************************/
#ifndef __GUI_BMPFILE_H
#define __GUI_BMPFILE_H

#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>

#include "../Config/DEV_Config.h"

extern UBYTE *bmp_dst_buf;
extern UBYTE *bmp_src_buf;

/*Bitmap file header   14bit*/
typedef struct
{
	UWORD bType;        				//File identifier, as for bmp is:0x4D42
	UDOUBLE bSize;      				//The size of the file
	UWORD brgbReversed1;   				//rgbReversed value, must be set to 0
	UWORD brgbReversed2;   				//rgbReversed value, must be set to 0
	UDOUBLE bOffset;   				    //The offset from the beginning of the file header to the beginning of the image data bit
}__attribute__((packed)) BMPFILEHEADER; //Tell the compiler to cancel optimal alignment of the structure during compilation

 
/*Bitmap information header  40bit*/
typedef struct
{
	UDOUBLE biInfoSize;                   //The size of the header: 40
	UDOUBLE biWidth;                      //The width of the image
	UDOUBLE biHeight;	                  //The height of the image
	UWORD biPlanes;		                  //The number of target planes in the image
	UWORD biBitCount;	                  //The number of bits per pixel
	UDOUBLE biCompression;                //Compression type
	UDOUBLE bimpImageSize;                //The size of the image in bytes. The data must be a multiple of 4.
	UDOUBLE biXPelsPerMeter;              //Number of horizontal pixel of the target device per meter
	UDOUBLE biYPelsPerMeter;              //Number of vertical pixel of the target device per meter
	UDOUBLE biClrUsed;                    //Number of colors for bitmap used in color palette
	UDOUBLE biClrImportant;               //Specifies the number of important colors. When the value of this field is equal to the number of colors (or equal to 0), it means that all colors are equally important.
}__attribute__((packed)) BMPINFOHEADER;//Tell the compiler to cancel optimal alignment of the structure during compilation

typedef struct
{
	UBYTE rgbBlue;                  //rgbBlue intensity
	UBYTE rgbGreen;                 //rgbGreen intensity
	UBYTE rgbRed;                   //rgbRed intensity
	UBYTE rgbReversed;              //rgbReversed value
}__attribute__((packed)) BMPRGBQUAD;//Tell the compiler to cancel optimal alignment of the structure during compilation

UBYTE GUI_ReadBmp(const char *path, UWORD x, UWORD y);

#endif
