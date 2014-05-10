#!/bin/bash

COUNT=0

while python -m unittest discover; do
  echo $((COUNT+=1))
done
