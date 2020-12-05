/*******************************************************************************
*
*   gpio.c
*
*   Copyright (c) 2013 Shahrooz Shahparnia
*
*   Description:
*   gpio is a command-line utility for executing gpio commands with the 
*   Broadcom bcm2835.  It was developed and tested on a Raspberry Pi single-board
*   computer model B.  The utility is based on the bcm2835 C library developed
*   by Mike McCauley of Open System Consultants, http://www.open.com.au/mikem/bcm2835/.
*
*   Invoking "gpio" results in a read, set of clear of a GPIO.  
*   Options include GPIO read/set/clear 
*   of a single GPIO pin, enabling or disabling pull up and pull downs as well as 
*   resetting all GPIOs to a default input state.  
*   The command usage and command-line parameters are described below
*   in the showusage function, which prints the usage if no command-line parameters
*   are included or if there are any command-line parameter errors.  Invoking gpio 
*   requires root privilege.
*
*   This file contains the main function as well as functions for displaying
*   usage and for parsing the command line.
*
*   Open Source Licensing GNU GPLv3
*
*   Building:
* After installing bcm2835, you can build this 
* with something like:
* gcc -o gpio gpio.c -l bcm2835
* sudo ./gpio
*
* Or you can test it before installing with:
* gcc -o gpio -I ../../src ../../src/bcm2835.c gpio.c
* sudo ./gpio
*
*
*   History:
*   11/10    VERSION 1.0.0: Original
*
*      User input parsing (comparse) and showusage\
*      have been adapted from: http://ipsolutionscorp.com/raspberry-pi-spi-utility/
*      mostly to keep consistence with the spincl tool usage.
*
*      Compile with: gcc -o gpio gpio.c bcm2835.c
*
*      Examples:
*            Clear pin 5: sudo ./gpio -ib -dc -pn -n5  
*            Reset all GPIOs to inputs and disable all pull up/downs: sudo ./gpio -ie
*            Read pin 10: sudo ./gpio -ib -dr -pn -n10
*            Read pin 10 in debug mode with verbose output: sudo ./gpio -ib -dr -pn -n10 -b
*            Read pin 10 and set pin as input with pull down: sudo ./gpio -ib -di -pd -n10
*
*            Note: Pin numbers match the Raspberry Pie connector pin numbers
********************************************************************************/

#include <bcm2835.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MODE_READ 0
#define MODE_SET 1
#define MODE_CLR 2
#define MODE_INPUT_READ 3

#define PULL_UP 0
#define PULL_DOWN 1
#define NO_PULL 2

#define GPIO_BEGIN 0
#define GPIO_END 1
#define NO_ACTION 2

#define NO_PIN 40 // Some big number that's beyond the connector's pin count
#define DEBUG_OFF 0
#define DEBUG_ON 1

uint8_t  init = NO_ACTION;
uint8_t  pull = NO_PULL;
uint8_t  mode = MODE_READ;
uint8_t  pin_number = NO_PIN;

uint8_t i, len;
uint8_t data, pin, debug_mode = DEBUG_OFF;

//*******************************************************************************
//  comparse: Parse the command line and return EXIT_SUCCESS or EXIT_FAILURE
//    argc: number of command-line arguments
//    argv: array of command-line argument strings
//*******************************************************************************

void gpio_reset(void);

int comparse(int argc, char **argv) {
    int argnum, i, xmitnum;
	
    if (argc < 2) {  // must have at least program name and len arguments
                     // or -ie (GPIO_END) or -ib (GPIO_BEGIN)
        fprintf(stderr, "Insufficient command line arguments\n");
        return EXIT_FAILURE;
    }
    
    argnum = 1;
    while (argnum < argc && argv[argnum][0] == '-') {

        switch (argv[argnum][1]) {

            case 'i':  // GPIO init
                switch (argv[argnum][2]) {
                    case 'b': init = GPIO_BEGIN; break;
                    case 'e': init = GPIO_END; break;
                    default:
                        fprintf(stderr, "%c is not a valid init option\n", argv[argnum][2]);
                        return EXIT_FAILURE;
                }
                break;

            case 'd':  // Set/Clear/Read Mode
                switch (argv[argnum][2]) {
                    case 'r': mode = MODE_READ; break;
                    case 's': mode = MODE_SET; break;
                    case 'c': mode = MODE_CLR; break;
		    case 'i': mode = MODE_INPUT_READ; break;
		    default:
                        fprintf(stderr, "%c is not a valid init option\n", argv[argnum][2]);
                        return EXIT_FAILURE;
                }
                break;
		
            case 'p':  // Pull up, down and no pull Mode
                switch (argv[argnum][2]) {
                    case 'u': pull = PULL_UP; break;
                    case 'd': pull = PULL_DOWN; break;
                    case 'n': pull = NO_PULL; break;
		    default:
                        fprintf(stderr, "%c is not a valid init option\n", argv[argnum][2]);
                        return EXIT_FAILURE;
                }
                break;		

            case 'n':  // pin number
	         pin_number = atoi(argv[argnum]+2);
                 break;

            case 'b':  // debug mode
		 debug_mode = DEBUG_ON;
                 break;

            default:
                fprintf(stderr, "%c is not a valid option\n", argv[argnum][1]);
                return EXIT_FAILURE;
        }

        argnum++;   // advance the argument number

    }

    if (argnum == argc && init != NO_ACTION) // no further arguments are needed
        return EXIT_SUCCESS;
  
    return EXIT_SUCCESS;
}

//*******************************************************************************
//  showusage: Print the usage statement and return errcode.
//*******************************************************************************

int showusage(int errcode) {
    printf("gpio \n");
    printf("Usage: \n");
    printf("  gpio [options]\n");
    printf("\n");
    printf("  Invoking gpio to set or reset a GPIO, enable disable pull up or pull down. Initialize or release a GPIO.\n");
    printf("\n");
    printf("  The following are the options, which must be a single letter\n");
    printf("    preceded by a '-' and followed by another character.\n");
    printf("    -ix where x is the GPIO init option, b[egin] or e[nd]\n");
    printf("      The begin option must be executed before any transfer can happen.\n");
    printf("      The end option will return the GPIO to inputs and turn off all pull up and pull downs.\n");
    printf("      It may be included with a transfer.\n");
    printf("    -dx where x is 'c' for clear, 's' is for set, 'r' for read and 'i' for read and set as input.\n");
    printf("    -px where x is the GPIO pull up or down option. 'u' for pull up, 'd' for pull down and 'n' for none.\n");  
    printf("    -nx where x is the pin number.\n");
    printf("\n");
    return errcode;
}

int main(int argc, char **argv) {

    printf("Running ... \n");
    
    // parse the command line
    if (comparse(argc, argv) == EXIT_FAILURE) return showusage (EXIT_FAILURE);

    if (!bcm2835_init()) return 1;
      
    // GPIO begin if specified    
    if (init == GPIO_BEGIN) ;


    // If len is 0, no need to continue, but do GPIO end if specified
    // if (len == 0) {
    //     if (init == GPIO_END) ;
    //	 printf("Zero length ... error!\n");
    //     return EXIT_SUCCESS;
    // }
    switch (pin_number) {
            case 3:
	       pin = RPI_V2_GPIO_P1_03;
	    break;
            case 5:
	       pin = RPI_V2_GPIO_P1_05;
	    break;	    
            case 7:
	       pin = RPI_V2_GPIO_P1_07;
	    break;
            case 26:
	       pin = RPI_V2_GPIO_P1_26;
	    break;
            case 24:
	       pin = RPI_V2_GPIO_P1_24;
	    break;
            case 21:
	       pin = RPI_V2_GPIO_P1_21;
	    break;
            case 19:
	       pin = RPI_V2_GPIO_P1_19;
	    break;
            case 23:
	       pin = RPI_V2_GPIO_P1_23;
	    break;
            case 10:
	       pin = RPI_V2_GPIO_P1_10;
	    break;
            case 11:
	       pin = RPI_V2_GPIO_P1_11;
	    break;
            case 12:
	       pin = RPI_V2_GPIO_P1_12;
	    break;
            case 13:
	       pin = RPI_V2_GPIO_P1_13;
	    break;
            case 15:
	       pin = RPI_V2_GPIO_P1_15;
	    break;
            case 16:
	       pin = RPI_V2_GPIO_P1_16;
	    break;
            case 18:
	       pin = RPI_V2_GPIO_P1_18;
	    break;
            case 22:
	       pin = RPI_V2_GPIO_P1_22;
	    break;
	    default:
	      pin = NO_PIN;
    }

    switch (pull) {
    	    case PULL_UP:
		bcm2835_gpio_set_pud(pin, BCM2835_GPIO_PUD_UP);
	    break;
    	    case PULL_DOWN:
		bcm2835_gpio_set_pud(pin, BCM2835_GPIO_PUD_DOWN);
	    break;
    	    case NO_PULL:
		bcm2835_gpio_set_pud(pin, BCM2835_GPIO_PUD_OFF);
	    break;
    	    default:
		bcm2835_gpio_set_pud(pin, BCM2835_GPIO_PUD_OFF);	    
    }

    switch (mode) {
    	    case MODE_READ:
	       data = bcm2835_gpio_lev(pin);
	       printf("Reading pin: %d\n", data);
	    break;
    	    case MODE_INPUT_READ:
	       bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_INPT);
	       data = bcm2835_gpio_lev(pin);
	       printf("Reading pin: %d\n", data);
	    break; 
    	    case MODE_SET:
	       bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_OUTP);
	       bcm2835_gpio_set(pin);
	    break;
    	    case MODE_CLR:
	       bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_OUTP);
	       bcm2835_gpio_clr(pin);
	    break;
	    default:
	       printf("Wrong mode ...!\n");
    }

    if (debug_mode == DEBUG_ON) {    
    	printf("Init %d\n", init);    
    	printf("Mode %d\n", mode);
    	printf("Pull %d\n", pull);
    	printf("Pin Number %d\n", pin_number);
    	printf("Pin %d\n", pin);
    }   
       
    if (init == GPIO_END) gpio_reset();       
    bcm2835_close();
    printf("... done!\n");
    return 0;
}

void gpio_reset(void) {
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_03, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_05, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_07, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_26, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_24, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_21, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_19, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_23, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_10, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_11, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_12, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_13, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_15, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_16, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_18, BCM2835_GPIO_PUD_OFF);
	bcm2835_gpio_set_pud(RPI_V2_GPIO_P1_22, BCM2835_GPIO_PUD_OFF);

	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_03, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_05, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_07, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_26, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_24, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_21, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_19, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_23, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_10, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_11, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_12, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_13, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_15, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_16, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_18, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_22, BCM2835_GPIO_FSEL_INPT);
}
