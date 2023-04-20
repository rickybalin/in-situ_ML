#!/bin/bash -e

module load conda/2022-09-08
conda activate ../../../installation/ssim

RUN_DIR=$PWD
SAFE_DIR=$RUN_DIR
echo Running tests in $RUN_DIR
echo and grabbing sample files from $SAFE_DIR
echo 

## Loop over cases for the colocated database
DB_TYPE="co"
for DB_BACKEND in "redis"
do
   for (( B=1; B<=16; B=B*4 ))
   do
      for (( N=4; N<=4; N=N*2 ))
      do 
         echo Setting up colocated test with batch size $B and $N GPU
         TEST_DIR=${DB_TYPE}_${DB_BACKEND}_${B}_${N}
         echo Working in $TEST_DIR

         # If directory does not exist, set it up
         if [ ! -d "$TEST_DIR" ]
         then
            echo Setting up input files
            mkdir $TEST_DIR; cd $TEST_DIR

            # Copy and update submit script
            cp $SAFE_DIR/run_polaris.sh .

            # Copy and update the config file
            mkdir conf; cd conf
            cp $SAFE_DIR/conf/config_colocated.yaml config.yaml
            sed -i "s/BACKEND_REPLACE/$DB_BACKEND/" config.yaml
            sed -i "s/DEVICES_REPLACE/$N/g" config.yaml
            BATCH=$(( 24/N ))
            sed -i "s/BATCH_REPLACE/$BATCH/g" config.yaml
            sed -i "s/SAMPLES_REPLACE/$B/g" config.yaml
            cd ..

            # Copy driver
            cp $SAFE_DIR/src/driver.py .
            
            # Copy model
            ln -s $SAFE_DIR/resnet50_jit.pt .
            cd ..
         else
            echo Test already set up
         fi

         # Submit job
         cd $TEST_DIR
         echo Running job
         ./run_polaris.sh
         cd ..
         echo 
   
      done
   done
done

