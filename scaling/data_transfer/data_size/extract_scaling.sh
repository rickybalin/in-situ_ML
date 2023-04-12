#!/bin/bash -e

module load conda/2022-09-08
conda activate /lus/grand/projects/datascience/balin/SC23/in-situ_ML/installation/ssim

RUN_DIR=$PWD
SAFE_DIR=$RUN_DIR
echo Running tests in $RUN_DIR
echo and grabbing sample files from $SAFE_DIR
echo 

## Loop over cases for the colocated database
## to extract and concatenate data
DB_TYPE="co"
for TEST_TYPE in "data_size"
do
   for DB_BACKEND in "redis" "keydb"
   do
      for (( NX=8; NX<=256; NX=NX*2 ))
      do 
         TEST_DIR=${DB_TYPE}_${DB_BACKEND}_${NX}x${NX}x${NX}
         echo Working in $TEST_DIR
         
         if [ ! -d "$TEST_DIR" ]
         then
             echo Directory does not exist
         else
             cd $TEST_DIR
             if ls 4*/data_transfer.log 1> /dev/null 2>&1; then
                 echo "Run directories exist"
                 echo Extracting data
                 cat 4*/data_transfer.log > data_transfer.dat
             else
                 echo "Run directories don't exist yet"
                 touch data_transfer.dat
                 rm data_transfer.dat
             fi
             cd ..
             echo 
         fi 
      done
   done
done

## Loop over cases for the clustered database
DB_TYPE="cl"
for TEST_TYPE in "data_size"
do
   for DB_BACKEND in "redis" "keydb"
   do
      for (( NX=8; NX<=256; NX=NX*2 ))
      do 
         TEST_DIR=${DB_TYPE}_${DB_BACKEND}_${NX}x${NX}x${NX}
         echo Working in $TEST_DIR
         
         if [ ! -d "$TEST_DIR" ]
         then
             echo Directory does not exist
         else
             cd $TEST_DIR
             if ls 4*/data_transfer.log 1> /dev/null 2>&1; then
                 echo "Run directories exist"
                 echo Extracting data
                 cat 4*/data_transfer.log > data_transfer.dat
             else
                 echo "Run directories don't exist yet"
                 touch data_transfer.dat
                 rm data_transfer.dat
             fi
             cd ..
             echo 
         fi 
      done
   done
done
     

## Launch Python script to post-process results and create figure
python plot_data_size.py
