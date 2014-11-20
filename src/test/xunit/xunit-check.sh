#!/bin/bash

usage() {
  echo "Usage: xunit-check.sh INPUT GOLDEN XSLT"
}

check_input() {
  FILE="$1"
  MESSAGE="$2"
  if [ -z "$FILE" ] || ! [ -f "$FILE" ]
  then
    echo "Wrong arguments: $MESSAGE"
    usage
    exit 1
  fi
}

ORIGIN="$1"
GOLDEN="$2"
XSLT="$3"

check_input $ORIGIN "INPUT"
check_input $GOLDEN "GOLDEN"
check_input $XSLT "XSLT"

OUTPUT="$(mktemp)"

xsltproc $XSLT $ORIGIN > $OUTPUT
xmllint --noblanks $GOLDEN > $OUTPUT.golden.noblanks
xmllint --noblanks $OUTPUT > $OUTPUT.noblanks

if diff -q $OUTPUT.golden.noblanks $OUTPUT.noblanks
then
  echo "PASS: $ORIGIN"
  RESULT=0
else
  xmllint --pretty 1 $GOLDEN > $OUTPUT.golden.pretty
  xmllint --pretty 1 $OUTPUT > $OUTPUT.pretty
  diff -u $OUTPUT.golden.pretty $OUTPUT.pretty
  echo "FAIL: $ORIGIN"
  RESULT=1
fi

rm -f $OUTPUT $OUTPUT.*

exit $RESULT
