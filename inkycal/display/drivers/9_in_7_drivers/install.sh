#!/bin/bash

# Installs drivers for 9.7" ePaper display
cd bcm2835-1.58
chmod +x configure
./configure
make
sudo make check
sudo make install

cd ..
cd IT8951
make clean
make
