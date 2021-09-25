#!/bin/bash

test_csv=result_test.csv

cp ../results.csv $test_csv
while true;
do
  ./generate.py -r $test_csv
  if [ "$?" == 1 ]; then
    break
  fi
done
rm $test_csv
