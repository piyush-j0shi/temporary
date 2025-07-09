#!/bin/sh
INPUT_STRING=hi

while [ "$INPUT_STRING" != "bye" ]
do
  echo "type something (bye to quit)"
  read INPUT_STRING
  echo "you typed: $INPUT_STRING"
done
