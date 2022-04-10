# # IT8951 parallel drivers for Inkycal
Inkycal now comes shipped with support for several parallel E-Paper displays!
To allow Inkycal to use these displays, the following files were modified:
  * main.c -> This is the main file and contains info about how the program runs
  * example.c -> This file contains imported functions from the library. It was modified to display
  the .BMP file from a custom path, which was not possible before
  * example.h -> Any modification to functions in the example.c file need to be reflected here. If
  a function in example.c now uses an addtional parameter, it must be adapted here accordingly


## How it works
Before anything becomes affective, it is required to navigate to this folder and run:
````bash
sudo make clean
sudo make
```
This executes the MAKEFILE, which in turn compiles `main.c`, `example.c` and `example.h`.
