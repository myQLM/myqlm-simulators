#!/usr/bin/sh

USAGE="Usage: . dependencies.sh [directory]"

test "${BASH_SOURCE[0]}" != "${0}" || {
	echo $USAGE
	exit
}

if [ $# -ne 1 ] ; then
	echo $USAGE
else
	path="$PWD""/""$1"
	if [ ${path: (-1)} == "/" ]; then
		path=${path::-1}
	fi
	export LD_LIBRARY_PATH="$path""/lib64":$LD_LIBRARY_PATH
	export LIBRARY_PATH="$path""/lib64":$LIBRARY_PATH
	export PYTHONPATH="$path""/lib64/python3.4/site-packages/":$PYTHONPATH
	export CPATH="$path""/include":$CPATH
	export C_INCLUDE_PATH="$path""/include":$C_INCLUDE_PATH
	export PATH="$path""/bin":$PATH
fi
