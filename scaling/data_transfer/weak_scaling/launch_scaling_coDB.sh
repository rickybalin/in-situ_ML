#!/bin/bash -e

RUN_DIR=$PWD
SAFE_DIR=$RUN_DIR
echo Running tests in $RUN_DIR
echo and grabbing sample files from $SAFE_DIR
echo 

## Loop over cases for the colocated database
DB_TYPE="co"
NY_MAX=$(( 64*256 ))
for TEST_TYPE in "weak"
do
   for DB_BACKEND in "redis" "keydb"
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
            mkdir $TEST_DIR; cd $TEST_DIR
            NPROCS=$(( 24*N ))
            echo Client running with $NPROCS processes

            # Copy and update submit script
            cp $SAFE_DIR/submit_polaris.sh .
            sed -i "s/NODES_REPLACE/$N/" submit_polaris.sh
            if [ $N -lt 11 ]
            then
               sed -i "s/QUEUE_REPLACE/debug-scaling/" submit_polaris.sh
            else
               sed -i "s/QUEUE_REPLACE/prod/" submit_polaris.sh
            fi

            # Copy and update the config file
            mkdir conf; cd conf
            cp $SAFE_DIR/conf/config_colocated.yaml config.yaml
            sed -i "s/BACKEND_REPLACE/$DB_BACKEND/" config.yaml
            sed -i "s/NODES_REPLACE/$N/" config.yaml
            sed -i "s/PROCS_REPLACE/$NPROCS/" config.yaml
            if [ $TEST_TYPE = "strong" ]
            then
               if [ $N -gt 300  ]
               then
                  NY=$(( NY*4/7 ))
               else
                  NY=$(( NY_MAX/N ))
               fi
               sed -i "s/NY_REPLACE/$NY/" config.yaml
            else
               sed -i "s/NY_REPLACE/32/" config.yaml
            fi
            cd ..

            # Copy driver
            cp $SAFE_DIR/src/driver.py .
            cd ..
         else
            echo Test already set up, submitting new run
         fi

         # Submit job
         cd $TEST_DIR
         if [ $N -lt 11 ]
         then
            #echo Not submitting job due to queue limitations
            echo Submitting jobs
            qsub submit_polaris.sh
            cd ..
            echo 
         else
            echo Submitting jobs
            qsub submit_polaris.sh
            cd ..
            echo 
         fi
   
      done
   done
done

