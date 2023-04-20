#!/bin/bash -e

module load conda/2022-09-08
conda activate ../../../installation/ssim

RUN_DIR=$PWD
SAFE_DIR=$RUN_DIR
echo Running tests in $RUN_DIR
echo and grabbing sample files from $SAFE_DIR
echo 

## Loop over cases for the colocated database
## to extract and concatenate data
DB_TYPE="co"
for DB_BACKEND in "redis"
do
   for (( B=1; B<=16; B=B*4 ))
   do
      for (( N=4; N<=4; N=N*2 ))
      do 
         TEST_DIR=${DB_TYPE}_${DB_BACKEND}_${B}_${N}
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
python plot_inference_comparison.py

