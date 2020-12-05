#ifndef _miniGUI_H_
#define _miniGUI_H_

#include <fcntl.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <linux/fb.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include "IT8951.h" 

typedef struct 
{
  uint16_t X;
  uint16_t Y;
}Point, *pPoint; 

//14byte文件头
typedef struct
{
	uint16_t cfType;//文件类型，"BM"(0x4D42)
	uint32_t cfSize;//文件大小（字节）
	uint32_t cfReserved;//保留，值为0
	uint32_t cfoffBits;//数据区相对于文件头的偏移量（字节）
}__attribute__((packed)) BITMAPFILEHEADER;
//__attribute__((packed))的作用是告诉编译器取消结构在编译过程中的优化对齐
 
//40byte信息头
typedef struct
{
	uint32_t ciSize;//40
	uint32_t ciWidth;//宽度
	uint32_t ciHeight;//高度
	uint16_t ciPlanes;//目标设备的位平面数，值为1
	uint16_t ciBitCount;//每个像素的位数
	uint32_t ciCompress;//压缩说明
	uint32_t ciSizeImage;//用字节表示的图像大小，该数据必须是4的倍数
	uint32_t ciXPelsPerMeter;//目标设备的水平像素数/米
	uint32_t ciYPelsPerMeter;//目标设备的垂直像素数/米
	uint32_t ciClrUsed;//位图使用调色板的颜色数
	uint32_t ciClrImportant;//指定重要的颜色数，当该域的值等于颜色数时（或者等于0时），表示所有颜色都一样重要
}__attribute__((packed)) BITMAPINFOHEADER;

typedef struct
{
	uint8_t blue;
	uint8_t green;
	uint8_t red;
	uint8_t reserved;
}__attribute__((packed)) PIXEL;//颜色模式RGB

#define ABS(X)    ((X) > 0 ? (X) : -(X))     

void EPD_Clear(uint8_t Color);
void EPD_DrawPixel(uint16_t x0,uint16_t y0,uint8_t color);
void EPD_DrawLine(uint16_t x1,uint16_t y1,uint16_t x2,uint16_t y2,uint8_t color);
void EPD_DrawRect(uint16_t Xpos,uint16_t Ypos,uint16_t Width,uint16_t Height,uint8_t color);
void EPD_DrawCircle(uint16_t Xpos,uint16_t Ypos,uint16_t Radius,uint8_t color);
void EPD_DrawPolygon(pPoint Points,uint16_t PointCount,uint8_t color);
void EPD_DrawEllipse(uint16_t Xpos,uint16_t Ypos,uint16_t XRadius,uint16_t YRadius,uint8_t color);
void EPD_FillRect(uint16_t Xpos,uint16_t Ypos,uint16_t Width,uint16_t Height,uint8_t color);
void EPD_FillCircle(uint16_t Xpos,uint16_t Ypos,uint16_t Radius,uint8_t color);
void EPD_PutChar(uint16_t Xpos,uint16_t Ypos,uint8_t ASCI,uint8_t charColor,uint8_t bkColor);
void EPD_Text(uint16_t Xpos,uint16_t Ypos,uint8_t *str,uint8_t Color,uint8_t bkColor);
void EPD_DrawBitmap(uint16_t Xpos, uint16_t Ypos,uint16_t *bmp);
void EPD_DrawMatrix(uint16_t Xpos, uint16_t Ypos,uint16_t Width, uint16_t High,const uint16_t* Matrix);
uint8_t Show_bmp(uint32_t x, uint32_t y,char *path);



#endif
