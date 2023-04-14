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
for TEST_TYPE in "weak" "strong"
do
   for DB_BACKEND in "redis"
   do
      for (( N=1; N<=1024; N=N*4 ))
      do 
         # Change nude number for largest run, set to 448 nodes
         if [ $N -gt 300  ]
         then
            N=448
         fi
         
         echo Colocated test with $N nodes
         TEST_DIR=${TEST_TYPE}_${DB_TYPE}_${DB_BACKEND}_${N}
         echo Working in $TEST_DIR

         # If directory does not exist, set it up
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
python plot_inference_scale.py
