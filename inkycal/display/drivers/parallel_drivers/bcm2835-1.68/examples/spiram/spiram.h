// spiram.h
//
// Header for a Little Library for accessing SPI RAM chips such as 23K256-I/P
// using bcm2835 library on Raspberry Pi
//
// Author: Mike McCauley
// Copyright (C) 2018 Mike McCauley
// This software is part of the bcm2835 library and is licensed under the same conditions
// $Id:  $

#include <stdbool.h> // bool, true, false

#ifndef SPIRAM_h
#define SPIRAM_h

#define SPIRAM_HOLD_DISABLE     0x1
#define SPIRAM_MODE_BYTE       (0x00 | SPIRAM_HOLD_DISABLE)
#define SPIRAM_MODE_PAGE       (0x80 | SPIRAM_HOLD_DISABLE)
#define SPIRAM_MODE_STREAM     (0x40 | SPIRAM_HOLD_DISABLE)
#define SPIRAM_MODE_INVALID    0xff
#define SPIRAM_OPCODE_READ_SR  0x05
#define SPIRAM_OPCODE_WRITE_SR 0x01
#define SPIRAM_OPCODE_READ     0x03
#define SPIRAM_OPCODE_WRITE    0x02

/* Size of a page in 23K256 */
#define SPIRAM_PAGE_SIZE       32

/*
 * This library allows you to read and write data from an external SPI interfaced static ram (SRAM)
 * such as 23K256 (256kbit = 32kByte)
 * Byte and POage modes are supported.
 * Valid addresses are from 0x0000 to 0x7fff
 * Tested on RPI 3 Model B, Raspbian Jessie
 */

/*
 * Initialise the spiram library, enables SPI with default divider of 
 * BCM2835_SPI_CLOCK_DIVIDER_65536 = 6.1035156kHz on RPI3.
 * You can change the SPI speed after calling this by calling bcm2835_spi_setClockDivider()
 * Returns true on success, false otherwise
 */
bool spiram_begin();

/*
 * Stops using the RPI SPI functions and returns the GPIO pins to their default behaviour.
 * Call this when you have finished using SPI forever, or at the end of your program
 * Returns true on success, false otherwise
 */
bool spiram_end();

/*
 * Read and returns the current value of the SRAM status register
 */
uint8_t spiram_read_sr();

/*
 * Write a new value to the SRAM status register, 
 * usually one of SPIRAM_MODE_*
 * You should never need to call this directly. Used internally.
 * Returns true on success, false otherwise
 */
bool spiram_write_sr(uint8_t value);

/*
 * Set the operating mode of the SRAM.
 * Mode is one of  SPIRAM_MODE_*. THis is done automatically 
 * by the spiram_write_* and spiram_read_* functions, so you would not normally
 * need to call this directly.
 * Returns true on success, false otherwise
 */
bool spiram_set_mode(uint8_t mode);

/*
 * Reads a single byte from the given address and returns it.
 */
uint8_t spiram_read_byte(uint16_t address);

/*
 * Writes a single byte to the given address.
 * Returns true on success, false otherwise
 */
bool spiram_write_byte(uint16_t address, uint8_t value);

/*
 * Reads a whole page of data (32 bytes) from the page starting at the given address.
 * The read data is placed in buf. Be sure that there is enough rom there for it.
 * Caution: if the starting address is not on a page boundary, 
 * it will wrap back to the beginning of the page.
 * Returns true on success, false otherwise
 */
bool spiram_read_page(uint16_t address, uint8_t *buf);

/*
 * Writes a whole page of data (32 bytes) to the page starting at the given address.
 * Caution: if the starting address is not on a page boundary, 
 * it will wrap back to the beginning of the page.
 * Returns true on success, false otherwise
 */
bool spiram_write_page(uint16_t address, uint8_t *buf);

#endif
