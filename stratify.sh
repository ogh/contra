#!/usr/bin/env bash

# Impose a cut-off on the seed level for a given context-file.
#
# Author:   Pontus Stenetorp    <pontus stenetorp se>
# Version:  2012-05-29

USAGE="${0} context_file"

if [ $# -ne 1 ]
then
    echo ${USAGE} 2>&1
    exit 1
fi
CONT_FILE=$1

# Used 100 for dev, 150 for test, 200 for train
CUT_OFF=150

SEEDS=`cut -f 4 ${CONT_FILE} | sort | uniq`

for SEED in ${SEEDS}
do
    grep $'^[^\t]\+\t[^\t]\+\t[^\t]\+\t'${SEED} ${CONT_FILE} | sort -R \
        | head -n ${CUT_OFF}
done
