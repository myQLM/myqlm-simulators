if HAVE_DOXYGEN
docpkg=$(PACKAGE_TARNAME)-doxy-$(PACKAGE_VERSION).tar.gz

.SECONDARY: doxygen.warn
doxygen.warn:
	$(DOXYGEN) Doxyfile
	if test $$(cat $@ | wc -l) -ne 0; \
	then \
		cat $@; \
	fi

if CHECK_DOC
check_doc:
	if test $$(cat doxygen.warn | wc -l) -ne 0; \
	then \
		cat doxygen.warn; \
	fi
else
check_doc:
	echo "No check of the documentation"
endif


$(docpkg):doxygen.warn
	cd html && tar czf ../$@ .

doc: doxygen.warn
	mkdir -p img

all-local: doxygen.warn check_doc


clean-local:
	rm -rf html doxygen.warn latex


doc_DATA=\
		 $(docpkg)

install-data-hook:
	[ -e $(DESTDIR)$(docdir)/$(PACKAGE_VERSION)/ ] && \
		echo "file $(DESTDIR)$(docdir)/$(PACKAGE_VERSION)/ exist continue\
		without installing the documentation"\
		&& exit 0;\
	mkdir $(DESTDIR)$(docdir)/$(PACKAGE_VERSION)/;\
	cd $(DESTDIR)$(docdir)/$(PACKAGE_VERSION);\
		tar xf ../$(docpkg) && rm -f ../$(docpkg)

uninstall-local:
	cd $(DESTDIR)$(docdir)/ && rm -rf $(PACKAGE_VERSION)

CLEANFILES=$(docpkg)
endif

EXTRA_DIST=\
		   README.md
