#include "../lib/Config/DEV_Config.h"
#include "example.h"
#include "../lib/GUI/GUI_BMPfile.h"

#include <math.h>

#include <stdlib.h>     //exit()
#include <signal.h>     //signal()


#define USE_Normal_Demo false
#define SHOW_BMP true

UWORD VCOM = 2510;

IT8951_Dev_Info Dev_Info;
UWORD Panel_Width;
UWORD Panel_Height;
UDOUBLE Init_Target_Memory_Addr;
int epd_mode = 0;	//0: no rotate, no mirror
					//1: no rotate, horizontal mirror, for 10.3inch
					//2: no totate, horizontal mirror, for 5.17inch
					//3: no rotate, no mirror, isColor, for 6inch color
					
void  Handler(int signo){
    Debug("\r\nHandler:exit\r\n");
    if(Refresh_Frame_Buf != NULL){
        free(Refresh_Frame_Buf);
        Debug("free Refresh_Frame_Buf\r\n");
        Refresh_Frame_Buf = NULL;
    }
    if(Panel_Frame_Buf != NULL){
        free(Panel_Frame_Buf);
        Debug("free Panel_Frame_Buf\r\n");
        Panel_Frame_Buf = NULL;
    }
    if(Panel_Area_Frame_Buf != NULL){
        free(Panel_Area_Frame_Buf);
        Debug("free Panel_Area_Frame_Buf\r\n");
        Panel_Area_Frame_Buf = NULL;
    }
    if(bmp_src_buf != NULL){
        free(bmp_src_buf);
        Debug("free bmp_src_buf\r\n");
        bmp_src_buf = NULL;
    }
    if(bmp_dst_buf != NULL){
        free(bmp_dst_buf);
        Debug("free bmp_dst_buf\r\n");
        bmp_dst_buf = NULL;
    }
    Debug("Going to sleep\r\n");
    EPD_IT8951_Sleep();
    DEV_Module_Exit();
    exit(0);
}


int main(int argc, char *argv[])
{
    //Exception handling:ctrl + c
    signal(SIGINT, Handler);

    if (argc < 2){
        Debug("Please input VCOM value on FPC cable!\r\n");
        Debug("Example: sudo ./epd -2.51\r\n");
        exit(1);
    }
	if (argc != 3){
		Debug("Please input e-Paper display mode!\r\n");
		Debug("Example: sudo ./epd -2.51 0 or sudo ./epd -2.51 1\r\n");
		Debug("Now, 10.3 inch glass panle is mode1, else is mode0\r\n");
		Debug("If you don't know what to type in just type 0 \r\n");
		exit(1);
    }

    //Init the BCM2835 Device
    if(DEV_Module_Init()!=0){
        return -1;
    }

    double temp;
    sscanf(argv[1],"%lf",&temp);
    VCOM = (UWORD)(fabs(temp)*1000);
    Debug("VCOM value:%d\r\n", VCOM);
	sscanf(argv[2],"%d",&epd_mode);
    Debug("Display mode:%d\r\n", epd_mode);
    Dev_Info = EPD_IT8951_Init(VCOM);

    //get some important info from Dev_Info structure
    Panel_Width = Dev_Info.Panel_W;
    Panel_Height = Dev_Info.Panel_H;
    Init_Target_Memory_Addr = Dev_Info.Memory_Addr_L | (Dev_Info.Memory_Addr_H << 16);
    char* LUT_Version = (char*)Dev_Info.LUT_Version;
    if( strcmp(LUT_Version, "M641") == 0 ){
        //6inch e-Paper HAT(800,600), 6inch HD e-Paper HAT(1448,1072), 6inch HD touch e-Paper HAT(1448,1072)
        A2_Mode = 4;
        Four_Byte_Align = true;
    }else if( strcmp(LUT_Version, "M841_TFAB512") == 0 ){
        //Another firmware version for 6inch HD e-Paper HAT(1448,1072), 6inch HD touch e-Paper HAT(1448,1072)
        A2_Mode = 6;
        Four_Byte_Align = true;
    }else if( strcmp(LUT_Version, "M841") == 0 ){
        //9.7inch e-Paper HAT(1200,825)
        A2_Mode = 6;
    }else if( strcmp(LUT_Version, "M841_TFA2812") == 0 ){
        //7.8inch e-Paper HAT(1872,1404)
        A2_Mode = 6;
    }else if( strcmp(LUT_Version, "M841_TFA5210") == 0 ){
        //10.3inch e-Paper HAT(1872,1404)
        A2_Mode = 6;
    }else{
        //default set to 6 as A2 Mode
        A2_Mode = 6;
    }
    Debug("A2 Mode:%d\r\n", A2_Mode);

	EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, INIT_Mode);


#if(SHOW_BMP)
    //Show a bmp file
    //1bp use A2 mode by default, before used it, refresh the screen with WHITE
    Display_BMP_Example(Panel_Width, Panel_Height, Init_Target_Memory_Addr, BitsPerPixel_4, "/home/pi/InkycalVenv/inkycal/display/drivers/7_in_8_drivers/pic/1872x1404_2.bmp");
    EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, GC16_Mode);
#endif

#if(USE_Normal_Demo)
/*
    //Show 16 grayscale
    Display_ColorPalette_Example(Panel_Width, Panel_Height, Init_Target_Memory_Addr);
	EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, GC16_Mode);

    //Show some character and pattern
    Display_CharacterPattern_Example(Panel_Width, Panel_Height, Init_Target_Memory_Addr, BitsPerPixel_4);
    EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, GC16_Mode);

    //Show a bmp file
    //1bp use A2 mode by default, before used it, refresh the screen with WHITE
    Display_BMP_Example(Panel_Width, Panel_Height, Init_Target_Memory_Addr, BitsPerPixel_1);
    Display_BMP_Example(Panel_Width, Panel_Height, Init_Target_Memory_Addr, BitsPerPixel_2);
    Display_BMP_Example(Panel_Width, Panel_Height, Init_Target_Memory_Addr, BitsPerPixel_4);
    EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, GC16_Mode);
    
    //Show A2 mode refresh effect
    EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, A2_Mode);
    Dynamic_Refresh_Example(Dev_Info,Init_Target_Memory_Addr);
    EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, A2_Mode);
    EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, GC16_Mode);
	
    //Show how to display a gif, not works well on 6inch e-Paper HAT, 9.7inch e-Paper HAT, others work well
    EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, A2_Mode);
    Dynamic_GIF_Example(Panel_Width, Panel_Height, Init_Target_Memory_Addr);
    EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, A2_Mode);
    EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, GC16_Mode);

    //Show how to test frame rate, test it individually,which is related to refresh area size and refresh mode
    EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, A2_Mode);
    Check_FrameRate_Example(800, 600, Init_Target_Memory_Addr, BitsPerPixel_1);
    EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, A2_Mode);
    EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, GC16_Mode);
    * */
#endif


    //We recommended refresh the panel to white color before storing in the warehouse.
    EPD_IT8951_Clear_Refresh(Dev_Info, Init_Target_Memory_Addr, INIT_Mode);

    //EPD_IT8951_Standby();
    EPD_IT8951_Sleep();

    //In case RPI is transmitting image in no hold mode, which requires at most 10s
    DEV_Delay_ms(5000);

    DEV_Module_Exit();
    return 0;
}
