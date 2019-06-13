
#
##
#
if HAVE_PYTHON

            
$(abs_builddir)/qat:
	mkdir -p $@

$(abs_builddir)/qat/__init__.py: $(abs_builddir)/qat
	touch  $@

# Files present inside build and source folders should be installed with a special rule
qatdir=$(pythondir)/qat
nodist_qat_PYTHON=$(srcdir)/qat/__init__.py
                
$(abs_builddir)/qat/pylinalg:
	mkdir -p $@

# Files present inside build and source folders should be installed with a special rule
qatpylinalgdir=$(pythondir)/qat/pylinalg
nodist_qatpylinalg_PYTHON=		  $(srcdir)/qat/pylinalg/__init__.py
                
%.so: %.py
	mkdir -p $$(dirname $@)
	cython -3 -Werror -Wextra $< -o $*.c
	gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing  -I/usr/include/python3.6m -o $@ $*.c

# For installation
nobase_nodist_python_PYTHON=		  qat/pylinalg/version.py

nobase_python_PYTHON=\
				qat/__init__.py\
				qat/pylinalg/__init__.so\
				qat/pylinalg/service.so\
				qat/pylinalg/simulator.so\
				qat/pylinalg/qpu.so



qat/pylinalg/version.py:$(abs_top_builddir)/version.py $(abs_builddir)/qat/pylinalg
	cp $< $@


BUILT_SOURCES=\
	qat/pylinalg/version.py \
	${nobase_python_PYTHON}

dist-hook:
	mkdir -p $(distdir)/qat
	cp $(nodist_qat_PYTHON) $(distdir)/qat
                
	mkdir -p $(distdir)/qat/pylinalg
	cp $(nodist_qatpylinalg_PYTHON) $(distdir)/qat/pylinalg
                
# For generation
all-local: $(nobase_nodist_python_PYTHON) \
	       $(abs_builddir)/qat/__init__.py

clean-local:
	if test $(srcdir) != $(builddir);\
		then\
		rm -f $(builddir)/qat/__init__.py;\
		rm -f $(builddir)/qat/pylinalg/__init__.py;\
	fi

#
##
#
CLEANFILES=${nodist_python_PYTHON}
endif
            
