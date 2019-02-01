#!/bin/sh
MODULES=$(cat $1 | xargs echo | sed  's/\([^ ]\+\) \+/'"\'"'*\1*'"\'"',/g' |sed 's/\([^,]\+\)$/'"\'"'*\1*'"\'"'/')
sh -c "coverage xml --include=$(echo $MODULES) -o $2 $4"
RELATIVE=$(echo $3/ | sed 's#/#.#g')
if [ -f "$2" ]
then
sed -i 's#'"$RELATIVE"'##g' $2 
fi
