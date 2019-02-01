#!/bin/bash

################################################################################
#
#
#
#
################################################################################

#
##
#

usage () {
    echo "$(basename ${0}) [gcc-options] header1.h ... headerN.h output.py"
}

help() {
    echo -e ""
    echo -e " header.h\tThe header file to convert"
    echo -e " output.py\tThe Python file in which to put the CFFI declaration"
    echo -e ""
    echo -e " -h, --help\tPrint this help"
    echo -e ""
}

_HEADERS=""
_OUTPUT=""


# Parsing arguments
#while [ ${#} -gt 0 ]
#do
#    case ${1} in
#        --help|-h)
#            usage
#            help
#            exit 0
#            ;;
#done

N=$((${#}-1))
_HEADERS=${*:1:$N}
LAST=$(($N+1))
_OUTPUT=${*:$LAST:$LAST}

if [ -z "${_HEADERS}" -o -z "${_OUTPUT}" ]
then
    usage >&2
    exit 1
fi

# Converting the header
cat > "${_OUTPUT}" <<EOF
#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# Author: Automated Conversion Tools
# Contributors:
###############################################################################
# Copyright (C) %%YEAR%%  Bull S. A. S.  -  All rights reserved
# Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois
# This is not Free or Open Source software.
# Please contact Bull S. A. S. for details about its license.
###############################################################################

C_DEF = """
EOF

sed "s/%%YEAR%%/$(date +%Y)/" -i "${_OUTPUT}"

#gcc -DCFFI -E -D__GNUC__=0 -w ${_HEADERS} | grep -v '^#' | sed '/^$/d;N' >> "${_OUTPUT}"
#gcc -DCFFI -E -D__GNUC__=0 -w ${_HEADERS} | grep -v '^#' | sed '/^$/d;N' >> "${_OUTPUT}"
gcc -DCFFI -E -D__GNUC__=0 -w ${_HEADERS} | sed '/^$/d;N' >> "${_OUTPUT}"
#gcc -DCFFI -E -D__GNUC__=0 -w ${_HEADERS} | sed '/^$/d;N' >> "${_OUTPUT}"
rc=${?}

cat >> "${_OUTPUT}" <<EOF
"""
EOF

# If something gone wrong, delete the generated file
if [ ${rc} -ne 0 ]
then
    rm -f "${_OUTPUT}"
fi

sed 's!//!/!g' -i "${_OUTPUT}"


exit ${rc}


#
##
#
