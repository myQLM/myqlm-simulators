#file to be installed
cffi_files=\
			 skel/skel.h


#file to be installed
nobase_include_HEADERS = \
						 $(cffi_files)\
						 skel/version.h

if HAVE_PYTHON
../lib/skel/cffi_h.py: $(cffi_files)
	mkdir -p $$(dirname $@)
	for i in $^; do \
		echo "#include <$$i>";\
		done > cffi.h
	C_INCLUDE_PATH="$(top_srcdir)/packaged/include:$(abs_top_builddir)/packaged/include:\
	${C_INCLUDE_PATH}" \
	$(top_srcdir)/h2py.sh $$(echo ${CFLAGS}|sed 's/-g[0-9]\?\>//g') cffi.h $@;\
	rm cffi.h


all-local: ../lib/skel/cffi_h.py

.PHONY: ../lib/skel/cffi_h.py
endif
