#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@brief 

@namespace ...
@authors Jean-Noel Quintin <jean-noel.quintin@atos.net>
@copyright 2018  Bull S.A.S.  -  All rights reserved.
           This is not Free or Open Source software.
           Please contact Bull SAS for details about its license.
           Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois


Description ...

Overview
=========


"""
import os
import bxi.base.posless as posless
class Default(dict):
    def __missing__(self, key):
        return "{" + key + "}"

def write_doxygen_specific_file(args):
    with open("packaged/doc/Doxyfile_specific.in", 'w+') as f:
        if args.c or args.cpp:
            f.write("""
INPUT += @top_srcdir@/packaged/include \
         @top_srcdir@/packaged/lib \
         @abs_top_builddir@/packaged/include

EXAMPLE_PATH           +=  @top_srcdir@/packaged/doc/examples/
""")
        else:
            f.write("""
INPUT += @top_srcdir@/packaged/lib

EXAMPLE_PATH           +=  @top_srcdir@/packaged/doc/examples/
""")

def write_deps_file(args):
    with open("deps.make", 'w+') as f:
        f.write("""{name}.configure:  ${{addprefix qat-core., ${{CONFIG_DEPS}}}}
""".format(name=args.name))

def write_tests_makefile(args):
    f = open("tests/Makefile.am", 'w+')
    libname = args.name.replace("-","")
    f.write("""
if HAVE_TESTS
all-local:
	mkdir -p report
""")
    if args.py:
        f.write("""

if HAVE_PYTHON
check-local:
	PYTHONPATH=${abs_top_srcdir}/packaged/lib:${abs_top_builddir}/packaged/lib/:$${PYTHONPATH} \
		LD_LIBRARY_PATH=${abs_top_builddir}/packaged/lib/.libs:$${LD_LIBRARY_PATH} \
		CPATH=${abs_top_srcdir}/packaged/include:$${CPATH} \
		C_INCLUDE_PATH=${abs_top_srcdir}/packaged/include:$${C_INCLUDE_PATH} \
		${PYTHON} -mnose -v -w ${abs_top_srcdir} ${NOSETESTS_ARGS}
endif
""")

    if args.c or args.cpp:
        f.write("""
TESTS = \
		unit_t

inst_checkdir=$(docdir)/tests/
inst_check_PROGRAMS= \
					 unit_t

unit_t_CFLAGS =\
			   -I$(top_srcdir)/packaged/include\
			   -I$(top_srcdir)/packaged/src\
			   $(ZMQ_CFLAGS)\
			   $(UUID_CFLAGS)\
			   @TST_CFLAGS@

unit_t_LDFLAGS =\
				@TST_LDFLAGS@\
				$(ZMQ_LIBS)\
				$(UUID_LIBS)

unit_t_LDADD=$(top_builddir)/packaged/lib/lib{libname}.la\
				   @TST_LIBS@
unit_t$(EEXT):force

unit_t_SOURCES=\
			   unit_t.c
""".format(libname=libname))



    f.write("""
#TESTS_ENVIRONMENT=@VALGRIND@ @VALGRIND_ARGS@
AUTOMAKE_OPTIONS = parallel-tests
TEST_EXTENSIONS = .pl .sh .py
LOG_COMPILER =${VALGRIND}  `if   test "${VALGRIND}" !=  ""   ; then echo "${VALGRIND_ARGS}"; fi`
LOG_DRIVER=$(top_srcdir)/custom-test-driver
PY_LOG_DRIVER=PYTHONPATH=${abs_top_srcdir}/packaged/lib/:${abs_top_builddir}/packaged/lib/:${abs_top_srcdir}/tests:$${PYTHONPATH} \
			   PATH=${abs_top_srcdir}/packaged/bin:${abs_top_srcdir}/packaged/doc/examples:${PATH}\
			   LD_LIBRARY_PATH=${abs_top_builddir}/packaged/lib/.libs:$${LD_LIBRARY_PATH} \
			   ${LOG_DRIVER}

compile_tests:$(check_PROGRAMS)


force:${top_srcdir}/valgrind.supp
	mkdir -p report
	-[ -f $$(basename $^)  ] || cp $^ .

DISTCLEANFILES=\
			   valgrind.supp\
			   report/${PACKAGE_NAME}-Results.xml\
			   report/${PACKAGE_NAME}-Listing.xml


endif
            """)

def write_packaged_include_makefile(args):
    f = open("packaged/include/Makefile.am", 'w+')
    cincludename = args.name.replace("-","/")
    f.write("""
    nobase_include_HEADERS= %s/version.h
            """%cincludename)
    os.makedirs("packaged/include/%s"%cincludename)
    rel = "".join(["../"] * len(cincludename.split("/")))
    os.symlink("%s../../misc/shared/version.h.in"%rel,
               "packaged/include/%s/version.h.in"%cincludename)

def write_packaged_lib_makefile(args):
    f = open("packaged/lib/Makefile.am", 'w+')
    listnames = args.name.split("-")
    names = list()
    for i in range(len(listnames)):
        names.append("/".join(listnames[:i+1]))
    os.makedirs("packaged/lib/%s/"%names[-1])
    for name in names:
        pyf = open("packaged/lib/%s/__init__.py"%name, 'w+')
        pyf.write("""
# -*- coding: utf-8 -*-

\"\"\"
@authors Jean-Noel Quintin <jean-noel.quintin@atos.net>
@copyright 2017  Bull S.A.S.  -  All rights reserved.\n
           This is not Free or Open Source software.\n
           Please contact Bull SAS for details about its license.\n
           Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois

\"\"\"

# Try to find other packages in other folders (with separate build directory)
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
""")

    f.write("""
#
##
#
if HAVE_PYTHON

            """)
    for name in names:
        f.write("""
$(abs_builddir)/{name}:
	mkdir -p $@

$(abs_builddir)/{name}/__init__.py: $(abs_builddir)/{name}
	touch  $@

# Files present inside build and source folders should be installed with a special rule
{name2}dir=$(pythondir)/{name}
nodist_{name2}_PYTHON=\
		  $(srcdir)/{name}/__init__.py
                """.format(name=name, name2 = name.replace("/", "")))



    f.write("""
%.so: %.py
	mkdir -p $$(dirname $@)
	touch $*.py
	cython -D -3 -Werror -Wextra $< -o $*.c
	gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing  -I/usr/include/python3.4m -o $@ $*.c

# For installation
nobase_nodist_python_PYTHON=\
		  {name}/version.py

#nobase_python_PYTHON=\
#		  {name}/...



{name}/version.py:$(abs_top_builddir)/version.py $(abs_builddir)/{name}
	cp $< $@


BUILT_SOURCES={name}/version.py

dist-hook:""".format(name=names[-1]))

    for name in names:
        f.write("""
	mkdir -p $(distdir)/{name}
	cp $(nodist_{name2}_PYTHON) $(distdir)/{name}
                """.format(name=name, name2 = name.replace("/", "")))
    if len(names) > 1:
        f.write("""
# For generation
all-local: $(nobase_nodist_python_PYTHON) \\""")
    else:
        f.write("""
# For generation
all-local: $(nobase_nodist_python_PYTHON)""")

    for name in names[1:]:
            f.write("""
	            $(abs_builddir)/{name}/__init__.py\\""".format(name=name))
            f.write("""
	        $(abs_builddir)/{name}/__init__.py
                """.format(name=names[0]))
    f.write("""

clean-local:
	if test $(srcdir) != $(builddir);\\
		then\\""")
    for name in names:
            f.write("""
		rm -f $(builddir)/{name}/__init__.py;\\""".format(name=name))
    f.write("""
	fi

#
##
#
CLEANFILES=${nodist_python_PYTHON}
endif
            """)

def write_packaged_makefile(args):
    f = open("packaged/Makefile.am", 'w+')
    subfolders = ""
    if args.c or args.cpp:
        subfolders += "include "
    if args.py:
        subfolders += "lib "
    subfolders += "doc"

    f.write("""
SUBDIRS=%s
            """%subfolders)

    if args.c or args.cpp:
        clibname = args.name.replace("-","")
        f.write("""
lib_LTLIBRARIES=lib/lib{name}.la

lib_lib{name}_la_SOURCES=\
		  src/version.c
#		  src/{name}.c


lib_lib{name}_la_LDFLAGS=\
					 $(ZMQ_LIBS)\
					 $(LIBTOOLLDFLAGS)\
					 $(UUID_LIBS)

lib_lib{name}_la_CFLAGS=\
					 -I$(top_srcdir)/packaged/include\
					 $(ZMQ_CFLAGS)\
					 $(UUID_CFLAGS)\
					 $(LIB_CFLAGS)

lib_lib{name}_la_LIBADD=$(LIB_LIBS)

AM_CFLAGS=\
		  -I$(srcdir)/include\
		  -I$(builddir)/include\
		  $(ZMQ_CFLAGS)

AM_LDFLAGS=\
		  $(ZMQ_CFLAGS)\
		  $(ZMQ_LIBS)
            """.format(name=clibname))




def write_specfile(args):
    f = open('%s.spec'%args.name, 'w+')
    f.write("""
###############################################################################
#
# {_name} product packaging
#
###############################################################################

%define name {_name}

%define version 0.0.1

# Using the .snapshot suffix helps the SVN tagging process.
# Please run <your_svn_checkout>/devtools/packaged/bin/auto_tag -m
# to get the auto_tag man file # and to understand the tagging process.

# If you don't care, then, just starts with
# Bull.1.0%{?dist}.%{?revision}snapshot
# and run 'make tag' when you want to tag.
%define release Bull.1.0%{?dist}.%{?revision}snapshot

# Warning: Bull's continuous compilation tools refuse the use of
# %release in the src_dir variable!
%define src_dir %{name}-%{version}
%define src_tarall %{src_dir}.tar.gz


# Make RPM installation relocatable
Prefix: /etc
Prefix: /usr


# Predefined variables:
# {%_mandir} => normally /usr/share/man (depends on the PDP)
# %{perl_vendorlib} => /usr/lib/perl5/vendor_perl/

%define src_conf_dir conf
%define src_bin_dir bin
%define src_lib_dir lib
%define src_doc_dir doc

%define target_conf_dir /etc/
%define target_bin_dir /usr/bin
%define target_lib_dir /usr/lib*
%define target_include_dir /usr/include
%define target_prefix  /usr/
%define target_data_dir  %{target_prefix}/share/
%define target_python_lib_dir %{python_sitearch}
%define target_man_dir %{_mandir}
%define target_share_dir /usr/share/%{name}
%define target_doc_dir /usr/share/doc/%{name}
%define target_notebook_dir /usr/share/doc/qat


# Package summary
Summary:        New product {_name}
Name:           %{name}
Version:        %{version}
Release:        %{release}
Source:         %{src_tarall}

# Perform a 'cat /usr/share/doc/rpm-*/GROUPS' to get a list of available
# groups. Note that you should be in the corresponding PDP to get the
# most accurate information!
# TODO: Specify the category your software belongs to
Group:          Development/Libraries
BuildRoot:      %{_tmppath}/%{name}-root
# Automatically filled in by PDP: it should not appear therefore!
#Packager:      Bull <help@bull.net>
Distribution:   Bull HPC

# Automatically filled in by PDP: it should not appear therefore!
#Vendor:         Bull
License:        'Bull S.A.S. proprietary : All rights reserved'
BuildArch:      x86_64
URL:            https://novahpc.frec.bull.fr

Provides:       %{name}

#Conflicts:

# Product dependencies
#Requires:       backtrace
#Requires:       net-snmp
#Requires:       python-cffi >= 0.8.6

# Packaging dependencies
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  gcc
BuildRequires:  CUnit-devel

# For documentation generation
BuildRequires:  doxygen


# Main package description
%description
{_name} description

# Documenatation sub-package
%package doc
Summary: Documentation of the {_name} package

%description doc
Doxygen documentation of {_name} package

# Devel sub-package
%package devel
Summary: Header files providing the {_name} API
Requires: %{name}

%description devel
Header files providing the {_name} API

# Tests sub-package
%package tests
Requires: %{name}
Summary: Tests for the {_name} library

%description tests
Test for the {_name} library


###############################################################################
# Prepare the files to be compiled
%prep
#%setup -q -n %{name}
test "x$RPM_BUILD_ROOT" != "x" && rm -rf $RPM_BUILD_ROOT

%setup

%configure --disable-debug %{?checkdoc} \\
    --with-tagfiles-prefix=%{src_tagfiles_prefix} \\
    --with-tagfiles-suffix=%{src_tagfiles_suffix} \\
    --with-htmldirs-prefix=%{target_htmldirs_prefix} \\
    --with-htmldirs-suffix=%{target_htmldirs_suffix} \\
    %{_python_env}

###############################################################################
# The current directory is the one main directory of the tar
# Order of upgrade is:
#%pretrans new
#%pre new
#install new
#%post new
#%preun old
#delete old
#%postun old
#%posttrans new
%build
%{__make}

%install
%{__make} install DESTDIR=$RPM_BUILD_ROOT  %{?mflags_install}
mkdir -p $RPM_BUILD_ROOT/%{target_doc_dir}
cp ChangeLog $RPM_BUILD_ROOT/%{target_doc_dir}
rm -f $RPM_BUILD_ROOT/%{target_lib_dir}/lib*.la

%post

%postun

%preun

%clean
cd /tmp
rm -rf $RPM_BUILD_ROOT/%{name}-%{version}
test "x$RPM_BUILD_ROOT" != "x" && rm -rf $RPM_BUILD_ROOT

###############################################################################
# Specify files to be placed into the package

# Main package
%files
%defattr(-,root,root)
#%{_libdir}/lib*
#%{target_bin_dir}/*
""".format_map(Default(_name=args.name)))
    if args.c or args.cpp:
        f.write("""
%{target_lib_dir}/lib*
""")
    if args.py:
        f.write("""
%{target_python_lib_dir}/*
""")
    f.write("""

# Changelog is automatically generated (see Makefile)
# The %doc macro already contain a default path (usually /usr/doc/)
# See:
# http://www.rpm.org/max-rpm/s1-rpm-inside-files-list-directives.html#S3-RPM-INSIDE-FLIST-DOC-DIRECTIVE for details
# %doc ChangeLog
# or using an explicit path:

%doc
       %{target_doc_dir}/ChangeLog
""")
    if args.c or args.cpp:
        f.write("""
# Devel sub-package files
%files devel
       %{_includedir}/{_name}/*.h
""".format_map(Default(_name=args.name)))
    f.write("""

# Documentation sub-package files
%files doc
       %{target_doc_dir}/%{version}/



##################################################
# %changelog is automatically generated by 'make log' (see the Makefile)
##################### WARNING ####################
## Do not add anything after the following line!
##################################################
%changelog""")


def write_configure(args):
    f = open('configure.ac', 'w+')
    f.write("""
AC_PREREQ([2.63])
AC_CONFIG_MACRO_DIR([.autotools_cache/m4])
AC_CONFIG_AUX_DIR([.autotools_cache])
m4_include([.autotools_cache/m4/common.m4])

define([MODULE], %s)

AC_PACKAGE([MODULE])
AC_INIT(MODULE, [MODULE_VERSION(MODULE)])
REPLACE_BRIEF(MODULE)
INIT_PRODUCT(MODULE)
            """ % args.name)

    if args.c:
        f.write("""
CHECK_C_COMPILER
                """)
    if args.cpp:
        f.write("""
CHECK_CXX_COMPILER
                """)
    if args.openmp:
        f.write("""

AC_OPENMP
CPPFLAGS="$CPPFLAGS $OPENMP_CFLAGS"
LDFLAGS="$LDFLAGS $OPENMP_CFLAGS"
                """)
    if args.c or args.cpp:
        f.write("""

AC_PROG_LIBTOOL


AC_CHECK_LIB([ssl], [isprint], [],
             [AC_MSG_ERROR([ssl library provided by openssl package not found])])
AC_CHECK_LIB([qatqproc], [printf], [],
             [AC_MSG_ERROR([Could not find qatqproc library])])
AC_CHECK_LIB([qatqpu], [printf], [],
             [AC_MSG_ERROR([Could not find qatqpu library])])
AC_CHECK_LIB([qatcore], [qat_core_util_unpack_options], [],
             [AC_MSG_ERROR([Could not find qatcore library])])
                """)
    f.write("""
DEFAULT_OPTION

DISABLE_TESTS
DISABLE_PYTHON
if test "$ENABLE_PYTHON" == "yes"
then
INIT_PYTHON


#PC_PYTHON_CHECK_MODULE([pyparsing], [], [AC_MSG_ERROR(Module not found)])
PC_PYTHON_CHECK_MODULE([cffi], [], [AC_MSG_ERROR(Module not found)])
fi

FLAGS_TEST


# Checks for library functions.
AC_FUNC_ERROR_AT_LINE
AC_FUNC_STRERROR_R
AC_CHECK_FUNCS([gethostname memset mkdir pow strdup strtol])

# Define RPMs subpackages
SUBPACKAGES="debuginfo doc devel tests"
AC_SUBST([SUBPACKAGES])
AC_EXTRA_DIST="h2py.sh"
AC_SUBST([AC_EXTRA_DIST])
#TODO add the pc.in file
AC_CONFIG_FILES([Makefile packaged/Makefile packaged/lib/Makefile packaged/doc/Makefile tests/Makefile 
            """)
    if args.c or args.cpp:
        f.write("""
            packaged/include/Makefile packaged/src/version.c packaged/include/%s/version.h
                """ % args.name)
    f.write("""
           ])
#include <stdio.h>

AC_OUTPUT

DISPLAY_CONF(MODULE)
            """)


def main():
    """Main function."""
    parser = posless.ArgumentParser(description='Adapt project for the new name')

    parser.add_argument('name',
                        type=str,
                        action="store",
                        help="name of your project")
    parser.add_argument('--c',
                        action="store_true",
                        help="Add if you have c code")
    parser.add_argument('--openmp',
                        action="store_true",
                        help="Add if you have openmp code")
    parser.add_argument('--cpp',
                        action="store_true",
                        help="Add if you have c++ code")
    parser.add_argument('--py',
                        action="store_true",
                        help="Add if you have python code")

    args = parser.parse_args()
    write_configure(args)
    write_specfile(args)
    write_packaged_makefile(args)
    write_tests_makefile(args)
    write_deps_file(args)
    write_doxygen_specific_file(args)

    if args.py:
        write_packaged_lib_makefile(args)

    if args.c or args.cpp:
        write_packaged_include_makefile(args)

if __name__ == '__main__':
    main()
    print('Now you can run: find . -name "*skel*" -exec rm -rf "{}" \;')
