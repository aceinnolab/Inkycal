if HAVE_DOXYGEN

doxyfile.stamp: ../src/bcm2835.h
	$(DOXYGEN) Doxyfile
	echo Timestamp > doxyfile.stamp

CLEANFILES = doxyfile.stamp *~

all-local: doxyfile.stamp

clean-local:
	rm -rf html
endif 
