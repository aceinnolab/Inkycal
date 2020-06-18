SRCS=IT8951.c miniGUI.c main.c AsciiLib.c bmp.c
CC=gcc
TARGET=IT8951

$(TARGET):$(SRCS)
	$(CC) -Wall $(SRCS) -o $(TARGET) -lbcm2835
	
clean:
	rm -f $(TARGET)
