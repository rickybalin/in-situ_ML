#!/bin/bash -e

RUN_DIR=$PWD
SAFE_DIR=$RUN_DIR
echo Running tests in $RUN_DIR
echo and grabbing sample files from $SAFE_DIR
echo 

## Loop over cases for the clustered database
DB_TYPE="cl"
NY_MAX=$(( 64*256 ))
for TEST_TYPE in "weak"
do
   for DB_BACKEND in "keydb"
   do
      for (( NDB=1; NDB<=64; NDB=NDB*4 ))
      do 
         for (( NSIM=NDB; NSIM<=NDB*64; NSIM=NSIM*4 ))
         do
            # Change nude number for largest run, set to 448 nodes
            if [ $NSIM -gt 300  ]
            then
               NSIM=448
            fi
         
            NTOT=$(( NDB+NSIM ))
            echo Clustered test with $NDB DB nodes,
            echo with $NSIM simulation nodes and $NTOT total nodes
            TEST_DIR=${TEST_TYPE}_${DB_TYPE}_${DB_BACKEND}_${NDB}_${NSIM}
            echo Working in $TEST_DIR
            
            # If directory does not exist, set it up
            if [ ! -d "$TEST_DIR" ]
            then
               echo Setting up input files
               mkdir $TEST_DIR; cd $TEST_DIR
               NPROCS=$(( 24*NSIM ))
               echo Client running with $NPROCS processes

               # Copy and update submit script
               cp $SAFE_DIR/submit_polaris.sh .
               sed -i "s/NODES_REPLACE/$NTOT/" submit_polaris.sh
               if [ $NTOT -lt 11 ]
               then
                  sed -i "s/QUEUE_REPLACE/debug-scaling/" submit_polaris.sh
               else
                  sed -i "s/QUEUE_REPLACE/prod/" submit_polaris.sh
               fi

               # Copy and update the config file
               mkdir conf; cd conf
               cp $SAFE_DIR/conf/config_clustered.yaml config.yaml
               sed -i "s/BACKEND_REPLACE/$DB_BACKEND/" config.yaml
               sed -i "s/NODES_REPLACE/$NTOT/" config.yaml
               sed -i "s/DB_REPLACE/$NDB/" config.yaml
               sed -i "s/SIM_REPLACE/$NSIM/" config.yaml
               sed -i "s/PROCS_REPLACE/$NPROCS/" config.yaml
               if [ $TEST_TYPE = "strong" ]
               then
                  if [ $NSIM -gt 300  ]
                  then
                     NY=$(( NY*4/7 ))
                  else
                     NY=$(( NY_MAX/NSIM ))
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
            if [ $NTOT -lt 11 ]
            then
               #echo Not submitting job due to queue limitations
               cd ..
               echo 
            elif [ $NTOT -gt 464 ]
            then
               echo Job is too big, not submitting
               cd ..
               rm -r $TEST_DIR
               echo 
               break
            else
               echo Submitting jobs
               qsub submit_polaris.sh
               cd ..
               echo 
            fi
         done
      done
   done
done


