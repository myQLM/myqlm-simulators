#
##
#
if HAVE_PYTHON

$(abs_builddir)/skel:
	mkdir $@

$(abs_builddir)/skel/__init__.py: $(abs_builddir)/skel
	touch  $@



# For installation
nobase_nodist_python_PYTHON=\
		  skel/version.py\
		  skel/cffi_h.py

nobase_python_PYTHON=\
		  skel/ffi.py \
		  skel/hello.py


#File present inside build and source folder should be install with a special rule
skeldir=$(pythondir)/skel
nodist_skel_PYTHON=\
		  $(srcdir)/skel/__init__.py

skel/version.py:${abs_top_builddir}/version.py $(abs_builddir)/skel
	cp $< $@


BUILT_SOURCES=skel/version.py

dist-hook:
	cp ${nodist_skel_PYTHON} $(distdir)/skel

# For generation
all-local: $(nobase_nodist_python_PYTHON) $(abs_builddir)/skel/__init__.py

clean-local:
	if test $(srcdir) != $(builddir);\
		then\
		rm -f $(builddir)/skel/__init__.py;\
	fi

#
##
#
CLEANFILES=${nodist_python_PYTHON}
endif
