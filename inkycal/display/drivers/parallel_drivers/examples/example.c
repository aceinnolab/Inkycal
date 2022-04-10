#include "example.h"

#include <time.h> 
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>

#include "../lib/e-Paper/EPD_IT8951.h"
#include "../lib/GUI/GUI_Paint.h"
#include "../lib/GUI/GUI_BMPfile.h"
#include "../lib/Config/Debug.h"

UBYTE *Refresh_Frame_Buf = NULL;

UBYTE *Panel_Frame_Buf = NULL;
UBYTE *Panel_Area_Frame_Buf = NULL;

bool Four_Byte_Align = false;

extern int epd_mode;
extern UWORD VCOM;
extern UBYTE isColor;
/******************************************************************************
function: Change direction of display, Called after Paint_NewImage()
parameter:
    mode: display mode
******************************************************************************/
static void Epd_Mode(int mode)
{
	if(mode == 3) {
		Paint_SetRotate(ROTATE_0);
		Paint_SetMirroring(MIRROR_NONE);
		isColor = 1;
	}else if(mode == 2) {
		Paint_SetRotate(ROTATE_0);
		Paint_SetMirroring(MIRROR_HORIZONTAL);
	}else if(mode == 1) {
		Paint_SetRotate(ROTATE_0);
		Paint_SetMirroring(MIRROR_HORIZONTAL);
	}else {
		Paint_SetRotate(ROTATE_0);
		Paint_SetMirroring(MIRROR_NONE);
	}
}


/******************************************************************************
function: Display_ColorPalette_Example
parameter:
    Panel_Width: Width of the panel
    Panel_Height: Height of the panel
    Init_Target_Memory_Addr: Memory address of IT8951 target memory address
******************************************************************************/
UBYTE Display_ColorPalette_Example(UWORD Panel_Width, UWORD Panel_Height, UDOUBLE Init_Target_Memory_Addr){
    UWORD In_4bp_Refresh_Area_Width;
    if(Four_Byte_Align == true){
        In_4bp_Refresh_Area_Width = Panel_Width - (Panel_Width % 32);
    }else{
        In_4bp_Refresh_Area_Width = Panel_Width;
    }
    UWORD In_4bp_Refresh_Area_Height = Panel_Height/16;

    UDOUBLE Imagesize;

    clock_t In_4bp_Refresh_Start, In_4bp_Refresh_Finish;
    double In_4bp_Refresh_Duration;

    Imagesize  = ((In_4bp_Refresh_Area_Width*4 % 8 == 0)? (In_4bp_Refresh_Area_Width*4 / 8 ): (In_4bp_Refresh_Area_Width*4 / 8 + 1)) * In_4bp_Refresh_Area_Height;

    if((Refresh_Frame_Buf = (UBYTE *)malloc(Imagesize)) == NULL) {
        Debug("Failed to apply for black memory...\r\n");
        return -1;
    }

    Debug("Start to demostrate 4bpp palette example\r\n");
    In_4bp_Refresh_Start = clock();

    UBYTE SixteenColorPattern[16] = {0xFF,0xEE,0xDD,0xCC,0xBB,0xAA,0x99,0x88,0x77,0x66,0x55,0x44,0x33,0x22,0x11,0x00};

    for(int i=0; i < 16; i++){
        memset(Refresh_Frame_Buf, SixteenColorPattern[i], Imagesize);
        EPD_IT8951_4bp_Refresh(Refresh_Frame_Buf, 0, i * In_4bp_Refresh_Area_Height, In_4bp_Refresh_Area_Width, In_4bp_Refresh_Area_Height, false, Init_Target_Memory_Addr, false);
    }

    In_4bp_Refresh_Finish = clock();
    In_4bp_Refresh_Duration = (double)(In_4bp_Refresh_Finish - In_4bp_Refresh_Start) / CLOCKS_PER_SEC;
    Debug( "Write and Show 4bp occupy %f second\n", In_4bp_Refresh_Duration );

    if(Refresh_Frame_Buf != NULL){
        free(Refresh_Frame_Buf);
        Refresh_Frame_Buf = NULL;
    }
    return 0;
}


/******************************************************************************
function: Display_CharacterPattern_Example
parameter:
    Panel_Width: Width of the panel
    Panel_Height: Height of the panel
    Init_Target_Memory_Addr: Memory address of IT8951 target memory address
    BitsPerPixel: Bits Per Pixel, 2^BitsPerPixel = grayscale
******************************************************************************/
UBYTE Display_CharacterPattern_Example(UWORD Panel_Width, UWORD Panel_Height, UDOUBLE Init_Target_Memory_Addr, UBYTE BitsPerPixel){
    UWORD Display_Area_Width;
    if(Four_Byte_Align == true){
        Display_Area_Width = Panel_Width - (Panel_Width % 32);
    }else{
        Display_Area_Width = Panel_Width;
    }
    UWORD Display_Area_Height = Panel_Height;

    UWORD Display_Area_Sub_Width = Display_Area_Width / 5;
    UWORD Display_Area_Sub_Height = Display_Area_Height / 5;

    UDOUBLE Imagesize;

    Imagesize = ((Display_Area_Width * BitsPerPixel % 8 == 0)? (Display_Area_Width * BitsPerPixel / 8 ): (Display_Area_Width * BitsPerPixel / 8 + 1)) * Display_Area_Height;
    if((Refresh_Frame_Buf = (UBYTE *)malloc(Imagesize)) == NULL) {
        Debug("Failed to apply for image memory...\r\n");
        return -1;
    }

    Paint_NewImage(Refresh_Frame_Buf, Display_Area_Width, Display_Area_Height, 0, BLACK);
    Paint_SelectImage(Refresh_Frame_Buf);
	Epd_Mode(epd_mode);
    Paint_SetBitsPerPixel(BitsPerPixel);
    Paint_Clear(WHITE);
    

    for(int y=20; y<Display_Area_Height - Display_Area_Sub_Height; y += Display_Area_Sub_Height )//To prevent arrays from going out of bounds
    {
        for(int  x=20; x<Display_Area_Width - Display_Area_Sub_Width; x += Display_Area_Sub_Width )//To prevent arrays from going out of bounds
        {
            //For color definition of all BitsPerPixel, you can refer to GUI_Paint.h
            Paint_DrawPoint(x+Display_Area_Sub_Width*3/8, y+Display_Area_Sub_Height*3/8, 0x10, DOT_PIXEL_7X7, DOT_STYLE_DFT);
            Paint_DrawPoint(x+Display_Area_Sub_Width*5/8, y+Display_Area_Sub_Height*3/8, 0x30, DOT_PIXEL_7X7, DOT_STYLE_DFT);
            Paint_DrawLine(x+Display_Area_Sub_Width*3/8, y+Display_Area_Sub_Height*5/8, x+Display_Area_Sub_Width*5/8, y+Display_Area_Sub_Height*5/8, 0x50, DOT_PIXEL_3X3, LINE_STYLE_SOLID);
            Paint_DrawRectangle(x, y, x+Display_Area_Sub_Width, y+Display_Area_Sub_Height, 0x00, DOT_PIXEL_3X3, DRAW_FILL_EMPTY);
            Paint_DrawCircle(x + Display_Area_Sub_Width/2, y + Display_Area_Sub_Height/2, Display_Area_Sub_Height/2, 0x50, DOT_PIXEL_2X2, DRAW_FILL_EMPTY);
            Paint_DrawNum(x+Display_Area_Sub_Width*3/10, y+Display_Area_Sub_Height*1/4, 1234567890, &Font16, 0x20, 0xE0);
            Paint_DrawString_EN(x+Display_Area_Sub_Width*3/10, y+Display_Area_Sub_Height*3/4, "hello world", &Font16, 0x30, 0xD0);
        }
    }


    switch(BitsPerPixel){
        case BitsPerPixel_8:{
            EPD_IT8951_8bp_Refresh(Refresh_Frame_Buf, 0, 0, Display_Area_Width,  Display_Area_Height, false, Init_Target_Memory_Addr);
            break;
        }
        case BitsPerPixel_4:{
            EPD_IT8951_4bp_Refresh(Refresh_Frame_Buf, 0, 0, Display_Area_Width,  Display_Area_Height, false, Init_Target_Memory_Addr,false);
            break;
        }
        case BitsPerPixel_2:{
            EPD_IT8951_2bp_Refresh(Refresh_Frame_Buf, 0, 0, Display_Area_Width,  Display_Area_Height, false, Init_Target_Memory_Addr,false);
            break;
        }
        case BitsPerPixel_1:{
            EPD_IT8951_1bp_Refresh(Refresh_Frame_Buf, 0, 0, Display_Area_Width,  Display_Area_Height, A2_Mode, Init_Target_Memory_Addr,false);
            break;
        }
    }

    if(Refresh_Frame_Buf != NULL){
        free(Refresh_Frame_Buf);
        Refresh_Frame_Buf = NULL;
    }

    return 0;
}



/******************************************************************************
function: Display_BMP_Example
parameter:
    Panel_Width: Width of the panel
    Panel_Height: Height of the panel
    Init_Target_Memory_Addr: Memory address of IT8951 target memory address
    BitsPerPixel: Bits Per Pixel, 2^BitsPerPixel = grayscale
******************************************************************************/
UBYTE Display_BMP_Example(UWORD Panel_Width, UWORD Panel_Height, UDOUBLE Init_Target_Memory_Addr, UBYTE BitsPerPixel, char *Path){
    UWORD WIDTH;
    if(Four_Byte_Align == true){
        WIDTH  = Panel_Width - (Panel_Width % 32);
    }else{
        WIDTH = Panel_Width;
    }
    UWORD HEIGHT = Panel_Height;

    UDOUBLE Imagesize;

    Imagesize = ((WIDTH * BitsPerPixel % 8 == 0)? (WIDTH * BitsPerPixel / 8 ): (WIDTH * BitsPerPixel / 8 + 1)) * HEIGHT;
    if((Refresh_Frame_Buf = (UBYTE *)malloc(Imagesize)) == NULL) {
        Debug("Failed to apply for black memory...\r\n");
        return -1;
    }

    Paint_NewImage(Refresh_Frame_Buf, WIDTH, HEIGHT, 0, BLACK);
    Paint_SelectImage(Refresh_Frame_Buf);
	Epd_Mode(epd_mode);
    Paint_SetBitsPerPixel(BitsPerPixel);
    Paint_Clear(WHITE);

    // sprintf(Path,"./pic/%dx%d_0.bmp", WIDTH, HEIGHT);

    GUI_ReadBmp(Path, 0, 0);

    //you can draw your character and pattern on the image, for color definition of all BitsPerPixel, you can refer to GUI_Paint.h, 
    //Paint_DrawRectangle(50, 50, WIDTH/2, HEIGHT/2, 0x30, DOT_PIXEL_3X3, DRAW_FILL_EMPTY);
    //Paint_DrawCircle(WIDTH*3/4, HEIGHT/4, 100, 0xF0, DOT_PIXEL_2X2, DRAW_FILL_EMPTY);
    //Paint_DrawNum(WIDTH/4, HEIGHT/5, 709, &Font20, 0x30, 0xB0);

    switch(BitsPerPixel){
        case BitsPerPixel_8:{
            Paint_DrawString_EN(10, 10, "8 bits per pixel 16 grayscale", &Font24, 0xF0, 0x00);
            EPD_IT8951_8bp_Refresh(Refresh_Frame_Buf, 0, 0, WIDTH,  HEIGHT, false, Init_Target_Memory_Addr);
            break;
        }
        case BitsPerPixel_4:{
            //Paint_DrawString_EN(10, 10, "4 bits per pixel 16 grayscale", &Font24, 0xF0, 0x00);
            EPD_IT8951_4bp_Refresh(Refresh_Frame_Buf, 0, 0, WIDTH,  HEIGHT, false, Init_Target_Memory_Addr,false);
            break;
        }
        case BitsPerPixel_2:{
            Paint_DrawString_EN(10, 10, "2 bits per pixel 4 grayscale", &Font24, 0xC0, 0x00);
            EPD_IT8951_2bp_Refresh(Refresh_Frame_Buf, 0, 0, WIDTH,  HEIGHT, false, Init_Target_Memory_Addr,false);
            break;
        }
        case BitsPerPixel_1:{
            Paint_DrawString_EN(10, 10, "1 bit per pixel 2 grayscale", &Font24, 0x80, 0x00);
            EPD_IT8951_1bp_Refresh(Refresh_Frame_Buf, 0, 0, WIDTH,  HEIGHT, A2_Mode, Init_Target_Memory_Addr,false);
            break;
        }
    }

    if(Refresh_Frame_Buf != NULL){
        free(Refresh_Frame_Buf);
        Refresh_Frame_Buf = NULL;
    }

    DEV_Delay_ms(5000);

    return 0;
}


/******************************************************************************
function: Dynamic_Refresh_Example
parameter:
    Dev_Info: Information structure read from IT8951
    Init_Target_Memory_Addr: Memory address of IT8951 target memory address
******************************************************************************/
UBYTE Dynamic_Refresh_Example(IT8951_Dev_Info Dev_Info, UDOUBLE Init_Target_Memory_Addr){
    UWORD Panel_Width = Dev_Info.Panel_W;
    UWORD Panel_Height = Dev_Info.Panel_H;

    UWORD Dynamic_Area_Width = 96;
    UWORD Dynamic_Area_Height = 48;

    UDOUBLE Imagesize;

    UWORD Start_X = 0,Start_Y = 0;

    UWORD Dynamic_Area_Count = 0;

    UWORD Repeat_Area_Times = 0;

    //malloc enough memory for 1bp picture first
    Imagesize = ((Panel_Width * 1 % 8 == 0)? (Panel_Width * 1 / 8 ): (Panel_Width * 1 / 8 + 1)) * Panel_Height;
    if((Refresh_Frame_Buf = (UBYTE *)malloc(Imagesize)) == NULL){
        Debug("Failed to apply for picture memory...\r\n");
        return -1;
    }

    clock_t Dynamic_Area_Start, Dynamic_Area_Finish;
    double Dynamic_Area_Duration;  

    while(1)
    {
        Dynamic_Area_Width = 128;
        Dynamic_Area_Height = 96;

        Start_X = 0;
        Start_Y = 0;

        Dynamic_Area_Count = 0;

        Dynamic_Area_Start = clock();
        Debug("Start to dynamic display...\r\n");

        for(Dynamic_Area_Width = 96, Dynamic_Area_Height = 64; (Dynamic_Area_Width < Panel_Width - 32) && (Dynamic_Area_Height < Panel_Height - 24); Dynamic_Area_Width += 32, Dynamic_Area_Height += 24)
        {

            Imagesize = ((Dynamic_Area_Width % 8 == 0)? (Dynamic_Area_Width / 8 ): (Dynamic_Area_Width / 8 + 1)) * Dynamic_Area_Height;
            Paint_NewImage(Refresh_Frame_Buf, Dynamic_Area_Width, Dynamic_Area_Height, 0, BLACK);
            Paint_SelectImage(Refresh_Frame_Buf);
			Epd_Mode(epd_mode);
            Paint_SetBitsPerPixel(1);

           for(int y=Start_Y; y< Panel_Height - Dynamic_Area_Height; y += Dynamic_Area_Height)
            {
                for(int x=Start_X; x< Panel_Width - Dynamic_Area_Width; x += Dynamic_Area_Width)
                {
                    Paint_Clear(WHITE);

                    //For color definition of all BitsPerPixel, you can refer to GUI_Paint.h
                    Paint_DrawRectangle(0, 0, Dynamic_Area_Width-1, Dynamic_Area_Height, 0x00, DOT_PIXEL_2X2, DRAW_FILL_EMPTY);

                    Paint_DrawCircle(Dynamic_Area_Width*3/4, Dynamic_Area_Height*3/4, 5, 0x00, DOT_PIXEL_1X1, DRAW_FILL_FULL);

                    Paint_DrawNum(Dynamic_Area_Width/4, Dynamic_Area_Height/4, ++Dynamic_Area_Count, &Font20, 0x00, 0xF0);

					if(epd_mode == 2)
						EPD_IT8951_1bp_Refresh(Refresh_Frame_Buf, 1280-Dynamic_Area_Width-x, y, Dynamic_Area_Width,  Dynamic_Area_Height, A2_Mode, Init_Target_Memory_Addr, true);
					else if(epd_mode == 1)
						EPD_IT8951_1bp_Refresh(Refresh_Frame_Buf, Panel_Width-Dynamic_Area_Width-x-16, y, Dynamic_Area_Width,  Dynamic_Area_Height, A2_Mode, Init_Target_Memory_Addr, true);
                    else
						EPD_IT8951_1bp_Refresh(Refresh_Frame_Buf, x, y, Dynamic_Area_Width,  Dynamic_Area_Height, A2_Mode, Init_Target_Memory_Addr, true);
                }
            }
            Start_X += 32;
            Start_Y += 24;
        }

        Dynamic_Area_Finish = clock();
        Dynamic_Area_Duration = (double)(Dynamic_Area_Finish - Dynamic_Area_Start) / CLOCKS_PER_SEC;
        Debug( "Write and Show occupy %f second\n", Dynamic_Area_Duration );

        Repeat_Area_Times ++;
        if(Repeat_Area_Times > 0){
            break;
        }
    }
    if(Refresh_Frame_Buf != NULL){
        free(Refresh_Frame_Buf);
        Refresh_Frame_Buf = NULL;
    }

    return 0;
}


/******************************************************************************
function: Dynamic_GIF_Example
parameter:
    Panel_Width: Width of the panel
    Panel_Height: Height of the panel
    Init_Target_Memory_Addr: Memory address of IT8951 target memory address
    BitsPerPixel: Bits Per Pixel, 2^BitsPerPixel = grayscale
******************************************************************************/
UBYTE Dynamic_GIF_Example(UWORD Panel_Width, UWORD Panel_Height, UDOUBLE Init_Target_Memory_Addr){

    UWORD Animation_Start_X = 0;
    UWORD Animation_Start_Y = 0;
    UWORD Animation_Area_Width = 800;
    UWORD Animation_Area_Height = 600;

    if(Animation_Area_Width > Panel_Width){
        return -1;
    }
    if(Animation_Area_Height > Panel_Height){
        return -1;
    }

    UDOUBLE Imagesize;

    UBYTE Pic_Count = 0;
    UBYTE Pic_Num = 7;
    char Path[30];

    UDOUBLE Basical_Memory_Addr = Init_Target_Memory_Addr;

    UDOUBLE Target_Memory_Addr = Basical_Memory_Addr;
    UWORD Repeat_Animation_Times = 0;

    clock_t Animation_Test_Start, Animation_Test_Finish;
    double Animation_Test_Duration;

    Imagesize = ((Animation_Area_Width * 1 % 8 == 0)? (Animation_Area_Width * 1 / 8 ): (Animation_Area_Width * 1 / 8 + 1)) * Animation_Area_Height;

    if((Refresh_Frame_Buf = (UBYTE *)malloc(Imagesize)) == NULL){
        Debug("Failed to apply for image memory...\r\n");
        return -1;
    }

    Paint_NewImage(Refresh_Frame_Buf, Animation_Area_Width, Animation_Area_Height, 0, BLACK);
    Paint_SelectImage(Refresh_Frame_Buf);
	Epd_Mode(epd_mode);
    Paint_SetBitsPerPixel(1);

    Debug("Start to write a animation\r\n");
    Animation_Test_Start = clock();
    for(int i=0; i < Pic_Num; i += 1){
        Paint_Clear(WHITE);
        sprintf(Path,"./pic/800x600_gif_%d.bmp",Pic_Count++);
        GUI_ReadBmp(Path, 0, 0);
        //For color definition of all BitsPerPixel, you can refer to GUI_Paint.h
        Paint_DrawNum(10, 10, i+1, &Font16, 0x00, 0xF0);
		if(epd_mode == 2)
			EPD_IT8951_1bp_Multi_Frame_Write(Refresh_Frame_Buf, 1280-Animation_Area_Width+Animation_Start_X, Animation_Start_Y, Animation_Area_Width,  Animation_Area_Height, Target_Memory_Addr,false);
        else if(epd_mode == 1)
			EPD_IT8951_1bp_Multi_Frame_Write(Refresh_Frame_Buf, Panel_Width-Animation_Area_Width+Animation_Start_X-16, Animation_Start_Y, Animation_Area_Width,  Animation_Area_Height, Target_Memory_Addr,false);
		else
			EPD_IT8951_1bp_Multi_Frame_Write(Refresh_Frame_Buf, Animation_Start_X, Animation_Start_Y, Animation_Area_Width,  Animation_Area_Height, Target_Memory_Addr,false);
        Target_Memory_Addr += Imagesize;
    }

    Animation_Test_Finish = clock();
    Animation_Test_Duration = (double)(Animation_Test_Finish - Animation_Test_Start) / CLOCKS_PER_SEC;
	Debug( "Write all frame occupy %f second\r\n", Animation_Test_Duration);

    Target_Memory_Addr = Basical_Memory_Addr;

    while(1){
        Debug("Start to show a animation\r\n");
        Animation_Test_Start = clock();

        for(int i=0; i< Pic_Num; i += 1){
			if(epd_mode == 2)
				EPD_IT8951_1bp_Multi_Frame_Refresh(Panel_Width-Animation_Area_Width+Animation_Start_X, Animation_Start_Y, Animation_Area_Width,  Animation_Area_Height, Target_Memory_Addr);
			else if(epd_mode == 1)
				EPD_IT8951_1bp_Multi_Frame_Refresh(Panel_Width-Animation_Area_Width+Animation_Start_X-16, Animation_Start_Y, Animation_Area_Width,  Animation_Area_Height, Target_Memory_Addr);
            else
				EPD_IT8951_1bp_Multi_Frame_Refresh(Animation_Start_X, Animation_Start_Y, Animation_Area_Width,  Animation_Area_Height, Target_Memory_Addr);
            Target_Memory_Addr += Imagesize;
        }
        Target_Memory_Addr = Basical_Memory_Addr;

        Animation_Test_Finish = clock();
        Animation_Test_Duration = (double)(Animation_Test_Finish - Animation_Test_Start) / CLOCKS_PER_SEC;
        Debug( "Show all frame occupy %f second\r\n", Animation_Test_Duration );

        Repeat_Animation_Times ++;
        if(Repeat_Animation_Times >15){
            break;
        }
    }

    if(Refresh_Frame_Buf != NULL){
        free(Refresh_Frame_Buf);
        Refresh_Frame_Buf = NULL;
    }

    return 0;
}



/******************************************************************************
function: Check_FrameRate_Example
parameter:
    Panel_Width: Width of the panel
    Panel_Height: Height of the panel
    Init_Target_Memory_Addr: Memory address of IT8951 target memory address
    BitsPerPixel: Bits Per Pixel, 2^BitsPerPixel = grayscale
******************************************************************************/
UBYTE Check_FrameRate_Example(UWORD Panel_Width, UWORD Panel_Height, UDOUBLE Target_Memory_Addr, UBYTE BitsPerPixel){
    UWORD Frame_Rate_Test_Width;
    if(Four_Byte_Align == true){
        Frame_Rate_Test_Width = Panel_Width - (Panel_Width % 32);
    }else{
        Frame_Rate_Test_Width = Panel_Width;
    }
    UWORD Frame_Rate_Test_Height = Panel_Height;
    UDOUBLE Imagesize;

    UBYTE *Refresh_FrameRate_Buf = NULL;

    UBYTE Count = 0;

    clock_t Frame_Rate_Test_Start, Frame_Rate_Test_Finish;
    double Frame_Rate_Test_Duration;

    Imagesize = ((Frame_Rate_Test_Width * BitsPerPixel % 8 == 0)? (Frame_Rate_Test_Width * BitsPerPixel / 8 ): (Frame_Rate_Test_Width * BitsPerPixel / 8 + 1)) * Frame_Rate_Test_Height;

    if((Refresh_FrameRate_Buf = (UBYTE *)malloc(Imagesize)) == NULL) {
        Debug("Failed to apply for image memory...\r\n");
        return -1;
    }

    Paint_NewImage(Refresh_FrameRate_Buf, Frame_Rate_Test_Width, Frame_Rate_Test_Height, 0, BLACK);
    Paint_SelectImage(Refresh_FrameRate_Buf);
	Epd_Mode(epd_mode);
    Paint_SetBitsPerPixel(BitsPerPixel);

    Debug("Start to test Frame Rate\r\n");
    Frame_Rate_Test_Start = clock();

    for(int i=0; i<10; i++){

        Paint_Clear(WHITE);
        //For color definition of all BitsPerPixel, you can refer to GUI_Paint.h
        Paint_DrawRectangle(20, 20, Frame_Rate_Test_Width-20, Frame_Rate_Test_Height-20, 0x00, DOT_PIXEL_4X4, DRAW_FILL_EMPTY);//To prevent arrays from going out of bounds
        Paint_DrawNum(Frame_Rate_Test_Width/2, Frame_Rate_Test_Height/2, ++Count, &Font24, 0x00, 0xF0);
        Paint_DrawString_EN(Frame_Rate_Test_Width/2, Frame_Rate_Test_Height/4, "frame rate test", &Font20, 0xF0, 0x00);
        Paint_DrawString_EN(Frame_Rate_Test_Width/2, Frame_Rate_Test_Height*3/4, "frame rate test", &Font20, 0xF0, 0x00);

        switch(BitsPerPixel){
            case 8:{
				if(epd_mode == 2)
					EPD_IT8951_8bp_Refresh(Refresh_FrameRate_Buf, 1280-Frame_Rate_Test_Width, 0, Frame_Rate_Test_Width,  Frame_Rate_Test_Height, false, Target_Memory_Addr);
				else if(epd_mode == 1)
					EPD_IT8951_8bp_Refresh(Refresh_FrameRate_Buf, 1872-Frame_Rate_Test_Width-16, 0, Frame_Rate_Test_Width,  Frame_Rate_Test_Height, false, Target_Memory_Addr);
				else					
					EPD_IT8951_8bp_Refresh(Refresh_FrameRate_Buf, 0, 0, Frame_Rate_Test_Width,  Frame_Rate_Test_Height, false, Target_Memory_Addr);
                break;
            }
            case 4:{
				if(epd_mode == 2)
					EPD_IT8951_4bp_Refresh(Refresh_FrameRate_Buf, 1280-Frame_Rate_Test_Width, 0, Frame_Rate_Test_Width,  Frame_Rate_Test_Height, false, Target_Memory_Addr,false);
				else if(epd_mode == 1)
					EPD_IT8951_4bp_Refresh(Refresh_FrameRate_Buf, 1872-Frame_Rate_Test_Width-16, 0, Frame_Rate_Test_Width,  Frame_Rate_Test_Height, false, Target_Memory_Addr,false);
				else
					EPD_IT8951_4bp_Refresh(Refresh_FrameRate_Buf, 0, 0, Frame_Rate_Test_Width,  Frame_Rate_Test_Height, false, Target_Memory_Addr,false);
                break;
            }
            case 2:{
				if(epd_mode == 2)
					EPD_IT8951_2bp_Refresh(Refresh_FrameRate_Buf, 1280-Frame_Rate_Test_Width, 0, Frame_Rate_Test_Width,  Frame_Rate_Test_Height, false, Target_Memory_Addr,false);
				else if(epd_mode == 1)
					EPD_IT8951_2bp_Refresh(Refresh_FrameRate_Buf, 1872-Frame_Rate_Test_Width-16, 0, Frame_Rate_Test_Width,  Frame_Rate_Test_Height, false, Target_Memory_Addr,false);
				else	
					EPD_IT8951_2bp_Refresh(Refresh_FrameRate_Buf, 0, 0, Frame_Rate_Test_Width,  Frame_Rate_Test_Height, false, Target_Memory_Addr,false);
                break;
            }
            case 1:{
				if(epd_mode == 2)
					EPD_IT8951_1bp_Refresh(Refresh_FrameRate_Buf, 1280-Frame_Rate_Test_Width, 0, Frame_Rate_Test_Width,  Frame_Rate_Test_Height, A2_Mode, Target_Memory_Addr,false);
				else if(epd_mode == 1)
					EPD_IT8951_1bp_Refresh(Refresh_FrameRate_Buf, 1872-Frame_Rate_Test_Width-16, 0, Frame_Rate_Test_Width,  Frame_Rate_Test_Height, A2_Mode, Target_Memory_Addr,false);
				else	
					EPD_IT8951_1bp_Refresh(Refresh_FrameRate_Buf, 0, 0, Frame_Rate_Test_Width,  Frame_Rate_Test_Height, A2_Mode, Target_Memory_Addr,false);
                break;
            }
        }
    }

    Frame_Rate_Test_Finish = clock();
    Frame_Rate_Test_Duration = (double)(Frame_Rate_Test_Finish - Frame_Rate_Test_Start) / CLOCKS_PER_SEC;
	Debug( "Write and Show 10 Frame occupy %f second\r\n", Frame_Rate_Test_Duration);
    Debug( "The frame rate is: %lf fps\r\n", 10/Frame_Rate_Test_Duration);

    if(Refresh_FrameRate_Buf != NULL){
        free(Refresh_FrameRate_Buf);
        Refresh_FrameRate_Buf = NULL;
    }

    return 0;
}

/******************************************************************************
function: TouchPanel_ePaper_Example
parameter:
    Panel_Width: Width of the panel
    Panel_Height: Height of the panel
    Init_Target_Memory_Addr: Memory address of IT8951 target memory address
******************************************************************************/
UBYTE TouchPanel_ePaper_Example(UWORD Panel_Width, UWORD Panel_Height, UDOUBLE Init_Target_Memory_Addr){
    int ret,fd;
    UWORD Touch_Pannel_Area_Width;
    if(Four_Byte_Align == true){
        Touch_Pannel_Area_Width = Panel_Width - (Panel_Width % 32);
    }else{
        Touch_Pannel_Area_Width = Panel_Width;
    }
    UWORD Touch_Pannel_Area_Height = Panel_Height;

    UDOUBLE Imagesize;

    UWORD Touch_Point0[2];
    UWORD Touch_X = 0,Touch_Y = 0;
    UWORD Touch_X_Old = 0,Touch_Y_Old = 0;

    UWORD Min_X = Panel_Width, Max_X = 0;
    UWORD Min_Y = Panel_Height, Max_Y = 0;

    UWORD X_Start, X_End, Y_Start, Y_End, Width, Height;

    UBYTE First_Point_Flag = 1;

    UWORD Panel_Frame_Buf_WidthByte;
    UWORD Panel_Area_Frame_Buf_WidthByte;

	if(access("/home/pi/FIFO",F_OK)){
		ret = mkfifo("/home/pi/FIFO",0777);
		if(ret == -1){
			Debug("mkfifo error!\n");
			exit(0);
		}
	}
    fd = open("/home/pi/FIFO",O_RDWR|O_NONBLOCK);
    if( fd == -1 )
    {
        Debug("Open error\r\n");
        exit(0);
    }

    Panel_Frame_Buf_WidthByte =  (Touch_Pannel_Area_Width * 1 % 8 == 0) ? (Touch_Pannel_Area_Width * 1 / 8 ): (Touch_Pannel_Area_Width * 1 / 8 + 1);

    Imagesize = ((Touch_Pannel_Area_Width * 1 % 8 == 0) ? (Touch_Pannel_Area_Width * 1 / 8 ): (Touch_Pannel_Area_Width *1 / 8 + 1)) * Touch_Pannel_Area_Height;

    if((Panel_Frame_Buf = (UBYTE *)malloc(Imagesize)) == NULL) {
        Debug("Failed to apply for Panel_Frame_Buf memory...\r\n");
        return -1;
    }

    //Assume the entire screen is refreshed
    if((Panel_Area_Frame_Buf = (UBYTE *)malloc(Imagesize)) == NULL) {
        Debug("Failed to apply for Panel_Area_Frame_Buf memory...\r\n");
        return -1;
    }

    Paint_NewImage(Panel_Frame_Buf, Touch_Pannel_Area_Width, Touch_Pannel_Area_Height, 0, BLACK);
    Paint_SelectImage(Panel_Frame_Buf);
	Epd_Mode(epd_mode);
    Paint_SetBitsPerPixel(1);
    Paint_Clear(WHITE);

    while(1)
    {
        Min_X = Panel_Width;
        Max_X = 0;
        Min_Y = Panel_Height;
        Max_Y = 0;

        First_Point_Flag = 1;

        ret = read(fd,Touch_Point0,sizeof(Touch_Point0));

        //Prepare the image
        while(ret == 4){
            Touch_X = Touch_Point0[0];
            Touch_Y = Touch_Point0[1];
            Paint_NewImage(Panel_Frame_Buf, Touch_Pannel_Area_Width, Touch_Pannel_Area_Height, 0, BLACK);
            Paint_SelectImage(Panel_Frame_Buf);
            Paint_SetBitsPerPixel(1);

            if(First_Point_Flag == 0)
            {
                //For color definition of all BitsPerPixel, you can refer to GUI_Paint.h
                Paint_DrawLine(Touch_X_Old, Touch_Y_Old, Touch_X, Touch_Y, 0x00, DOT_PIXEL_3X3, LINE_STYLE_SOLID);
            }
            Touch_X_Old = Touch_X;
            Touch_Y_Old = Touch_Y;
            First_Point_Flag = 0;

            if(Touch_X < Min_X){
                Min_X = Touch_X;
            }
            if(Touch_X > Max_X){
                Max_X = Touch_X;
            }
            if(Touch_Y < Min_Y){
                Min_Y = Touch_Y;
            }
            if(Touch_Y > Max_Y){
                Max_Y = Touch_Y;
            }

            DEV_Delay_ms(15);

            Debug("Touch_X:%d\r\n",Touch_X);
            Debug("Touch_Y:%d\r\n",Touch_Y);
            ret = read(fd,Touch_Point0,sizeof(Touch_Point0));
            Debug("Stop ret:%d\r\n",ret);
        }

        //If Min < Max, then Indicates that there is a refresh area
        if( (Min_X<Max_X)||(Min_Y<Max_Y) )
        {
            //----------Calculate Data, please be cautious that the width must be 32-bit aligned----------
            Debug("Min_X - Max_X Output:%d~%d\r\n",Min_X,Max_X);
            Debug("Min_Y - Max_Y Output:%d~%d\r\n",Min_Y,Max_Y);

            X_Start = Min_X < 32 ? 0 : Min_X - (Min_X % 32);
            Debug("X_Start:%d\r\n",X_Start);
            X_End = ( Max_X + (32 - (Max_X % 32)) ) > Touch_Pannel_Area_Width ? ( Max_X - (Max_X % 32) )  : ( Max_X + (32 - (Max_X % 32)) );
            Debug("X_End:%d\r\n",X_End);
            Y_Start = Min_Y;
            Debug("Y_Start:%d\r\n",Y_Start);
            Y_End = Max_Y;
            Debug("Y_Start:%d\r\n",Y_End);

            Width = X_End - X_Start;
            if(Width<=0){
                Width = 32;
            }
            Debug("Width:%d\r\n",Width);
            Height = Y_End-Y_Start;
            if(Height<=0){
                Height = 32;
            }
            Debug("Height:%d\r\n",Height);

            //----------Prepare Image----------
            Paint_NewImage(Panel_Area_Frame_Buf, Width, Height, 0, BLACK);
            Paint_SelectImage(Panel_Area_Frame_Buf);
			Epd_Mode(epd_mode);
            Paint_Clear(WHITE);

            Panel_Area_Frame_Buf_WidthByte = (Width % 8 == 0) ? (Width / 8 ): (Width / 8 + 1);

            for(int y = 0; y< Height; y++){
                memcpy(Panel_Area_Frame_Buf + (y * Panel_Area_Frame_Buf_WidthByte), Panel_Frame_Buf + ((Y_Start + y) * Panel_Frame_Buf_WidthByte) + X_Start/8 , Panel_Area_Frame_Buf_WidthByte);
            }

            //----------Display Image----------
            EPD_IT8951_1bp_Refresh(Panel_Area_Frame_Buf, X_Start, Y_Start, Width,  Height, A2_Mode, Init_Target_Memory_Addr, true);
        }
    }

    if( Panel_Area_Frame_Buf != NULL ){
        free(Panel_Area_Frame_Buf);
        Panel_Area_Frame_Buf = NULL;
    }

    if( Panel_Frame_Buf != NULL ){
        free(Panel_Frame_Buf);
        Panel_Frame_Buf = NULL;
    }

    return 0;
}



static UBYTE BMP_Test(UWORD Panel_Width, UWORD Panel_Height, UDOUBLE Init_Target_Memory_Addr, UBYTE BitsPerPixel, UBYTE Pic_Count)
{
    UWORD WIDTH;

    if(Four_Byte_Align == true){
        WIDTH  = Panel_Width - (Panel_Width % 32);
    }else{
        WIDTH = Panel_Width;
    }
    UWORD HEIGHT = Panel_Height;

    UDOUBLE Imagesize;

    Imagesize = ((WIDTH * BitsPerPixel % 8 == 0)? (WIDTH * BitsPerPixel / 8 ): (WIDTH * BitsPerPixel / 8 + 1)) * HEIGHT;
    if((Refresh_Frame_Buf = (UBYTE *)malloc(Imagesize)) == NULL) {
        Debug("Failed to apply for black memory...\r\n");
        return -1;
    }

    Paint_NewImage(Refresh_Frame_Buf, WIDTH, HEIGHT, 0, BLACK);
    Paint_SelectImage(Refresh_Frame_Buf);
	Epd_Mode(epd_mode);
    Paint_SetBitsPerPixel(BitsPerPixel);
    Paint_Clear(WHITE);


	char Path[30];
	sprintf(Path,"./pic/%dx%d_%d.bmp", WIDTH, HEIGHT, Pic_Count);
	GUI_ReadBmp(Path, 0, 0);

    switch(BitsPerPixel){
        case BitsPerPixel_8:{
            Paint_DrawString_EN(10, 10, "8 bits per pixel 16 grayscale", &Font24, 0xF0, 0x00);
            EPD_IT8951_8bp_Refresh(Refresh_Frame_Buf, 0, 0, WIDTH,  HEIGHT, false, Init_Target_Memory_Addr);
            break;
        }
        case BitsPerPixel_4:{
			Paint_DrawString_EN(10, 10, "4 bits per pixel 16 grayscale", &Font24, 0xF0, 0x00);
            EPD_IT8951_4bp_Refresh(Refresh_Frame_Buf, 0, 0, WIDTH,  HEIGHT, false, Init_Target_Memory_Addr,false);
            break;
        }
        case BitsPerPixel_2:{
            Paint_DrawString_EN(10, 10, "2 bits per pixel 4 grayscale", &Font24, 0xC0, 0x00);
            EPD_IT8951_2bp_Refresh(Refresh_Frame_Buf, 0, 0, WIDTH,  HEIGHT, false, Init_Target_Memory_Addr,false);
            break;
        }
        case BitsPerPixel_1:{
            Paint_DrawString_EN(10, 10, "1 bit per pixel 2 grayscale", &Font24, 0x80, 0x00);
            EPD_IT8951_1bp_Refresh(Refresh_Frame_Buf, 0, 0, WIDTH,  HEIGHT, A2_Mode, Init_Target_Memory_Addr,false);
            break;
        }
    }

    if(Refresh_Frame_Buf != NULL){
        free(Refresh_Frame_Buf);
        Refresh_Frame_Buf = NULL;
    }

    DEV_Delay_ms(5000);

    return 0;
}




void Factory_Test_Only(IT8951_Dev_Info Dev_Info, UDOUBLE Init_Target_Memory_Addr)
{
    while(1)
    {
        for(int i=0; i < 4; i++){
			EPD_IT8951_SystemRun();
			
			EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, GC16_Mode);
            // BMP_Test(Dev_Info.Panel_W, Dev_Info.Panel_H, Init_Target_Memory_Addr, BitsPerPixel_1, i);
            // BMP_Test(Dev_Info.Panel_W, Dev_Info.Panel_H, Init_Target_Memory_Addr, BitsPerPixel_2, i);
            BMP_Test(Dev_Info.Panel_W, Dev_Info.Panel_H, Init_Target_Memory_Addr, BitsPerPixel_4, i);
            // BMP_Test(Dev_Info.Panel_W, Dev_Info.Panel_H, Init_Target_Memory_Addr, BitsPerPixel_8, i);
			EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, GC16_Mode);
			
			EPD_IT8951_Sleep();
			DEV_Delay_ms(5000);
        }
		EPD_IT8951_SystemRun();
		
		EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, A2_Mode);
        Dynamic_Refresh_Example(Dev_Info,Init_Target_Memory_Addr);
		EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, A2_Mode);
		
		if(isColor) 
			Color_Test(Dev_Info, Init_Target_Memory_Addr);
		
		EPD_IT8951_Sleep();
		DEV_Delay_ms(5000);
    }
}

void Color_Test(IT8951_Dev_Info Dev_Info, UDOUBLE Init_Target_Memory_Addr)
{
	PAINT_TIME Time = {2020, 9, 30, 18, 10, 34};
	
	while(1) 
	{
		UWORD Panel_Width = Dev_Info.Panel_W;
		UWORD Panel_Height = Dev_Info.Panel_H;

		UDOUBLE Imagesize;

		//malloc enough memory for 1bp picture first
		Imagesize = ((Panel_Width * 1 % 8 == 0)? (Panel_Width * 1 / 8 ): (Panel_Width * 1 / 8 + 1)) * Panel_Height;
		if((Refresh_Frame_Buf = (UBYTE *)malloc(Imagesize*4)) == NULL) {
			Debug("Failed to apply for picture memory...\r\n");
		}

		Paint_NewImage(Refresh_Frame_Buf, Panel_Width, Panel_Height, 0, BLACK);
		Paint_SelectImage(Refresh_Frame_Buf);
		Epd_Mode(epd_mode);
		Paint_SetBitsPerPixel(4);
		Paint_Clear(WHITE);

		if(0) {
			Paint_DrawRectangle(100, 100, 300, 300, 0x0f00, DOT_PIXEL_1X1, DRAW_FILL_FULL);	//Red
			Paint_DrawRectangle(100, 400, 300, 600, 0x00f0, DOT_PIXEL_1X1, DRAW_FILL_FULL);	//Green
			Paint_DrawRectangle(100, 700, 300, 900, 0x000f, DOT_PIXEL_1X1, DRAW_FILL_FULL);	//Bule
			
			Paint_DrawCircle(500, 200, 100, 0x00ff, DOT_PIXEL_1X1, DRAW_FILL_FULL);
			Paint_DrawCircle(500, 500, 100, 0x0f0f, DOT_PIXEL_1X1, DRAW_FILL_FULL);
			Paint_DrawCircle(500, 800, 100, 0x0ff0, DOT_PIXEL_1X1, DRAW_FILL_FULL);
			
			Paint_DrawLine(1000, 200, 1100, 200, 0x055a, 10, LINE_STYLE_SOLID);
			Paint_DrawLine(1000, 300, 1100, 300, 0x05a5, 20, LINE_STYLE_SOLID);
			Paint_DrawLine(1000, 400, 1100, 400, 0x0a55, 30, LINE_STYLE_SOLID);

			Paint_DrawString_EN(1000, 500, "Hello, World!", &Font24, 0x0aa5, 0x0fff);
			Paint_DrawString_EN(1000, 600, "Hello, World!", &Font24, 0x0a5a, 0x0fff);
			Paint_DrawString_EN(1000, 700, "Hello, World!", &Font24, 0x05aa, 0x0fff);

			Paint_DrawString_CN(700, 400, "ÄãºÃ Î¢Ñ©µç×Ó", &Font24CN, 0x00fa, 0x0000);
			Paint_DrawNum(700, 500, 123456789, &Font24, 0x0a0f, 0x0fff);
			Paint_DrawTime(700, 600, &Time, &Font24, 0x0fa0, 0x0fff);
		}else {
			for(UWORD j=0; j<14; j++) {
				for(UWORD i=0; i<19; i++) {
					Paint_DrawRectangle(i*72, j*72+1, (i+1)*72-1, (j+1)*72, (i+j*19)*15, DOT_PIXEL_1X1, DRAW_FILL_FULL);
				}
			}
		}

		EPD_IT8951_4bp_Refresh(Refresh_Frame_Buf, 0, 0, Panel_Width,  Panel_Height, false, Init_Target_Memory_Addr, false);
		
		if(Refresh_Frame_Buf != NULL) {
			free(Refresh_Frame_Buf);
			Refresh_Frame_Buf = NULL;
		}

		DEV_Delay_ms(5000);
		break;
	}
}
