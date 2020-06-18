lib_LIBRARIES = libbcm2835.a
libbcm2835_a_SOURCES = bcm2835.c
include_HEADERS = bcm2835.h
check_PROGRAMS = test
test_SOURCES = test.c
test_LDADD = ./libbcm2835.a
TESTS = $(check_PROGRAMS)
CLEANFILES = *~

