#!/bin/bash 

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
NY_MAX=$(( 64*256 ))
for TEST_TYPE in "weak"
do
   for DB_BACKEND in "redis" "keydb"
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
               echo Directory does not exist
               echo 
            else
               cd $TEST_DIR
               if ls 4*/data_transfer.log 1> /dev/null 2>&1; then
                  echo "Run directories exist"
                  echo Extracting data
                  cat 4*/data_transfer.log > data_transfer.dat
                  cat 4*/loop.log > loop.dat
               else
                  echo "Run directories don't exist yet"
                  touch data_transfer.dat
                  rm data_transfer.dat
                  touch loop.dat
                  rm loop.dat
               fi
               cd ..
               echo 
            fi

            if [ $NTOT -gt 464 ]
            then
               break
            fi
         done
      done
   done
done


## Launch Python script to post-process results and create figure
python plot_weak_scale.py
