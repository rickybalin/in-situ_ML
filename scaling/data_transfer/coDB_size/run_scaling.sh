#!/bin/bash -e

RUN_DIR=$PWD
SAFE_DIR=$RUN_DIR
echo Running tests in $RUN_DIR
echo and grabbing sample files from $SAFE_DIR
echo 

## Loop over cases for the colocated database
DB_TYPE="co"
for TEST_TYPE in "coDB_size"
do
   for DB_BACKEND in "keydb"
   do
      for (( N=1; N<=32; N=N*2 ))
      do 
         echo Setting up colocated test with $N DB cores
         TEST_DIR=${DB_TYPE}_${DB_BACKEND}_${N}
         echo Working in $TEST_DIR

         # If directory does not exist, set it up
         echo $TEST_DIR
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
            sed -i "s/DBPROCS_REPLACE/$N/g" config.yaml
            cd ..

            # Copy driver
            cp $SAFE_DIR/src/driver.py .
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

