// spiram.c
//
// Little library for accessing  SPI RAM such as 23K256-I/P
// using bcm2835 library on Raspberry Pi
//
// Author: Mike McCauley
// Copyright (C) 2018 Mike McCauley
// This software is part of the bcm2835 library and is licensed under the same conditions
// $Id:  $

#include <bcm2835.h>
#include <string.h> // memcpy
#include "spiram.h"

static uint8_t _mode = SPIRAM_MODE_INVALID;

uint8_t spiram_read_sr()
{
  uint8_t command[] = { SPIRAM_OPCODE_READ_SR, 0};
  bcm2835_spi_transfern(command, sizeof(command));
  return command[1];
}

bool spiram_write_sr(uint8_t value)
{
  uint8_t command[] = { SPIRAM_OPCODE_WRITE_SR, value};
  bcm2835_spi_transfern(command, sizeof(command));
  return true;
}

bool spiram_set_mode(uint8_t mode)
{
  if (mode != _mode)
    {
      spiram_write_sr(mode);
      _mode = mode;
    }
  return true;
}

bool spiram_begin()
{
  _mode = SPIRAM_MODE_BYTE;
  
  bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_MSBFIRST);      // The default
  bcm2835_spi_setDataMode(BCM2835_SPI_MODE0);                   // The default
  bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_65536); // The default
  bcm2835_spi_chipSelect(BCM2835_SPI_CS0);                      // The default
  bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS0, LOW);      // the default
  return true;
}

bool spiram_end()
{
  bcm2835_spi_end();
  return true;
}


uint8_t spiram_read_byte(uint16_t address)
{
  spiram_set_mode(SPIRAM_MODE_BYTE);
  uint8_t command[] = { SPIRAM_OPCODE_READ, (address >> 8) & 0xff, address & 0xff, 0xff };
  bcm2835_spi_transfern(command, sizeof(command));
  uint8_t ret = command[3];
}

bool spiram_write_byte(uint16_t address, uint8_t value)
{
  spiram_set_mode(SPIRAM_MODE_BYTE);
  uint8_t command[] = { SPIRAM_OPCODE_WRITE, (address >> 8) & 0xff, address & 0xff, value };
  bcm2835_spi_writenb(command, sizeof(command));
  return true;
}

bool spiram_read_page(uint16_t address, uint8_t *buf)
{
  spiram_set_mode(SPIRAM_MODE_PAGE);
  uint8_t command[3 + SPIRAM_PAGE_SIZE] = { SPIRAM_OPCODE_READ, (address >> 8) & 0xff, address & 0xff };
  bcm2835_spi_transfern(command, sizeof(command));
  memcpy(buf, command + 3, SPIRAM_PAGE_SIZE);
  return true;
}

bool spiram_write_page(uint16_t address, uint8_t *buf)
{
  spiram_set_mode(SPIRAM_MODE_PAGE);
  uint8_t command[3 + SPIRAM_PAGE_SIZE] = { SPIRAM_OPCODE_WRITE, (address >> 8) & 0xff, address & 0xff };
  memcpy(command + 3, buf, SPIRAM_PAGE_SIZE);;
  bcm2835_spi_writenb(command, sizeof(command));
  return true;
}
