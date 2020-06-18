#include <string.h>
#include "miniGUI.h"
#include "AsciiLib.h"

extern IT8951DevInfo gstI80DevInfo;
extern uint8_t* gpFrameBuf; //Host Source Frame buffer

void EPD_Clear(uint8_t Color)
{
	memset(gpFrameBuf, Color, gstI80DevInfo.usPanelW * gstI80DevInfo.usPanelH);
}

void EPD_DrawPixel(uint16_t x0, uint16_t y0, uint8_t color)
{
	if(x0 < 0 || x0 >= gstI80DevInfo.usPanelW || y0 < 0 || y0 >= gstI80DevInfo.usPanelH)
		return ;	
	
	/*
	显存处理
	*/
	gpFrameBuf[y0*gstI80DevInfo.usPanelW + x0] = color;
}

void EPD_DrawLine(uint16_t x1,uint16_t y1,uint16_t x2,uint16_t y2,uint8_t color)
{
	  uint32_t deltax = 0, deltay = 0, x = 0, y = 0, xinc1 = 0, xinc2 = 0, 
	  yinc1 = 0, yinc2 = 0, den = 0, num = 0, num_add = 0, num_pixels = 0, 
	  curpixel = 0;
	  
	  deltax = ABS(x2 - x1);        /* The difference between the x's */
	  deltay = ABS(y2 - y1);        /* The difference between the y's */
	  x = x1;                       /* Start x off at the first pixel */
	  y = y1;                       /* Start y off at the first pixel */
	  
	  if (x2 >= x1)                 /* The x-values are increasing */
	  {
		    xinc1 = 1;
		    xinc2 = 1;
	  }
	  else                          /* The x-values are decreasing */
	  {
		    xinc1 = -1;
		    xinc2 = -1;
	  }
	  
	  if (y2 >= y1)                 /* The y-values are increasing */
	  {
		    yinc1 = 1;
		    yinc2 = 1;
	  }
	  else                          /* The y-values are decreasing */
	  {
		    yinc1 = -1;
		    yinc2 = -1;
	  }
	  
	  if (deltax >= deltay)         /* There is at least one x-value for every y-value */
	  {
		    xinc1 = 0;              /* Don't change the x when numerator >= denominator */
		    yinc2 = 0;              /* Don't change the y for every iteration */
		    den = deltax;
		    num = deltax / 2;
		    num_add = deltay;
		    num_pixels = deltax;    /* There are more x-values than y-values */
	  }
	  else                          /* There is at least one y-value for every x-value */
	  {
		    xinc2 = 0;              /* Don't change the x for every iteration */
		    yinc1 = 0;              /* Don't change the y when numerator >= denominator */
		    den = deltay;
		    num = deltay / 2;
		    num_add = deltax;
		    num_pixels = deltay;    /* There are more y-values than x-values */
	  }
	  
	  for (curpixel = 0; curpixel <= num_pixels; curpixel++)
	  {
		    EPD_DrawPixel(x, y, color);          /* Draw the current pixel */
		    num += num_add;                      /* Increase the numerator by the top of the fraction */
		    if (num >= den)                      /* Check if numerator >= denominator */
		    {
			      num -= den;                    /* Calculate the new numerator value */
			      x += xinc1;                    /* Change the x as appropriate */
			      y += yinc1;                    /* Change the y as appropriate */
		    }
		    x += xinc2;                          /* Change the x as appropriate */
		    y += yinc2;                          /* Change the y as appropriate */
	  }
}

void EPD_DrawRect(uint16_t Xpos,uint16_t Ypos,uint16_t Width,uint16_t Height,uint8_t color)
{
	EPD_DrawLine(Xpos, Ypos, Xpos+Width, Ypos, color);
	EPD_DrawLine(Xpos, Ypos, Xpos, Ypos+Height, color);
	EPD_DrawLine(Xpos, Ypos+Height, Xpos+Width, Ypos+Height, color);
	EPD_DrawLine(Xpos+Width, Ypos, Xpos+Width, Ypos+Height, color);
}


void EPD_DrawCircle(uint16_t Xpos,uint16_t Ypos,uint16_t Radius,uint8_t color)
{
	  int   decision;    	/* Decision Variable */ 
	  uint32_t  current_x;   	/* Current X Value */
	  uint32_t  current_y;   	/* Current Y Value */
	  
	  decision = 3 - (Radius << 1);
	  current_x = 0;
	  current_y = Radius;
	  
	  while (current_x <= current_y)
	  {
		    EPD_DrawPixel((Xpos + current_x), (Ypos - current_y), color);
		    
		    EPD_DrawPixel((Xpos - current_x), (Ypos - current_y), color);
		    
		    EPD_DrawPixel((Xpos + current_y), (Ypos - current_x), color);
		    
		    EPD_DrawPixel((Xpos - current_y), (Ypos - current_x), color);
		    
		    EPD_DrawPixel((Xpos + current_x), (Ypos + current_y), color);
		    
		    EPD_DrawPixel((Xpos - current_x), (Ypos + current_y), color);
		    
		    EPD_DrawPixel((Xpos + current_y), (Ypos + current_x), color);
		    
		    EPD_DrawPixel((Xpos - current_y), (Ypos + current_x), color);
		    
		    if (decision < 0)
		    { 
				decision += (current_x << 2) + 6;
		    }
		    else
		    {
			      decision += ((current_x - current_y) << 2) + 10;
			      current_y--;
		    }
		    current_x++;
	  } 
}

void EPD_DrawPolygon(pPoint Points,uint16_t PointCount,uint8_t color)
{
  uint16_t x = 0, y = 0;
  
  if(PointCount < 2)
  {
    return;
  }
  
  EPD_DrawLine(Points->X, Points->Y, (Points+PointCount-1)->X, (Points+PointCount-1)->Y,color);
  
  while(--PointCount)
  {
    x = Points->X;
    y = Points->Y;
    Points++;
    EPD_DrawLine(x, y, Points->X, Points->Y,color);
  }
}


void EPD_DrawEllipse(uint16_t Xpos, uint16_t Ypos, uint16_t XRadius, uint16_t YRadius, uint8_t color)
{
  int32_t x = 0, y = -YRadius, err = 2-2*XRadius, e2;
  float k = 0, rad1 = 0, rad2 = 0;
  
  rad1 = XRadius;
  rad2 = YRadius;
  
  k = (float)(rad2/rad1);  
  
  do { 
    EPD_DrawPixel((Xpos-(uint16_t)(x/k)), (Ypos+y), color);
    EPD_DrawPixel((Xpos+(uint16_t)(x/k)), (Ypos+y), color);
    EPD_DrawPixel((Xpos+(uint16_t)(x/k)), (Ypos-y), color);
    EPD_DrawPixel((Xpos-(uint16_t)(x/k)), (Ypos-y), color);      
    
    e2 = err;
    if (e2 <= x) {
      err += ++x*2+1;
      if (-y == x && e2 <= y) e2 = 0;
    }
    if (e2 > y) err += ++y*2+1;     
  }
  while (y <= 0);
}

void EPD_FillRect(uint16_t Xpos,uint16_t Ypos,uint16_t Width,uint16_t Height,uint8_t color)
{
	uint16_t i;
	for (i=0;i<Height;i++)
	{
		EPD_DrawLine(Xpos, Ypos+i,Xpos+Width,Ypos+i,color);
	}
  
}

void EPD_FillCircle(uint16_t Xpos,uint16_t Ypos,uint16_t Radius,uint8_t color)
{
  int32_t  decision;     /* Decision Variable */ 
  uint32_t  current_x;   /* Current X Value */
  uint32_t  current_y;   /* Current Y Value */
  
  decision = 3 - (Radius << 1);
  
  current_x = 0;
  current_y = Radius;

  while (current_x <= current_y)
  {
    if(current_y > 0) 
    {
	EPD_DrawLine(Xpos - current_y, Ypos + current_x,Xpos +current_y,Ypos + current_x,color);
	EPD_DrawLine(Xpos - current_y, Ypos - current_x,Xpos + current_y, Ypos - current_x,color);
    }
    
    if(current_x > 0) 
    {
	EPD_DrawLine(Xpos - current_x, Ypos - current_y,Xpos+current_x,Ypos - current_y,color);
 	EPD_DrawLine(Xpos - current_x, Ypos + current_y,Xpos+current_x,Ypos + current_y,color);
    }
    if (decision < 0)
    { 
      decision += (current_x << 2) + 6;
    }
    else
    {
      decision += ((current_x - current_y) << 2) + 10;
      current_y--;
    }
    current_x++;
  }
  
 	EPD_DrawCircle(Xpos, Ypos, Radius,color);
}

void EPD_PutChar(uint16_t Xpos,uint16_t Ypos,uint8_t ASCI,uint8_t charColor,uint8_t bkColor )
{
	uint16_t i, j;
	uint8_t buffer[16], tmp_char;
	GetASCIICode(buffer,ASCI);
	for(i=0; i<16; i++)
	{
		tmp_char = buffer[i];
		for(j=0; j<8; j++)
		{
			if(((tmp_char >> (7-j)) & 0x01) == 0x01)
			{
				EPD_DrawPixel(Xpos+j, Ypos+i, charColor);
			}
			else
			{
				EPD_DrawPixel(Xpos+j, Ypos+i, bkColor);
			}
		}
	}
}


void EPD_Text(uint16_t Xpos,uint16_t Ypos,uint8_t *str,uint8_t Color,uint8_t bkColor)
{
	uint8_t TempChar;
	do
	{
		TempChar = *str++;  
		EPD_PutChar(Xpos, Ypos, TempChar, Color, bkColor);    
		if(Xpos < gstI80DevInfo.usPanelW - 8)
		{
			Xpos += 8;
		} 
		else if (Ypos < gstI80DevInfo.usPanelH - 16)
		{
			Xpos = 0;
			Ypos += 16;
		}   
	else
	{
		Xpos = 0;
		Ypos = 0;
	}    
    }
    while (*str != 0);
}

extern uint16_t bmp01[];

void EPD_DrawBitmap(uint16_t Xpos, uint16_t Ypos,uint16_t *bmp)
{
	uint16_t i,j;
	uint16_t R,G,B,temp;
	double Gray;

	for (j=0;j<412;j++)
	{
		for (i=0;i<550;i++)
		{
			temp = bmp[j*550+i];
			R = (temp >> 11)<<3;
			G = ((temp&0x07E0) >> 5)<<2;
			B = (temp&0x01F)<<3;
			Gray = (R*299 + G*587 + B*114 + 500) / 1000;
			EPD_DrawPixel(i, j,(uint8_t)Gray);
		}	
	}
}

void EPD_DrawMatrix(uint16_t Xpos, uint16_t Ypos,uint16_t Width, uint16_t High,const uint16_t* Matrix)
{
	uint16_t i,j,x,y;
	uint16_t R,G,B,temp;
	double Gray;
	
	for (y=0,j=Ypos;y<High;y++,j++)
	{
 		for (x=0,i=Xpos;x<Width;x++,i++)
		{
			temp = Matrix[y*550+x];
			R = (temp >> 11)<<3;
			G = ((temp&0x07E0) >> 5)<<2;
			B = (temp&0x001F) <<3;
			Gray = (R*299 + G*587 + B*114 + 500) / 1000;
			EPD_DrawPixel(i, j, Gray);
		}
	}
}

//显示BMP图片相关的全局变量
struct   fb_var_screeninfo vinfo; 	// 记录用户可修改的显示控制器参数
uint32_t fbfd = 0;					// /dev/fb0 文件描述符
uint8_t *fbp = 0;					// 内存映射指针
uint8_t *bmp_dst_buf = NULL;		// BMP Buffer
uint8_t *bmp_src_buf = NULL;		// BMP Buffer
uint32_t bmp_width, bmp_height;
uint8_t  bmp_BitCount;
uint32_t bytesPerLine;
uint32_t imageSize;
uint32_t skip;
PIXEL    palette[256];

static void Bitmap_format_Matrix(uint8_t *dst,uint8_t *src)
{
	uint32_t i,j,k;
    uint8_t *psrc = src;
    uint8_t *pdst = dst;
    uint8_t *p = psrc;
	uint8_t temp;
	uint32_t count;
	
	//由于bmp存储是从后面往前面，所以需要倒序进行转换
	switch(bmp_BitCount)
	{
		case 1:
			pdst += (bmp_width * bmp_height);
			
			for(i=0;i<bmp_height;i++)
			{
				pdst -= bmp_width;
				count = 0;
				for (j=0;j<(bmp_width+7)/8;j++)
				{
					temp = p[j];
					
					for (k=0;k<8;k++)
					{
						pdst[0]= ((temp & (0x80>>k)) >> (7-k));
						count++;
						pdst++;
						if (count == bmp_width)
						{
							break;
						}
					}
				}
				pdst -= bmp_width;
				p += bytesPerLine;
			}
		break;
		case 4:
			pdst += (bmp_width * bmp_height);

			for(i=0;i<bmp_height;i++)
			{
				pdst -= bmp_width;
				count = 0;
				for (j=0;j<(bmp_width+1)/2;j++)
				{
					temp = p[j];
					pdst[0]= ((temp & 0xf0) >> 4);
					count++;
					pdst++;
					if (count == bmp_width)
					{
						break;
					}

					pdst[0] = temp & 0x0f;
					count++;
					pdst++;
					if (count == bmp_width)
					{
						break;
					}
				}
				pdst -= bmp_width;
				p += bytesPerLine;
			}
		break;
		case 8:
			pdst += (bmp_width*bmp_height);
			for(i=0;i<bmp_height;i++)
			{
				p = psrc+(i+1)*bytesPerLine;
				p -= skip;
				for(j=0;j<bmp_width;j++)
				{
					pdst -= 1;
					p -= 1;
					pdst[0] = p[0];
				}
			}
		break;
		case 16:
			pdst += (bmp_width*bmp_height*2);
			for(i=0;i<bmp_height;i++)
			{
				p = psrc+(i+1)*bytesPerLine;
				p -= skip;
				for(j=0;j<bmp_width;j++)
				{
					pdst -= 2;
					p -= 2;
					pdst[0] = p[1];
					pdst[1] = p[0];
				}
			}
		break;
		case 24:
			pdst += (bmp_width*bmp_height*3);
			for(i=0;i<bmp_height;i++)
			{
				p = psrc+(i+1)*bytesPerLine;
				p -= skip;
				for(j=0;j<bmp_width;j++)
				{
					pdst -= 3;
					p -= 3;
					pdst[0] = p[2];
					pdst[1] = p[1];
					pdst[2] = p[0];
				}
			}
		break;
		case 32:
			pdst += (bmp_width*bmp_height*4);
			for(i=0;i<bmp_height;i++)
			{
				p = psrc+(i+1)*bmp_width*4;
				for(j=0;j<bmp_width;j++)
				{
					pdst -= 4;
					p -= 4;
					pdst[0] = p[2];
					pdst[1] = p[1];
					pdst[2] = p[0];
					pdst[3] = p[3];
				}
			}
		break;
		
		default:
		break;
	}	
}

static void DrawMatrix(uint16_t Xpos, uint16_t Ypos,uint16_t Width, uint16_t High,const uint8_t* Matrix)
{
	uint16_t i,j,x,y;
	uint8_t R,G,B;
	uint8_t temp1,temp2;
	double Gray;
	
	for (y=0,j=Ypos;y<High;y++,j++)
	{
 		for (x=0,i=Xpos;x<Width;x++,i++)
		{
			switch(bmp_BitCount)
			{
				case 1:
				case 4:
				case 8:
					R = palette[Matrix[(y*Width+x)]].red;
					G = palette[Matrix[(y*Width+x)]].green;
					B = palette[Matrix[(y*Width+x)]].blue;
				break;
				
				case 16:
					temp1 = Matrix[(y*Width+x)*2];
					temp2 = Matrix[(y*Width+x)*2+1];
					R = (temp1 & 0x7c)<<1;
					G = (((temp1 & 0x03) << 3 ) | ((temp2&0xe0) >> 5))<<3;
					B = (temp2 & 0x1f)<<3;
				break;
				
				case 24:
					R = Matrix[(y*Width+x)*3];
					G = Matrix[(y*Width+x)*3+1];
					B = Matrix[(y*Width+x)*3+2];
				break;
				
				case 32:
					R = Matrix[(y*Width+x)*4];
					G = Matrix[(y*Width+x)*4+1];
					B = Matrix[(y*Width+x)*4+2];
				break;
				
				default:
				break;
			}
		
			Gray = (R*299 + G*587 + B*114 + 500) / 1000;
			EPD_DrawPixel(i, j, Gray);	
		}
	}
}

uint8_t Show_bmp(uint32_t x, uint32_t y,char *path)
{
	FILE *fp;//bmp文件指针
	BITMAPFILEHEADER FileHead;
	BITMAPINFOHEADER InfoHead;
	uint32_t total_length;
	uint8_t *buf = NULL;
	uint32_t ret = -1;
	 
	fp = fopen(path,"rb");
	if (fp == NULL)
	{
		return(-1);
	}
 
	ret = fread(&FileHead, sizeof(BITMAPFILEHEADER),1, fp);
	if (ret != 1)
	{
		printf("Read header error!\n");
		fclose(fp);
		return(-2);
	}

	//检测是否是bmp图像
	if (FileHead.cfType != 0x4D42)//文件类型，"BM"(0x4D42)
	{
		printf("It's not a BMP file\n");
		fclose(fp);
		return(-3);
	}
	
	printf("\n*****************************************\n");
	printf("BMP_cfSize:%d \n", FileHead.cfSize);
 	printf("BMP_cfoffBits:%d \n", FileHead.cfoffBits);
	
	ret = fread((char *)&InfoHead, sizeof(BITMAPINFOHEADER),1, fp);
	if (ret != 1)
	{
		printf("Read infoheader error!\n");
		fclose(fp);
		return(-4);
	}
	
	printf("BMP_ciSize:%d \n", InfoHead.ciSize);
 	printf("BMP_ciWidth:%d \n", InfoHead.ciWidth);
	printf("BMP_ciHeight:%d \n", InfoHead.ciHeight);
	printf("BMP_ciPlanes:%x \n", InfoHead.ciPlanes);
	printf("BMP_ciBitCount:%x \n", InfoHead.ciBitCount);
	printf("BMP_ciCompress:%x \n", InfoHead.ciCompress);
	printf("BMP_ciSizeImage:%x \n", InfoHead.ciSizeImage);
	printf("BMP_ciXPelsPerMeter:%x \n", InfoHead.ciXPelsPerMeter);
	printf("BMP_ciYPelsPerMeter:%x \n", InfoHead.ciYPelsPerMeter);
	printf("BMP_ciClrUsed:%x \n", InfoHead.ciClrUsed);
	printf("BMP_ciClrImportant:%x \n", InfoHead.ciClrImportant);
 	printf("*****************************************\n\n");
	
	total_length = FileHead.cfSize-FileHead.cfoffBits;
	bytesPerLine=((InfoHead.ciWidth*InfoHead.ciBitCount+31)>>5)<<2;
	imageSize=bytesPerLine*InfoHead.ciHeight;
	skip=(4-((InfoHead.ciWidth*InfoHead.ciBitCount)>>3))&3;
	
	printf("total_length:%d,%d\n", InfoHead.ciSizeImage,FileHead.cfSize-FileHead.cfoffBits);
	printf("bytesPerLine = %d\n", bytesPerLine);
	printf("imageSize = %d\n", imageSize);
	printf("skip = %d\n", skip);
	
    bmp_width = InfoHead.ciWidth;
    bmp_height = InfoHead.ciHeight;
	bmp_BitCount = InfoHead.ciBitCount;
	
    bmp_src_buf = (uint8_t*)calloc(1,total_length);
    if(bmp_src_buf == NULL){
        printf("Load > malloc bmp out of memory!\n");
        return -5;
    }
	
	bmp_dst_buf = (uint8_t*)calloc(1,total_length);
    if(bmp_dst_buf == NULL){
        printf("Load > malloc bmp out of memory!\n");
        return -5;
    }

	 //跳转到数据区
    fseek(fp, FileHead.cfoffBits, SEEK_SET);
	
	//每行字节数
    buf = bmp_src_buf;
    while ((ret = fread(buf,1,total_length,fp)) >= 0) 
	{
        if (ret == 0) 
		{
            usleep(100);
            continue;
        }
		buf = ((uint8_t*)buf) + ret;
        total_length = total_length - ret;
        if(total_length == 0)
            break;
    }
	
	//跳转到调试板
	switch(bmp_BitCount)
	{	
		case 1:
			fseek(fp, 54, SEEK_SET);
			ret = fread(palette,1,4*2,fp);
			if (ret != 8) 
			{
				printf("Error: fread != 8\n");
				return -5;
			}
		
			bmp_dst_buf = (uint8_t*)calloc(1,InfoHead.ciWidth * InfoHead.ciHeight);
			if(bmp_dst_buf == NULL)
			{
				printf("Load > malloc bmp out of memory!\n");
				return -5;
			}
		break;
		
		case 4:
			fseek(fp, 54, SEEK_SET);
			ret = fread(palette,1,4*16,fp);
			if (ret != 64) 
			{
				printf("Error: fread != 64\n");
				return -5;
			}
		
			bmp_dst_buf = (uint8_t*)calloc(1,InfoHead.ciWidth * InfoHead.ciHeight);
			if(bmp_dst_buf == NULL)
			{
				printf("Load > malloc bmp out of memory!\n");
				return -5;
			}
		break;
		
		case 8:
			fseek(fp, 54, SEEK_SET);

			ret = fread(palette,1,4*256,fp);

			if (ret != 1024) 
			{
				printf("Error: fread != 1024\n");
				return -5;
			}
		break;
		
		default:
		break;
	}

	Bitmap_format_Matrix(bmp_dst_buf,bmp_src_buf);
	DrawMatrix(x, y,InfoHead.ciWidth, InfoHead.ciHeight, bmp_dst_buf);

	fclose(fp);
	return(0);
}






