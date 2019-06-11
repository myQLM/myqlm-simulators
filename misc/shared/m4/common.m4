define([MODULE_VERSION],[esyscmd([awk '/^%define version/ {print }' $1.spec | sed 's/.* //' | tr -d '\n'])])
define([MODULE_BRIEF],[esyscmd([awk '/^Summary:/ {print}' $1.spec | head -n 1 | sed 's/[^ \t]*[ \t]*\(.*\)/\1/' | tr -d '\n'])])
define([REPLACE_BRIEF],[
       PROJECT_BRIEF="MODULE_BRIEF($1)"
       AC_SUBST([PROJECT_BRIEF])
])


define([ADD_SYSTEMD],[
       AC_PROG_SED
       AC_ARG_WITH([systemdsysdir],
                        [AS_HELP_STRING([--with-systemdsysdir=DIR],
                                        [Directory for systemd service files])],
                        ,
                        [with_systemdsysdir=auto])
       AS_IF([test "x$with_systemdsysdir" = "xyes" -o "x$with_systemdsysdir" = "xauto"],
             [ def_systemdsystemunitdir=$($PKG_CONFIG --variable=systemdsystemunitdir systemd)

             if test $prefix != NONE; then
                 def_systemdsystemunitdir=$(echo $def_systemdsystemunitdir | $SED 's#'$($PKG_CONFIG  --variable=prefix systemd)'#'$prefix'#')
             fi

             AS_IF([test "x$def_systemdsystemunitdir" = "x"],
                   [AS_IF([test "x$with_systemdsysdir" = "xyes"],
                          [AC_MSG_ERROR([systemd support requested but pkg-config unable to query systemd package])])
                   with_systemdsysdir=no],
                   [with_systemdsysdir="$def_systemdsystemunitdir"])])
       AS_IF([test "x$with_systemdsysdir" != "xno"],
             [AC_SUBST([systemdsysdir], [$with_systemdsysdir])])
       AM_CONDITIONAL([HAVE_SYSTEMD], [test "x$with_systemdsysdir" != "xno"])
       ])

define([INIT_PRODUCT],[
    AC_CONFIG_MACRO_DIR([.autotools_cache/m4])
    AC_CONFIG_AUX_DIR([.autotools_cache])
    AC_CONFIG_HEADERS([template_config.h])
    AC_CONFIG_FILES([template_version.py])
    AC_CONFIG_FILES([template_setup.py])
    AM_INIT_AUTOMAKE([foreign subdir-objects])
    PKG_PROG_PKG_CONFIG

    if test "$2" == "systemd"; then
    ADD_SYSTEMD
    else
    AM_CONDITIONAL([HAVE_SYSTEMD], [test "xyes" = "xno"])
    fi

    AC_CHECK_PROGS([DOXYGEN], [doxygen])
    if test -z "$DOXYGEN"; then
        AC_MSG_WARN([Doxygen not found - continuing without Doxygen support])
    fi
    AC_CHECK_PROGS([DOT], [dot])
    if test -z "$DOT"; then
        AC_MSG_WARN([dot (graphviz) not found - continuing without dot support - The documentation will not be generated])
    fi
    AC_SUBST([DOC_FOLDER])
    ])

define([DEFAULT_OPTION],[
###########################
# debug
###########################
    AC_ARG_ENABLE([debug], [AS_HELP_STRING([--enable-debug], [enable debugging, default: yes])])
    if test x"$enable_debug" != "xno"; then
        CPPFLAGS="$CPPFLAGS -g3 -O0 ";
        CFLAGS="$CFLAGS -g3 -O0 ";
    fi

###########################
# gcov coverage reporting
###########################
    AC_ARG_ENABLE([gcov], [AS_HELP_STRING([--enable-gcov], [use Gcov to test the test suite , default: no])],)
    if test x"$enable_gcov" == "xyes"; then
        CFLAGS+=" --coverage"
        CPPFLAGS+=" --coverage"
        LDFLAGS+=" --coverage"
    else
        enable_gcov=no
    fi


###########################
# valgrind
###########################
    run_valgrind="no"
    AC_ARG_ENABLE([valgrind], [AS_HELP_STRING([--enable-valgrind[=args]], [use Valgrind to test the test suite])])
    if test x"$enable_valgrind" != "xno"; then
        AC_CHECK_PROG(VALGRIND_CHECK,valgrind,yes)
        if test x"$VALGRIND_CHECK" == "xyes"; then
            if test x"$enable_valgrind" == "xyes"; then
                enable_valgrind=""
            fi

            run_valgrind="yes"
            if test $# -eq 0; then
                VALGRIND='\$(abs_top_builddir)/libtool --mode=execute valgrind'
            fi
            if test $# -eq 1; then
                VALGRIND=$1
            fi
            AC_SUBST(VALGRIND)

        else
            AC_MSG_WARN([Please install valgrind before checking continuing without valgrind.])
            enable_valgrind=no
        fi

    fi
    if test x"$enable_valgrind" == "xno"; then
        enable_valgrind=""
    fi

    abs_path=$(readlink -f ${srcdir})

    VALGRIND_ARGS=" $enable_valgrind  --track-origins=yes --leak-check=full --show-reachable=yes --undef-value-errors=yes   --trace-children=no --child-silent-after-fork=yes --suppressions=${abs_path}/valgrind.supp "
    AC_SUBST(VALGRIND_ARGS)

###########################
# warnings
###########################
    AC_CHECK_PROGS([DOXYGEN], [doxygen])
    if test -z "$DOXYGEN"; then
        AC_MSG_WARN([Doxygen not found - continuing without Doxygen support])
    fi
    AC_CHECK_PROGS([DOT], [dot])
    if test -z "$DOT"; then
        AC_MSG_WARN([dot (graphviz) not found - continuing without dot support - The documentation will not be generated])
    fi
    AC_ARG_ENABLE([doc], [AS_HELP_STRING([--disable-doc], [disable the generation of the documentation])])
    if test x"$enable_doc" != "xno" ; then
        if ! test -z "$DOXYGEN";
        then
            if ! test -z "$DOT";
            then
                ENABLE_DOC="yes"
                AC_CONFIG_FILES([packaged/doc/Doxyfile packaged/doc/Doxyfile_specific])
            fi
        fi
    fi
    AM_CONDITIONAL([HAVE_DOXYGEN], [test x"$ENABLE_DOC" == "xyes"])
    if test x"$ENABLE_DOC" != "xyes"
    then
        ENABLE_DOC=no
    fi
    AC_ARG_ENABLE([check-doc], [AS_HELP_STRING([--enable-check-doc], [enable the documentation check])])
    AM_CONDITIONAL([CHECK_DOC], [test x"$enable_check_doc" == "xyes"])

    AC_ARG_ENABLE([mode-maintaners], [AS_HELP_STRING([--enable-mode-maintaners])])
    if test x"$enable_mode_maintaners" != "xno" ; then
        CPPFLAGS+=" -Wall -Werror  -Wextra -Wconversion "
    fi
###########################
    ])
define([DISABLE_TESTS],[
    ENABLE_TESTS=yes
    AC_ARG_ENABLE([tests], [AS_HELP_STRING([--disable-tests] , [disable the tests])])
    if test x"$enable_tests" == "xno"
    then
        ENABLE_TESTS=no
    fi
    AM_CONDITIONAL([HAVE_TESTS], [test x"$ENABLE_TESTS" == "xyes"])
    ])

define([DISABLE_PYTHON],[
    ENABLE_PYTHON=yes
    AC_ARG_ENABLE([python], [AS_HELP_STRING([--disable-python] , [disable the pyhon module])])
    if test x"$enable_python" == "xno"
    then
        ENABLE_PYTHON=no
    fi
    AM_CONDITIONAL([HAVE_PYTHON], [test x"$ENABLE_PYTHON" == "xyes"])
    ])

define([INIT_PYTHON], [
	#AM_PATH_PYTHON
	PC_INIT([1.0], [3.99], , [AM_MSG_ERROR([Python not found])])
	PC_PYTHON_SITE_PACKAGE_DIR
	#PC_PYTHON_EXEC_PACKAGE_DIR
	])

define([FLAGS_TEST], [
################################ testing dependencies ############################
    OLD_CPPLFAGS=${CPPFLAGS}
    OLD_LDLFAGS=${LDFLAGS}
    OLD_LIBS=${LIBS}
#build flags specifical for test

    AC_SEARCH_LIBS([curs_set], [curses])
    AC_SEARCH_LIBS([CU_register_suites], [cunit])

    TST_CPPFLAGS=${CPPFLAGS}
    TST_CFLAGS=${CPPFLAGS}
    TST_CPPFLAGS=${CFLAGS}
    TST_LDFLAGS=${LDFLAGS}
    TST_LIBS=${LIBS}

#does the substitution inside the makefile
    AC_SUBST(TST_CPPFLAGS)
    AC_SUBST(TST_CFLAGS)
    AC_SUBST(TST_CPPFLAGS)
    AC_SUBST(TST_LDFLAGS)
    AC_SUBST(TST_LIBS)

    CPPFLAGS=${OLD_CPPLFAGS}
    LDFLAGS=${OLD_LDLFAGS}
    LIBS=${OLD_LIBS}
])

define([CHECK_CXX_COMPILER],[
    # Checks for programs.
    AC_PROG_CXX
    AC_PROG_LIBTOOL
    AC_PROG_MKDIR_P
    AC_PROG_INSTALL


    #check the POSIX conformity
    AC_EGREP_CPP(posix_200809L_supported,
                 [#define _POSIX_C_SOURCE 200809L
                  #include <unistd.h>
                  #ifdef _POSIX_VERSION
                  #if _POSIX_VERSION == 200809L
                  posix_200809L_supported
                  #endif
                  #endif
                  ],
                  [],
                  [AC_MSG_FAILURE([*** Implementation must conform to the POSIX.1-2008 standard.])]
    )
    AX_CHECK_COMPILE_FLAG([-std=c++11], [
                        CXXFLAGS="$CXXFLAGS -std=c++11"])
    AC_ARG_ENABLE([optimisations], [AS_HELP_STRING([--disable-optimisations])])
    if test x"$enable_optimisations" != "xno" ; then
        AX_CHECK_COMPILE_FLAG([-mbmi2], [
                            CXXFLAGS="$CXXFLAGS -mbmi2"])
        AX_CHECK_COMPILE_FLAG([-mfma], [
                            CXXFLAGS="$CXXFLAGS -mfma"])
    fi
    # Checks for header files.
    # if some header are optional you could add tests there and get the macro defined
    #AC_CHECK_HEADERS([stdbool.h])

    # Checks for typedefs, structures, and compiler characteristics.


    AC_CHECK_HEADER([stdbool.h],
                    [],
                    [AC_MSG_ERROR([stdbool.h cannot be found])],
                )
    AC_C_INLINE
    AC_TYPE_INT64_T
    AC_TYPE_PID_T
    AC_TYPE_SIZE_T
    AC_TYPE_UINT16_T
    AC_TYPE_UINT32_T
    AC_TYPE_UINT64_T
    AC_TYPE_UINT8_T
])

define([CHECK_C_COMPILER],[
    # Checks for programs.
    AC_PROG_CC_C99
    AM_PROG_CC_C_O
    AC_PROG_LIBTOOL
    AC_PROG_MKDIR_P
    AC_PROG_INSTALL


    #check the POSIX conformity
    AC_EGREP_CPP(posix_200809L_supported,
                 [#define _POSIX_C_SOURCE 200809L
                  #include <unistd.h>
                  #ifdef _POSIX_VERSION
                  #if _POSIX_VERSION == 200809L
                  posix_200809L_supported
                  #endif
                  #endif
                  ],
                  [],
                  [AC_MSG_FAILURE([*** Implementation must conform to the POSIX.1-2008 standard.])]
    )
    # Checks for header files.
    # if some header are optional you could add tests there and get the macro defined
    #AC_CHECK_HEADERS([stdbool.h])

    # Checks for typedefs, structures, and compiler characteristics.


    AC_CHECK_HEADER([stdbool.h],
                    [],
                    [AC_MSG_ERROR([stdbool.h cannot be found])],
                )
    AC_C_INLINE
    AC_TYPE_INT64_T
    AC_TYPE_PID_T
    AC_TYPE_SIZE_T
    AC_TYPE_UINT16_T
    AC_TYPE_UINT32_T
    AC_TYPE_UINT64_T
    AC_TYPE_UINT8_T
])


define([DISPLAY_CONF],[
echo "summary   :"
echo "          MODULE          : "MODULE
echo "          VERSION         : "MODULE_VERSION($1)
echo "          CC              : ${CC}"
echo "          CPPFLAGS        : ${CPPFLAGS}"
echo "          LDFLAGS         : ${LDFLAGS} ${LIBS}"
echo
echo "          ENABLE_DOC      : ${ENABLE_DOC}"
echo "          ENABLE_PYTHON   : ${ENABLE_PYTHON}"
echo "          enable valgrind : $run_valgrind"
echo "          VALGRIND        : $VALGRIND"
echo "          GCOV            : ${enable_gcov}"
echo "          BRIEF           : MODULE_BRIEF($1)"
echo
echo
echo "          python site dir : "${pythondir}
])


define([CHECK_FLEX], [
AC_PROG_GREP
AC_PROG_SED
AC_PROG_LEX
AC_MSG_CHECKING([flex version])
flex_version=$($LEX --version | $GREP '^flex ' | $SED -e 's/^.\+ \([[0-9]]\+\.[[0-9]]\+\.[[0-9]]\+\)/\1/')
if test "$1" = "$flex_version"; then :
    AC_MSG_RESULT([yes])
    $2
    :
else
    AC_MSG_RESULT([no])
    $3
    :
fi
])
define([CHECK_BISON], [
AC_PROG_YACC
AC_MSG_CHECKING([bison version])
bison_version=$($YACC --version | $GREP '^bison ' | $SED -e 's/^.\+ \([[0-9]]\+\.[[0-9]]\+\)\(\.[[0-9]]\+-\?.*\)\?/\1/')
if test "$1" = "$bison_version"; then :
    AC_MSG_RESULT([yes])
    $2
    :
else
    AC_MSG_RESULT([no])
    $3
    :
fi
])


