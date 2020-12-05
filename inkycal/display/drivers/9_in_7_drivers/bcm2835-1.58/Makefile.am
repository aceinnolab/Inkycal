ACLOCAL_AMFLAGS = -I m4
SUBDIRS = src doc
CLEANFILES = *~
EXTRA_DIST = examples/blink/blink.c \
examples/input/input.c \
examples/event/event.c \
examples/spi/spi.c \
examples/spin/spin.c \
examples/pwm/pwm.c \
examples/i2c/i2c.c \
examples/gpio/gpio.c \
examples/spiram/spiram_test.c \
examples/spiram/spiram.c \
examples/spiram/spiram.h

upload:
	rsync -avz @PACKAGE_TARNAME@-@VERSION@.tar.gz doc/html/ www.airspayce.com:public_html/mikem/@PACKAGE_NAME@


