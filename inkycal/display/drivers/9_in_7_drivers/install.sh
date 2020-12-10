#!/bin/bash

# Unzip C++ SPI library and driver files
echo "Unzipping files"
unzip bcm2835-1.68.zip
unzip IT8951.zip
rm bcm2835-1.68.zip
rm IT8951.zip

# Install C++ SPI library for Raspberry
echo "Installing C++ SPI library"
cd bcm2835-1.68
chmod +x configure
./configure
make
sudo make check
sudo make install

# Install 9.7" E-Paper drivers
echo "Installing 9.7inch E-Paper drivers"
cd ..
cd IT8951
make clean
make

# Show image to check if it works
echo "Showing demo image"
sudo ./IT8951 0 0 pika.bmp

echo "If you see a pikachu on the E-Paper, the install"
echo "was successfull. If not, please report this issue."