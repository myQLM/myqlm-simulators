SUBDIRS=packaged tests


if HAVE_SYSTEMD
DISTCHECK_CONFIGURE_FLAGS = \
			    --with-systemdsystemunitdir=$$dc_install_base/$(systemdsystemunitdir)
endif

EXTRA_DIST=\
		   valgrind.supp\
		   custom-test-driver\
		   vcsversion\
		   ${PACKAGE_NAME}.spec\
		   ChangeLog\
		   misc/shared/doxypypy.py\
		   misc/shared/doxypypy\
		   ${AC_EXTRA_DIST}

ACLOCAL_AMFLAGS=-I .autotools_cache/m4

TEST_REVISION=$(shell $(top_srcdir)/check_vcsrevision.sh $(top_srcdir) $(top_builddir))

current_makefile=$(lastword $(MAKEFILE_LIST))
rpm_topdir=$(shell rpm --eval="%_topdir")
rpmdir=$(shell rpm --eval="%_rpmdir")
srcrpmdir=$(shell rpm --eval="%_srcrpmdir")
sourcedir=$(shell rpm --eval="%_sourcedir")
pythonlibdir=$(shell rpm --eval="%python2_sitelib")


# TODO: specify your spec file here
specfile=$(top_srcdir)/@PACKAGE_NAME@.spec

# For release target (rt_)
# TODO: you may change that. See NovaForge for examples.
rt_project=exc_rd
rt_package=integration
rt_release=$(name)

# For (optionnal) doc target
#howto-basename= packaged/doc/HOWTO

# TODO: Here, you list all the files and directories you want to include
# with your release. When a directory is specified, all its content is
# taken into account recursively.
files=$(specfile) packaged/

#TODO: if you have man pages, list them here (they should be in the doc source folder)
man_files=

name=@PACKAGE_NAME@
version=@VERSION@
raw_release=$(shell awk '/^%define release/ {print $$NF}' $(specfile))
srelease=$(shell rpm --define='revision $${revision}.' --eval=$(raw_release))
release=$(shell rpm  --define='revision $${revision}.' --eval=$(raw_release))
arch=$(shell awk '/^BuildArch/ {print $$NF}' $(specfile))
pkg_dir= $(name)-$(version)
sub_pkgs_dir= $(addsuffix -$(version), $(addprefix $(name)-, ${SUBPACKAGES}))
tarall= $(pkg_dir).tar.gz
spackage_name=$(pkg_dir)-$(srelease)
package_name=$(pkg_dir)-$(release)
sub_package_names=$(addsuffix  -$(release), $(sub_pkgs_dir))
srpm= $(srcrpmdir)/$(spackage_name).src.rpm
sub_rpms= $(addprefix $(rpmdir)/$(arch)/, $(addsuffix .$(arch).rpm, $(sub_package_names)))
rpm= $(rpmdir)/$(arch)/$(package_name).$(arch).rpm
tar_srcdir=/tmp/$(USER)/$(pkg_dir)

# Default target: erase only produced files.
clean-local:
	rm -f *~ archives/$(shell basename $(rpm)) archives/$(shell basename $(srpm))

# Use this target to print out the version that will be produce
showversion:
	@version_from_spec $(specfile)

# Use this target to get information gathered by this Makefile.
# 'make config'
config:$(specfile)
	@echo "name:		$(name)"
	@echo "version:		$(version)"
	@echo "release:		$(release)"
	@echo "pkg_dir:		$(pkg_dir)"
	@echo "srpm:		$(srpm)"
	@echo "rpm:		$(rpm)"
	@echo "pythonlibdir:    $(pythonlibdir)"
	@echo "rt_project:	$(rt_project)"
	@echo "rt_package:	$(rt_package)"
	@echo "rt_release:	$(rt_release)"
	@echo "INFO: config OK"

# Documentation should not usually be included with your software
# since there is a documentation service that produces homogeneous,
# standardized documentation. Therefore, you can still write your
# documentation and archive it through CVS, but this documentation
# will have to be sent to Bull documentation service.  Anyway, this
# target allows the transformation of an OpenOffice file into a PDF
# and a TXT file using unoconv.
doc:
	rm -rf ${top_builddir}/packaged/doc/doxygen.warn
	${MAKE} -C packaged/doc doc
	if test $$(cat packaged/doc/doxygen.warn | wc -l) -ne 0; \
	then \
		cat packaged/doc/doxygen.warn; \
		exit 1;\
	fi

# Create the ChangeLog file and add changelog entries to the RPM .spec file.

log:
	git -C $(top_srcdir) --no-pager log --format="%ai %aN %n%n%x09* %s%d%n" > $(top_builddir)/ChangeLog


ChangeLog:
	touch $(top_builddir)/ChangeLog

generate_rpm:vcsversion log
	NB=$$(rpmspec -q $(specfile) | grep snapshot | wc -l);\
	if test $${NB} -gt 0; then \
		echo "Snapshot version detected in specfile! Check your versionning!" >&2;\
		exit 1;\
	fi
	make -C $(top_builddir) dist
	mkdir -p $(sourcedir)
	rm -f $(sourcedir)/$(tarall)
	cp ${DIST_ARCHIVES} $(sourcedir)/$(tarall)
	rpmbuild -bb -v --define='checkdoc --enable-check-doc' $(specfile) && echo "INFO: rpmbuild -bb -> OK";\
	rpmbuild -bs -v --define='checkdoc --enable-check-doc' $(specfile) && echo "INFO: rpmbuild -bs -> OK";\
	if test -f archives ; then rm -f archives ; mkdir -p archives ; fi;\
	if test ! -d archives ; then mkdir -p archives ; fi;\
	cp $(sub_rpms) archives || echo "no subpackage found";\
	cp $(srpm) archives/;\
	cp $(rpm) archives/

generate_devrpm:vcsversion ChangeLog
	NB=$$(rpmspec -q $(specfile) | grep snapshot | wc -l);\
	if test $${NB} -eq 0; then\
		echo "No mention to snapshot version in specfile! Check your versionning!" >&2;\
		exit 1;\
	fi
	make -C $(top_builddir) dist
	mkdir -p $(sourcedir)
	rm -f $(sourcedir)/$(tarall)
	cp ${DIST_ARCHIVES} $(sourcedir)/$(tarall)
	MODIF=$$(git -C ${top_srcdir} status -s | grep -v "??" | wc -l);\
	if test "$${MODIF}" != 0;  then \
		ST="M";\
	else\
		ST="";\
	fi;\
	revision=$$(echo $$(git -C $(top_srcdir) log --pretty=format:'%ad' --date=raw -1 | sed 's/ .*$$/'"$${ST}"'/'));\
	rpmbuild --nodeps -bb -v --define="revision $${revision}." $(specfile) && echo "INFO: rpmbuild -bb -> OK";\
	rpmbuild --nodeps -bs -v --define="revision $${revision}." $(specfile) && echo "INFO: rpmbuild -bs -> OK";\
	if test -f archives ; then rm -f archives ; mkdir -p archives ; fi;\
	if test ! -d archives ; then mkdir -p archives ; fi;\
	echo  "revision: $${revision}";\
	cp $(sub_rpms) archives || echo "some subpackage not found";\
	cp $(srpm) archives/;\
	cp $(rpm) archives/;

# This target speed up the build process: it does not generate the
# changelog file. use only for development.
devrpm: generate_devrpm

rpm: log generate_rpm

# auto_tag2 should be in your PATH
# This target is for tagging your software in the CVS tree.
# See DEV_PROCESS.readme for details.
tag: clean
	@echo -n "Launching the test suite? (y/N)"
	@read SURE; if test -n "$${SURE}" -a "$${SURE}" = "y";then make test;fi
	@if type auto_tag; then\
		auto_tag $(specfile);\
		autoreconf -f;\
		./config.status --recheck; \
	else\
		echo ;echo ;\
		echo "*************************************************";\
		echo "The script auto_tag cannot be found in your path!";\
		echo "Please install it!";\
		echo "For that purpose, I suggest you do something like:";\
		echo ;\
		echo "mkdir ~/.local/bull-exc-vcs ~/.local/bin";\
		echo "cd ~/.local/bull-exc-vcs";\
		echo "svn checkout https://nfbpshpc.frec.bull.fr:443/svn/hpcbxi/devtools/trunk devtools";\
		echo "ln -sf ~/.local/bull-exc-vcs/devtools/bin/* ~/.local/bin/";\
		echo "export PATH=~/.local/bin:\$PATH";\
		echo ;\
		echo "Enjoy! ;-)";\
		exit 1;\
	fi;

compile_tests: all
	${MAKE} -C tests compile_tests

test:
	@PYTHONPATH=packaged/lib:$(PYTHONPATH)
	./bootstrap.sh; \
	./configure; \
	make; \
	make check; \
	make distclean

release:
	@if type ask4release; then\
		ask4release $(current_makefile) $(specfile) $(rt_project) $(rt_package) $(rt_release);\
	else\
		echo ;echo ;\
		echo "*************************************************";\
		echo "The script ask4release cannot be found in your path!";\
		echo "Please install it!";\
		echo "For that purpose, I suggest you do something like:";\
		echo ;\
		echo "mkdir ~/.local/bull-exc-vcs ~/.local/bin";\
		echo "cd ~/.local/bull-exc-vcs";\
		echo "svn checkout https://nfbpshpc.frec.bull.fr:443/svn/hpcbxi/devtools/trunk devtools";\
		echo "ln -sf ~/.local/bull-exc-vcs/devtools/bin/* ~/.local/bin/";\
		echo "export PATH=~/.local/bin:\$PATH";\
		echo ;\
		echo "Enjoy! ;-)";\
		exit 1;\
	fi;


BUILT_SOURCES=config.h version.py setup.py
CLEANFILES=config.h version.py

setup.py:vcsversion template_setup.py
	cp template_setup.py $@

version.py:vcsversion template_version.py
	cp template_version.py $@
	VCSVERSION=`sed 's/.*: //' $<`;\
	echo "VCSVERSION = \"$$VCSVERSION\"" >> $@

config.h:vcsversion template_config.h
	cp template_config.h $@
	VCSVERSION=`sed 's/.*: //' $<`;\
	echo "#define VCSVERSION \"$$VCSVERSION\"" >> $@


vcsversion: ${TEST_REVISION}
	if ! test -e $(top_srcdir)/$@; then \
		BRANCH=$$(git -C $(top_srcdir) symbolic-ref HEAD 2> /dev/null | cut -b 12-);\
		LOG=$$(git -C $(top_srcdir) log --pretty=format:'%H, %ad' --date=iso -1);\
		MODIF=$$(git -C $(top_srcdir) status -s | grep -v "??" | wc -l);\
		if test "$${MODIF}" != 0; then \
			ST="MODIFIED";\
		else\
			ST="";\
		fi; \
		echo "$${BRANCH}-$${LOG} $${ST}" >> $@;\
	fi

dist:vcsversion
