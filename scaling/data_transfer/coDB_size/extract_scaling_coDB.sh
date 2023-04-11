#!/bin/bash -e

RUN_DIR=$PWD
SAFE_DIR=$RUN_DIR
echo Running tests in $RUN_DIR
echo and grabbing sample files from $SAFE_DIR
echo 

## Loop over cases for the colocated database
## to extract and concatenate data
DB_TYPE="co"
for TEST_TYPE in "coDB_size"
do
   for DB_BACKEND in "redis" "keydb"
   do
      for (( N=1; N<=32; N=N*2 ))
      do 
         TEST_DIR=${DB_TYPE}_${DB_BACKEND}_${N}
         echo Working in $TEST_DIR
         cd $TEST_DIR
         cat 4*/data_transfer.log > data_transfer.dat
         cd ..
         echo 
      done
   done
done

## Launch Python script to post-process results and create figure
python plot_coDB.py

