#ifndef __EXAMPLE__
#define __EXAMPLE__

#include "../lib/e-Paper/EPD_IT8951.h"
#include "../lib/Config/DEV_Config.h"


// 1 bit per pixel, which is 2 grayscale
#define BitsPerPixel_1 1
// 2 bit per pixel, which is 4 grayscale 
#define BitsPerPixel_2 2
// 4 bit per pixel, which is 16 grayscale
#define BitsPerPixel_4 4
// 8 bit per pixel, which is 256 grayscale, but will automatically reduce by hardware to 4bpp, which is 16 grayscale
#define BitsPerPixel_8 8


//For all refresh fram buf except touch panel
extern UBYTE *Refresh_Frame_Buf;

//Only for touch panel
extern UBYTE *Panel_Frame_Buf;
extern UBYTE *Panel_Area_Frame_Buf;

extern bool Four_Byte_Align;

UBYTE Display_ColorPalette_Example(UWORD Panel_Width, UWORD Panel_Height, UDOUBLE Init_Target_Memory_Addr);

UBYTE Display_CharacterPattern_Example(UWORD Panel_Width, UWORD Panel_Height, UDOUBLE Init_Target_Memory_Addr, UBYTE BitsPerPixel);

UBYTE Display_BMP_Example(UWORD Panel_Width, UWORD Panel_Height, UDOUBLE Init_Target_Memory_Addr, UBYTE BitsPerPixel, char *Path);

UBYTE Dynamic_Refresh_Example(IT8951_Dev_Info Dev_Info, UDOUBLE Init_Target_Memory_Addr);

UBYTE Dynamic_GIF_Example(UWORD Panel_Width, UWORD Panel_Height, UDOUBLE Init_Target_Memory_Addr);

UBYTE Check_FrameRate_Example(UWORD Panel_Width, UWORD Panel_Height, UDOUBLE Target_Memory_Addr, UBYTE BitsPerPixel);

UBYTE TouchPanel_ePaper_Example(UWORD Panel_Width, UWORD Panel_Height, UDOUBLE Init_Target_Memory_Addr);

void Factory_Test_Only(IT8951_Dev_Info Dev_Info, UDOUBLE Init_Target_Memory_Addr);
void Color_Test(IT8951_Dev_Info Dev_Info, UDOUBLE Init_Target_Memory_Addr);

#endif
