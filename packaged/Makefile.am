lib_LTLIBRARIES=lib/libskel.la

lib_libskel_la_SOURCES=\
		  src/skel.c


lib_libskel_la_LDFLAGS=\
					 $(ZMQ_LIBS)\
					 $(LIBTOOLLDFLAGS)\
					 $(UUID_LIBS)

lib_libskel_la_CFLAGS=\
					 -I$(top_srcdir)/packaged/include\
					 $(ZMQ_CFLAGS)\
					 $(UUID_CFLAGS)\
					 $(LIB_CFLAGS)

lib_libskel_la_LIBADD=$(LIB_LIBS)

AM_CFLAGS=\
		  -I$(srcdir)/include\
		  -I$(builddir)/include\
		  $(ZMQ_CFLAGS)

AM_LDFLAGS=\
		  $(ZMQ_CFLAGS)\
		  $(ZMQ_LIBS)




SUBDIRS=include lib doc
