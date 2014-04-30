#!/bin/sh

COUNT=0

while python -m unittest discover; do
  let COUNT+=1
  echo $COUNT
done
