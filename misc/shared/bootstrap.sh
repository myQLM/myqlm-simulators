#!/bin/sh
test -n "${srcdir}" || srcdir=$(dirname "$0")
test -n "${srcdir}" || srcdir=.
(
cd "${srcdir}" &&
    (libtoolize --copy --force || glibtoolize --copy --force) &&
    ([ -e aclocal.m4 ] || aclocal -I m4) &&
    (autoheader) &&
    (automake --add-missing --copy --gnu) &&
    (autoconf) 
) || exit
