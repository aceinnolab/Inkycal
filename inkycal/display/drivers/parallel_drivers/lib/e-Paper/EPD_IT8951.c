/*****************************************************************************
* | File      	:   EPD_IT8951.c
* | Author      :   Waveshare team
* | Function    :   IT8951 Common driver
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2019-09-17
* | Info        :
* -----------------------------------------------------------------------------
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
#include "EPD_IT8951.h"
#include <time.h>

//basic mode definition
UBYTE INIT_Mode = 0;
UBYTE GC16_Mode = 2;
//A2_Mode's value is not fixed, is decide by firmware's LUT 
UBYTE A2_Mode = 6;

/******************************************************************************
function :	Software reset
parameter:
******************************************************************************/
static void EPD_IT8951_Reset(void)
{
    DEV_Digital_Write(EPD_RST_PIN, HIGH);
    DEV_Delay_ms(200);
    DEV_Digital_Write(EPD_RST_PIN, LOW);
    DEV_Delay_ms(10);
    DEV_Digital_Write(EPD_RST_PIN, HIGH);
    DEV_Delay_ms(200);
}


/******************************************************************************
function :	Wait until the busy_pin goes HIGH
parameter:
******************************************************************************/
static void EPD_IT8951_ReadBusy(void)
{
	// Debug("Busy ------\r\n");
    UBYTE Busy_State = DEV_Digital_Read(EPD_BUSY_PIN);
    //0: busy, 1: idle
    while(Busy_State == 0) {
        Busy_State = DEV_Digital_Read(EPD_BUSY_PIN);
    }
	// Debug("Busy Release ------\r\n");
}


/******************************************************************************
function :	write command
parameter:  command
******************************************************************************/
static void EPD_IT8951_WriteCommand(UWORD Command)
{
	//Set Preamble for Write Command
	UWORD Write_Preamble = 0x6000;
	
	EPD_IT8951_ReadBusy();

    DEV_Digital_Write(EPD_CS_PIN, LOW);
	
	DEV_SPI_WriteByte(Write_Preamble>>8);
	DEV_SPI_WriteByte(Write_Preamble);
	
	EPD_IT8951_ReadBusy();	
	
	DEV_SPI_WriteByte(Command>>8);
	DEV_SPI_WriteByte(Command);
	
	DEV_Digital_Write(EPD_CS_PIN, HIGH);
}


/******************************************************************************
function :	write data
parameter:  data
******************************************************************************/
static void EPD_IT8951_WriteData(UWORD Data)
{
    //Set Preamble for Write Command
	UWORD Write_Preamble = 0x0000;

    EPD_IT8951_ReadBusy();

    DEV_Digital_Write(EPD_CS_PIN, LOW);

	DEV_SPI_WriteByte(Write_Preamble>>8);
	DEV_SPI_WriteByte(Write_Preamble);

    EPD_IT8951_ReadBusy();

	DEV_SPI_WriteByte(Data>>8);
	DEV_SPI_WriteByte(Data);

    DEV_Digital_Write(EPD_CS_PIN, HIGH);
}


/******************************************************************************
function :	write multi data
parameter:  data
******************************************************************************/
static void EPD_IT8951_WriteMuitiData(UWORD* Data_Buf, UDOUBLE Length)
{
    //Set Preamble for Write Command
	UWORD Write_Preamble = 0x0000;

    EPD_IT8951_ReadBusy();

    DEV_Digital_Write(EPD_CS_PIN, LOW);

	DEV_SPI_WriteByte(Write_Preamble>>8);
	DEV_SPI_WriteByte(Write_Preamble);

    EPD_IT8951_ReadBusy();

    for(UDOUBLE i = 0; i<Length; i++)
    {
	    DEV_SPI_WriteByte(Data_Buf[i]>>8);
	    DEV_SPI_WriteByte(Data_Buf[i]);
    }
    DEV_Digital_Write(EPD_CS_PIN, HIGH);
}



/******************************************************************************
function :	read data
parameter:  data
******************************************************************************/
static UWORD EPD_IT8951_ReadData()
{
    UWORD ReadData;
	UWORD Write_Preamble = 0x1000;
    UWORD Read_Dummy;

    EPD_IT8951_ReadBusy();

    DEV_Digital_Write(EPD_CS_PIN, LOW);

	DEV_SPI_WriteByte(Write_Preamble>>8);
	DEV_SPI_WriteByte(Write_Preamble);

    EPD_IT8951_ReadBusy();

    //dummy
    Read_Dummy = DEV_SPI_ReadByte()<<8;
    Read_Dummy |= DEV_SPI_ReadByte();

    EPD_IT8951_ReadBusy();

    ReadData = DEV_SPI_ReadByte()<<8;
    ReadData |= DEV_SPI_ReadByte();

    DEV_Digital_Write(EPD_CS_PIN, HIGH);

    return ReadData;
}




/******************************************************************************
function :	read multi data
parameter:  data
******************************************************************************/
static void EPD_IT8951_ReadMultiData(UWORD* Data_Buf, UDOUBLE Length)
{
	UWORD Write_Preamble = 0x1000;
    UWORD Read_Dummy;

    EPD_IT8951_ReadBusy();

    DEV_Digital_Write(EPD_CS_PIN, LOW);

	DEV_SPI_WriteByte(Write_Preamble>>8);
	DEV_SPI_WriteByte(Write_Preamble);

    EPD_IT8951_ReadBusy();

    //dummy
    Read_Dummy = DEV_SPI_ReadByte()<<8;
    Read_Dummy |= DEV_SPI_ReadByte();

    EPD_IT8951_ReadBusy();

    for(UDOUBLE i = 0; i<Length; i++)
    {
	    Data_Buf[i] = DEV_SPI_ReadByte()<<8;
	    Data_Buf[i] |= DEV_SPI_ReadByte();
    }

    DEV_Digital_Write(EPD_CS_PIN, HIGH);
}



/******************************************************************************
function:	write multi arg
parameter:	data
description:	some situation like this:
* 1 commander     0    argument
* 1 commander     1    argument
* 1 commander   multi  argument
******************************************************************************/
static void EPD_IT8951_WriteMultiArg(UWORD Arg_Cmd, UWORD* Arg_Buf, UWORD Arg_Num)
{
     //Send Cmd code
     EPD_IT8951_WriteCommand(Arg_Cmd);
     //Send Data
     for(UWORD i=0; i<Arg_Num; i++)
     {
         EPD_IT8951_WriteData(Arg_Buf[i]);
     }
}


/******************************************************************************
function :	Cmd4 ReadReg
parameter:  
******************************************************************************/
static UWORD EPD_IT8951_ReadReg(UWORD Reg_Address)
{
    UWORD Reg_Value;
    EPD_IT8951_WriteCommand(IT8951_TCON_REG_RD);
    EPD_IT8951_WriteData(Reg_Address);
    Reg_Value =  EPD_IT8951_ReadData();
    return Reg_Value;
}



/******************************************************************************
function :	Cmd5 WriteReg
parameter:  
******************************************************************************/
static void EPD_IT8951_WriteReg(UWORD Reg_Address,UWORD Reg_Value)
{
    EPD_IT8951_WriteCommand(IT8951_TCON_REG_WR);
    EPD_IT8951_WriteData(Reg_Address);
    EPD_IT8951_WriteData(Reg_Value);
}



/******************************************************************************
function :	get VCOM
parameter:  
******************************************************************************/
static UWORD EPD_IT8951_GetVCOM(void)
{
    UWORD VCOM;
    EPD_IT8951_WriteCommand(USDEF_I80_CMD_VCOM);
    EPD_IT8951_WriteData(0x0000);
    VCOM =  EPD_IT8951_ReadData();
    return VCOM;
}



/******************************************************************************
function :	set VCOM
parameter:  
******************************************************************************/
static void EPD_IT8951_SetVCOM(UWORD VCOM)
{
    EPD_IT8951_WriteCommand(USDEF_I80_CMD_VCOM);
    EPD_IT8951_WriteData(0x0001);
    EPD_IT8951_WriteData(VCOM);
}



/******************************************************************************
function :	Cmd10 LD_IMG
parameter:  
******************************************************************************/
static void EPD_IT8951_LoadImgStart( IT8951_Load_Img_Info* Load_Img_Info )
{
    UWORD Args;
    Args = (\
        Load_Img_Info->Endian_Type<<8 | \
        Load_Img_Info->Pixel_Format<<4 | \
        Load_Img_Info->Rotate\
    );
    EPD_IT8951_WriteCommand(IT8951_TCON_LD_IMG);
    EPD_IT8951_WriteData(Args);
}


/******************************************************************************
function :	Cmd11 LD_IMG_Area
parameter:  
******************************************************************************/
static void EPD_IT8951_LoadImgAreaStart( IT8951_Load_Img_Info* Load_Img_Info, IT8951_Area_Img_Info* Area_Img_Info )
{
    UWORD Args[5];
    Args[0] = (\
        Load_Img_Info->Endian_Type<<8 | \
        Load_Img_Info->Pixel_Format<<4 | \
        Load_Img_Info->Rotate\
    );
    Args[1] = Area_Img_Info->Area_X;
    Args[2] = Area_Img_Info->Area_Y;
    Args[3] = Area_Img_Info->Area_W;
    Args[4] = Area_Img_Info->Area_H;
    EPD_IT8951_WriteMultiArg(IT8951_TCON_LD_IMG_AREA, Args,5);
}

/******************************************************************************
function :	Cmd12 LD_IMG_End
parameter:  
******************************************************************************/
static void EPD_IT8951_LoadImgEnd(void)
{
    EPD_IT8951_WriteCommand(IT8951_TCON_LD_IMG_END);
}


/******************************************************************************
function :	EPD_IT8951_Get_System_Info
parameter:  
******************************************************************************/
static void EPD_IT8951_GetSystemInfo(void* Buf)
{
    IT8951_Dev_Info* Dev_Info; 

    EPD_IT8951_WriteCommand(USDEF_I80_CMD_GET_DEV_INFO);

    EPD_IT8951_ReadMultiData((UWORD*)Buf, sizeof(IT8951_Dev_Info)/2);

    Dev_Info = (IT8951_Dev_Info*)Buf;
	Debug("Panel(W,H) = (%d,%d)\r\n",Dev_Info->Panel_W, Dev_Info->Panel_H );
	Debug("Memory Address = %X\r\n",Dev_Info->Memory_Addr_L | (Dev_Info->Memory_Addr_H << 16));
	Debug("FW Version = %s\r\n", (UBYTE*)Dev_Info->FW_Version);
	Debug("LUT Version = %s\r\n", (UBYTE*)Dev_Info->LUT_Version);
}


/******************************************************************************
function :	EPD_IT8951_Set_Target_Memory_Addr
parameter:  
******************************************************************************/
static void EPD_IT8951_SetTargetMemoryAddr(UDOUBLE Target_Memory_Addr)
{
	UWORD WordH = (UWORD)((Target_Memory_Addr >> 16) & 0x0000FFFF);
	UWORD WordL = (UWORD)( Target_Memory_Addr & 0x0000FFFF);

    EPD_IT8951_WriteReg(LISAR+2, WordH);
    EPD_IT8951_WriteReg(LISAR  , WordL);
}


/******************************************************************************
function :	EPD_IT8951_WaitForDisplayReady
parameter:  
******************************************************************************/
static void EPD_IT8951_WaitForDisplayReady(void)
{
    //Check IT8951 Register LUTAFSR => NonZero Busy, Zero - Free
    while( EPD_IT8951_ReadReg(LUTAFSR) )
    {
        //wait in idle state
    }
}





/******************************************************************************
function :	EPD_IT8951_HostAreaPackedPixelWrite_1bp
parameter:  
******************************************************************************/
static void EPD_IT8951_HostAreaPackedPixelWrite_1bp(IT8951_Load_Img_Info*Load_Img_Info,IT8951_Area_Img_Info*Area_Img_Info, bool Packed_Write)
{
    UWORD Source_Buffer_Width, Source_Buffer_Height;
    UWORD Source_Buffer_Length;

    UWORD* Source_Buffer = (UWORD*)Load_Img_Info->Source_Buffer_Addr;
    EPD_IT8951_SetTargetMemoryAddr(Load_Img_Info->Target_Memory_Addr);
    EPD_IT8951_LoadImgAreaStart(Load_Img_Info,Area_Img_Info);

    //from byte to word
    //use 8bp to display 1bp, so here, divide by 2, because every byte has full bit.
    Source_Buffer_Width = Area_Img_Info->Area_W/2;
    Source_Buffer_Height = Area_Img_Info->Area_H;
    Source_Buffer_Length = Source_Buffer_Width * Source_Buffer_Height;
    
    if(Packed_Write == true)
    {
        EPD_IT8951_WriteMuitiData(Source_Buffer, Source_Buffer_Length);
    }
    else
    {
        for(UDOUBLE i=0; i<Source_Buffer_Height; i++)
        {
            for(UDOUBLE j=0; j<Source_Buffer_Width; j++)
            {
                EPD_IT8951_WriteData(*Source_Buffer);
                Source_Buffer++;
            }
        }
    }

    EPD_IT8951_LoadImgEnd();
}





/******************************************************************************
function :	EPD_IT8951_HostAreaPackedPixelWrite_2bp
parameter:  
******************************************************************************/
static void EPD_IT8951_HostAreaPackedPixelWrite_2bp(IT8951_Load_Img_Info*Load_Img_Info, IT8951_Area_Img_Info*Area_Img_Info, bool Packed_Write)
{
    UWORD Source_Buffer_Width, Source_Buffer_Height;
    UWORD Source_Buffer_Length;

    UWORD* Source_Buffer = (UWORD*)Load_Img_Info->Source_Buffer_Addr;
    EPD_IT8951_SetTargetMemoryAddr(Load_Img_Info->Target_Memory_Addr);
    EPD_IT8951_LoadImgAreaStart(Load_Img_Info,Area_Img_Info);

    //from byte to word
    Source_Buffer_Width = (Area_Img_Info->Area_W*2/8)/2;
    Source_Buffer_Height = Area_Img_Info->Area_H;
    Source_Buffer_Length = Source_Buffer_Width * Source_Buffer_Height;

    if(Packed_Write == true)
    {
        EPD_IT8951_WriteMuitiData(Source_Buffer, Source_Buffer_Length);
    }
    else
    {
        for(UDOUBLE i=0; i<Source_Buffer_Height; i++)
        {
            for(UDOUBLE j=0; j<Source_Buffer_Width; j++)
            {
                EPD_IT8951_WriteData(*Source_Buffer);
                Source_Buffer++;
            }
        }
    }

    EPD_IT8951_LoadImgEnd();
}





/******************************************************************************
function :	EPD_IT8951_HostAreaPackedPixelWrite_4bp
parameter:  
******************************************************************************/
static void EPD_IT8951_HostAreaPackedPixelWrite_4bp(IT8951_Load_Img_Info*Load_Img_Info, IT8951_Area_Img_Info*Area_Img_Info, bool Packed_Write)
{
    UWORD Source_Buffer_Width, Source_Buffer_Height;
    UWORD Source_Buffer_Length;
	
    UWORD* Source_Buffer = (UWORD*)Load_Img_Info->Source_Buffer_Addr;
    EPD_IT8951_SetTargetMemoryAddr(Load_Img_Info->Target_Memory_Addr);
    EPD_IT8951_LoadImgAreaStart(Load_Img_Info,Area_Img_Info);

    //from byte to word
    Source_Buffer_Width = (Area_Img_Info->Area_W*4/8)/2;
    Source_Buffer_Height = Area_Img_Info->Area_H;
    Source_Buffer_Length = Source_Buffer_Width * Source_Buffer_Height;

    if(Packed_Write == true)
    {
        EPD_IT8951_WriteMuitiData(Source_Buffer, Source_Buffer_Length);
    }
    else
    {
        for(UDOUBLE i=0; i<Source_Buffer_Height; i++)
        {
            for(UDOUBLE j=0; j<Source_Buffer_Width; j++)
            {
                EPD_IT8951_WriteData(*Source_Buffer);
                Source_Buffer++;
            }
        }
    }
	
    EPD_IT8951_LoadImgEnd();
}







/******************************************************************************
function :	EPD_IT8951_HostAreaPackedPixelWrite_8bp
parameter:  
Precautions: Can't Packed Write
******************************************************************************/
static void EPD_IT8951_HostAreaPackedPixelWrite_8bp(IT8951_Load_Img_Info*Load_Img_Info,IT8951_Area_Img_Info*Area_Img_Info)
{
    UWORD Source_Buffer_Width, Source_Buffer_Height;

    UWORD* Source_Buffer = (UWORD*)Load_Img_Info->Source_Buffer_Addr;
    EPD_IT8951_SetTargetMemoryAddr(Load_Img_Info->Target_Memory_Addr);
    EPD_IT8951_LoadImgAreaStart(Load_Img_Info,Area_Img_Info);

    //from byte to word
    Source_Buffer_Width = (Area_Img_Info->Area_W*8/8)/2;
    Source_Buffer_Height = Area_Img_Info->Area_H;

    for(UDOUBLE i=0; i<Source_Buffer_Height; i++)
    {
        for(UDOUBLE j=0; j<Source_Buffer_Width; j++)
        {
            EPD_IT8951_WriteData(*Source_Buffer);
            Source_Buffer++;
        }
    }
    EPD_IT8951_LoadImgEnd();
}






/******************************************************************************
function :	EPD_IT8951_Display_Area
parameter:  
******************************************************************************/
static void EPD_IT8951_Display_Area(UWORD X,UWORD Y,UWORD W,UWORD H,UWORD Mode)
{
    UWORD Args[5];
    Args[0] = X;
    Args[1] = Y;
    Args[2] = W;
    Args[3] = H;
    Args[4] = Mode;
    //0x0034
    EPD_IT8951_WriteMultiArg(USDEF_I80_CMD_DPY_AREA, Args,5);
}



/******************************************************************************
function :	EPD_IT8951_Display_AreaBuf
parameter:  
******************************************************************************/
static void EPD_IT8951_Display_AreaBuf(UWORD X,UWORD Y,UWORD W,UWORD H,UWORD Mode, UDOUBLE Target_Memory_Addr)
{
    UWORD Args[7];
    Args[0] = X;
    Args[1] = Y;
    Args[2] = W;
    Args[3] = H;
    Args[4] = Mode;
    Args[5] = (UWORD)Target_Memory_Addr;
    Args[6] = (UWORD)(Target_Memory_Addr>>16);
    //0x0037
    EPD_IT8951_WriteMultiArg(USDEF_I80_CMD_DPY_BUF_AREA, Args,7); 
}



/******************************************************************************
function :	EPD_IT8951_Display_1bp
parameter:  
******************************************************************************/
static void EPD_IT8951_Display_1bp(UWORD X, UWORD Y, UWORD W, UWORD H, UWORD Mode,UDOUBLE Target_Memory_Addr, UBYTE Back_Gray_Val,UBYTE Front_Gray_Val)
{
    //Set Display mode to 1 bpp mode - Set 0x18001138 Bit[18](0x1800113A Bit[2])to 1
    EPD_IT8951_WriteReg(UP1SR+2, EPD_IT8951_ReadReg(UP1SR+2) | (1<<2) );

    EPD_IT8951_WriteReg(BGVR, (Front_Gray_Val<<8) | Back_Gray_Val);

    if(Target_Memory_Addr == 0)
    {
        EPD_IT8951_Display_Area(X,Y,W,H,Mode);
    }
    else
    {
        EPD_IT8951_Display_AreaBuf(X,Y,W,H,Mode,Target_Memory_Addr);
    }
    
    EPD_IT8951_WaitForDisplayReady();

    EPD_IT8951_WriteReg(UP1SR+2, EPD_IT8951_ReadReg(UP1SR+2) & ~(1<<2) );
}


/******************************************************************************
function :	Enhanced driving capability
parameter:  Enhanced driving capability for IT8951, in case the blurred display effect
******************************************************************************/
void Enhance_Driving_Capability(void)
{
    UWORD RegValue = EPD_IT8951_ReadReg(0x0038);
    Debug("The reg value before writing is %x\r\n", RegValue);

    EPD_IT8951_WriteReg(0x0038, 0x0602);

    RegValue = EPD_IT8951_ReadReg(0x0038);
    Debug("The reg value after writing is %x\r\n", RegValue);
}




/******************************************************************************
function :	Cmd1 SYS_RUN
parameter:  Run the system
******************************************************************************/
void EPD_IT8951_SystemRun(void)
{
    EPD_IT8951_WriteCommand(IT8951_TCON_SYS_RUN);
}


/******************************************************************************
function :	Cmd2 STANDBY
parameter:  Standby
******************************************************************************/
void EPD_IT8951_Standby(void)
{
    EPD_IT8951_WriteCommand(IT8951_TCON_STANDBY);
}


/******************************************************************************
function :	Cmd3 SLEEP
parameter:  Sleep
******************************************************************************/
void EPD_IT8951_Sleep(void)
{
    EPD_IT8951_WriteCommand(IT8951_TCON_SLEEP);
}


/******************************************************************************
function :	EPD_IT8951_Init
parameter:  
******************************************************************************/
IT8951_Dev_Info EPD_IT8951_Init(UWORD VCOM)
{
    IT8951_Dev_Info Dev_Info;

    EPD_IT8951_Reset();

    EPD_IT8951_SystemRun();

    EPD_IT8951_GetSystemInfo(&Dev_Info);
    
    //Enable Pack write
    EPD_IT8951_WriteReg(I80CPCR,0x0001);

    //Set VCOM by handle
    if(VCOM != EPD_IT8951_GetVCOM())
    {
        EPD_IT8951_SetVCOM(VCOM);
        Debug("VCOM = -%.02fV\n",(float)EPD_IT8951_GetVCOM()/1000);
    }
    return Dev_Info;
}


/******************************************************************************
function :	EPD_IT8951_Clear_Refresh
parameter:  
******************************************************************************/
void EPD_IT8951_Clear_Refresh(IT8951_Dev_Info Dev_Info,UDOUBLE Target_Memory_Addr, UWORD Mode)
{

    UDOUBLE ImageSize = ((Dev_Info.Panel_W * 4 % 8 == 0)? (Dev_Info.Panel_W * 4 / 8 ): (Dev_Info.Panel_W * 4 / 8 + 1)) * Dev_Info.Panel_H;
    UBYTE* Frame_Buf = malloc (ImageSize);
    memset(Frame_Buf, 0xFF, ImageSize);


    IT8951_Load_Img_Info Load_Img_Info;
    IT8951_Area_Img_Info Area_Img_Info;

    EPD_IT8951_WaitForDisplayReady();

    Load_Img_Info.Source_Buffer_Addr = (UDOUBLE)Frame_Buf;
    Load_Img_Info.Endian_Type = IT8951_LDIMG_L_ENDIAN;
    Load_Img_Info.Pixel_Format = IT8951_4BPP;
    Load_Img_Info.Rotate =  IT8951_ROTATE_0;
    Load_Img_Info.Target_Memory_Addr = Target_Memory_Addr;

    Area_Img_Info.Area_X = 0;
    Area_Img_Info.Area_Y = 0;
    Area_Img_Info.Area_W = Dev_Info.Panel_W;
    Area_Img_Info.Area_H = Dev_Info.Panel_H;

    EPD_IT8951_HostAreaPackedPixelWrite_4bp(&Load_Img_Info, &Area_Img_Info, false);

    EPD_IT8951_Display_Area(0, 0, Dev_Info.Panel_W, Dev_Info.Panel_H, Mode);

    free(Frame_Buf);
    Frame_Buf = NULL;
}


/******************************************************************************
function :	EPD_IT8951_1bp_Refresh
parameter:
******************************************************************************/
void EPD_IT8951_1bp_Refresh(UBYTE* Frame_Buf, UWORD X, UWORD Y, UWORD W, UWORD H, UBYTE Mode, UDOUBLE Target_Memory_Addr, bool Packed_Write)
{
    IT8951_Load_Img_Info Load_Img_Info;
    IT8951_Area_Img_Info Area_Img_Info;

    EPD_IT8951_WaitForDisplayReady();

    Load_Img_Info.Source_Buffer_Addr = (UDOUBLE)Frame_Buf;
    Load_Img_Info.Endian_Type = IT8951_LDIMG_L_ENDIAN;
    //Use 8bpp to set 1bpp
    Load_Img_Info.Pixel_Format = IT8951_8BPP;
    Load_Img_Info.Rotate =  IT8951_ROTATE_0;
    Load_Img_Info.Target_Memory_Addr = Target_Memory_Addr;

    Area_Img_Info.Area_X = X/8;
    Area_Img_Info.Area_Y = Y;
    Area_Img_Info.Area_W = W/8;
    Area_Img_Info.Area_H = H;


    //clock_t start, finish;
    //double duration;

    //start = clock();

    EPD_IT8951_HostAreaPackedPixelWrite_1bp(&Load_Img_Info, &Area_Img_Info, Packed_Write);

    //finish = clock();
    //duration = (double)(finish - start) / CLOCKS_PER_SEC;
	//Debug( "Write occupy %f second\n", duration );

    //start = clock();

    EPD_IT8951_Display_1bp(X,Y,W,H,Mode,Target_Memory_Addr,0xF0,0x00);

    //finish = clock();
    //duration = (double)(finish - start) / CLOCKS_PER_SEC;
	//Debug( "Show occupy %f second\n", duration );
}



/******************************************************************************
function :	EPD_IT8951_1bp_Multi_Frame_Write
parameter:  
******************************************************************************/
void EPD_IT8951_1bp_Multi_Frame_Write(UBYTE* Frame_Buf, UWORD X, UWORD Y, UWORD W, UWORD H,UDOUBLE Target_Memory_Addr, bool Packed_Write)
{
    IT8951_Load_Img_Info Load_Img_Info;
    IT8951_Area_Img_Info Area_Img_Info;

    EPD_IT8951_WaitForDisplayReady();

    Load_Img_Info.Source_Buffer_Addr = (UDOUBLE)Frame_Buf;
    Load_Img_Info.Endian_Type = IT8951_LDIMG_L_ENDIAN;
    //Use 8bpp to set 1bpp
    Load_Img_Info.Pixel_Format = IT8951_8BPP;
    Load_Img_Info.Rotate =  IT8951_ROTATE_0;
    Load_Img_Info.Target_Memory_Addr = Target_Memory_Addr;

    Area_Img_Info.Area_X = X/8;
    Area_Img_Info.Area_Y = Y;
    Area_Img_Info.Area_W = W/8;
    Area_Img_Info.Area_H = H;

    EPD_IT8951_HostAreaPackedPixelWrite_1bp(&Load_Img_Info, &Area_Img_Info,Packed_Write);
}




/******************************************************************************
function :	EPD_IT8951_1bp_Multi_Frame_Refresh
parameter:  
******************************************************************************/
void EPD_IT8951_1bp_Multi_Frame_Refresh(UWORD X, UWORD Y, UWORD W, UWORD H,UDOUBLE Target_Memory_Addr)
{
    EPD_IT8951_WaitForDisplayReady();

    EPD_IT8951_Display_1bp(X,Y,W,H, A2_Mode,Target_Memory_Addr,0xF0,0x00);
}




/******************************************************************************
function :	EPD_IT8951_2bp_Refresh
parameter:  
******************************************************************************/
void EPD_IT8951_2bp_Refresh(UBYTE* Frame_Buf, UWORD X, UWORD Y, UWORD W, UWORD H, bool Hold, UDOUBLE Target_Memory_Addr, bool Packed_Write)
{
    IT8951_Load_Img_Info Load_Img_Info;
    IT8951_Area_Img_Info Area_Img_Info;

    EPD_IT8951_WaitForDisplayReady();

    Load_Img_Info.Source_Buffer_Addr = (UDOUBLE)Frame_Buf;
    Load_Img_Info.Endian_Type = IT8951_LDIMG_L_ENDIAN;
    Load_Img_Info.Pixel_Format = IT8951_2BPP;
    Load_Img_Info.Rotate =  IT8951_ROTATE_0;
    Load_Img_Info.Target_Memory_Addr = Target_Memory_Addr;

    Area_Img_Info.Area_X = X;
    Area_Img_Info.Area_Y = Y;
    Area_Img_Info.Area_W = W;
    Area_Img_Info.Area_H = H;

    EPD_IT8951_HostAreaPackedPixelWrite_2bp(&Load_Img_Info, &Area_Img_Info,Packed_Write);

    if(Hold == true)
    {
        EPD_IT8951_Display_Area(X,Y,W,H, GC16_Mode);
    }
    else
    {
        EPD_IT8951_Display_AreaBuf(X,Y,W,H, GC16_Mode,Target_Memory_Addr);
    }
}




/******************************************************************************
function :	EPD_IT8951_4bp_Refresh
parameter:  
******************************************************************************/
void EPD_IT8951_4bp_Refresh(UBYTE* Frame_Buf, UWORD X, UWORD Y, UWORD W, UWORD H, bool Hold, UDOUBLE Target_Memory_Addr, bool Packed_Write)
{
    IT8951_Load_Img_Info Load_Img_Info;
    IT8951_Area_Img_Info Area_Img_Info;

    EPD_IT8951_WaitForDisplayReady();

    Load_Img_Info.Source_Buffer_Addr = (UDOUBLE)Frame_Buf;
    Load_Img_Info.Endian_Type = IT8951_LDIMG_L_ENDIAN;
    Load_Img_Info.Pixel_Format = IT8951_4BPP;
    Load_Img_Info.Rotate =  IT8951_ROTATE_0;
    Load_Img_Info.Target_Memory_Addr = Target_Memory_Addr;

    Area_Img_Info.Area_X = X;
    Area_Img_Info.Area_Y = Y;
    Area_Img_Info.Area_W = W;
    Area_Img_Info.Area_H = H;

    EPD_IT8951_HostAreaPackedPixelWrite_4bp(&Load_Img_Info, &Area_Img_Info, Packed_Write);

    if(Hold == true)
    {
        EPD_IT8951_Display_Area(X,Y,W,H, GC16_Mode);
    }
    else
    {
        EPD_IT8951_Display_AreaBuf(X,Y,W,H, GC16_Mode,Target_Memory_Addr);
    }
}


/******************************************************************************
function :	EPD_IT8951_8bp_Refresh
parameter:  
******************************************************************************/
void EPD_IT8951_8bp_Refresh(UBYTE *Frame_Buf, UWORD X, UWORD Y, UWORD W, UWORD H, bool Hold, UDOUBLE Target_Memory_Addr)
{
    IT8951_Load_Img_Info Load_Img_Info;
    IT8951_Area_Img_Info Area_Img_Info;

    EPD_IT8951_WaitForDisplayReady();

    Load_Img_Info.Source_Buffer_Addr = (UDOUBLE)Frame_Buf;
    Load_Img_Info.Endian_Type = IT8951_LDIMG_L_ENDIAN;
    Load_Img_Info.Pixel_Format = IT8951_8BPP;
    Load_Img_Info.Rotate =  IT8951_ROTATE_0;
    Load_Img_Info.Target_Memory_Addr = Target_Memory_Addr;

    Area_Img_Info.Area_X = X;
    Area_Img_Info.Area_Y = Y;
    Area_Img_Info.Area_W = W;
    Area_Img_Info.Area_H = H;

    EPD_IT8951_HostAreaPackedPixelWrite_8bp(&Load_Img_Info, &Area_Img_Info);

    if(Hold == true)
    {
        EPD_IT8951_Display_Area(X, Y, W, H, GC16_Mode);
    }
    else
    {
        EPD_IT8951_Display_AreaBuf(X, Y, W, H, GC16_Mode, Target_Memory_Addr);
    }
}
