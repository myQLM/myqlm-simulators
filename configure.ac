
AC_PREREQ([2.63])
AC_CONFIG_MACRO_DIR([.autotools_cache/m4])
AC_CONFIG_AUX_DIR([.autotools_cache])
m4_include([.autotools_cache/m4/common.m4])

define([MODULE], qat-pylinalg)

AC_PACKAGE([MODULE])
AC_INIT(MODULE, [MODULE_VERSION(MODULE)])
REPLACE_BRIEF(MODULE)
INIT_PRODUCT(MODULE)
            
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
            
           ])
#include <stdio.h>

AC_OUTPUT

DISPLAY_CONF(MODULE)
            