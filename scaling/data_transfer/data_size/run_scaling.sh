#!/bin/bash -e

RUN_DIR=$PWD
SAFE_DIR=$RUN_DIR
echo Running tests in $RUN_DIR
echo and grabbing sample files from $SAFE_DIR
echo 

## Loop over cases for the colocated database
DB_TYPE="co"
for TEST_TYPE in "data_size"
do
   for DB_BACKEND in "redis" "keydb"
   do
      for (( NX=8; NX<=256; NX=NX*2 ))
      do 
         echo Setting up colocated test with $NX nodes
         TEST_DIR=${DB_TYPE}_${DB_BACKEND}_${NX}x${NX}x${NX}
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
            sed -i "s/NX_REPLACE/$NX/g" config.yaml
            cd ..

            # Copy driver
            cp $SAFE_DIR/src/driver.py .
            cd ..
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



## Loop over cases for the clustered database
DB_TYPE="cl"
for TEST_TYPE in "data_size"
do
   for DB_BACKEND in "redis" "keydb"
   do
      for (( NX=8; NX<=256; NX=NX*2 ))
      do 
         echo Setting up clustered test with $NX nodes
         TEST_DIR=${DB_TYPE}_${DB_BACKEND}_${NX}x${NX}x${NX}
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
            cp $SAFE_DIR/conf/config_clustered.yaml config.yaml
            sed -i "s/BACKEND_REPLACE/$DB_BACKEND/" config.yaml
            sed -i "s/NX_REPLACE/$NX/g" config.yaml
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
         # Need to kill redis server manually before launching new job
         if [ $DB_BACKEND = "redis" ]
         then
            echo Killing redis server
            #pkill redis-server
         elif [ $DB_BACKEND = "keydb" ]
         then
            echo Killing keydb server
            #pkill keydb-server
         fi
         cd ..
         echo 
   
      done
   done
done




