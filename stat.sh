#!/bin/sh

# XXX
#
# Version:  2012-05-29
# Author:   Pontus Stenetorp    <pontus stenetorp se>

# TODO: ARG CHECK!

CONT_FILE=$1

echo 'Total samples:'
wc -l ${CONT_FILE} | cut -f 1 -d ' '
echo
echo 'By category:'
cut -f 2 ${CONT_FILE} | sort | uniq -c | sort -r -n
echo
echo 'By seed:'
cut -f 2,4 ${CONT_FILE} | sort | uniq -c | sort -r -n
