// spiram_test.c
//
// Example program for bcm2835 
// Shows how to interface with SPI RAM such as 23K256-I/P
// using the spiram little library
//
// Tested on RPI 3 Model B, Raspbian Jessie
// Tested at full speed over many hours with no errors.
//
// Connect RPi 3 B to 23K256-I/P like this:
// RPi pin    Function     23K256-I/P pin (name)
// J1-6       GND          4 (VSS)
// J1-1       3.3V         8 (VCC)
//                    and  7 (/HOLD)
// J1-19      SPI0_MOSI    5 (SI)
// J1-21      SPI0_MISO    2 (SO)
// J1-23      SPI0_SCLK    6 (SCK)
// J1-24      SPI0_CE0_N   1 (/CS)
//
// After installing bcm2835, you can build this
// with something like:
// gcc -o spiram_test spiram.c spiram_test.c -l bcm2835
// sudo ./spiram_test
//
// Or you can test it before installing with:
// gcc -o spiram_test -I ../../src ../../src/bcm2835.c spiram.c spiram_test.c
// sudo ./spiram_test
//
// Author: Mike McCauley
// Copyright (C) 2018 Mike McCauley
// $Id:  $

#include <bcm2835.h>
#include <stdio.h>
#include <string.h> // memcmp
#include "spiram.h"

int main(int argc, char **argv)
{
  if (!bcm2835_init())
    {
      printf("bcm2835_init failed. Are you running as root??\n");
      return 1;
    }

  if (!bcm2835_spi_begin())
    {
      printf("bcm2835_spi_begin failed. Are you running as root??\n");
      return 1;
    }
  if (!spiram_begin())
    {
      printf("spiram_begin failed.\n");
      return 1;
    }
  /* You can speed things up by selecting a faster SPI speed
  // after spiram_begin, which defaults to BCM2835_SPI_CLOCK_DIVIDER_65536 = 6.1035156kHz on RPI3
  */
  bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_64); // 6.25MHz on RPI3

  uint8_t value = 0;
  uint16_t address = 0x0000;
  while (1)
    {
      uint8_t ret;

      /*      ret = spiram_read_sr();*/
      spiram_write_byte(address, value);
      ret = spiram_read_byte(address);
      if (ret != value)
	printf("ERROR: spiram_read_byte address %04x got %02x, expected %02x\n", address, ret, value);
#if 0
      printf("spiram_read_byte at address %04x got %02x\n", address, ret);
#endif
      
      uint8_t write_page_buf[SPIRAM_PAGE_SIZE] = { 0, value, value, value };
      uint8_t read_page_buf[SPIRAM_PAGE_SIZE];
      spiram_write_page(address, write_page_buf);
    
      spiram_read_page(address, read_page_buf);
      if (memcmp(write_page_buf, read_page_buf, SPIRAM_PAGE_SIZE) != 0)
	printf("ERROR: spiram_read_page at address %04x\n", address);
#if 0
      printf("spiram_read_page address %04x got ", address);
      int i;
      for (i = 0; i < SPIRAM_PAGE_SIZE; i++)
	printf("%02x ", read_page_buf[i]);
      printf("\n");
#endif
      /* sleep(1); */
      value++;
      address++;
    }
  
  spiram_end();
  bcm2835_close();
  return 0;
}

