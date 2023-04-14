#!/bin/bash -e

RANKS=24
PPN=24
NGPU=NGPU_REPLACE
LOGGING="verbose-perf"

# Set env
module load conda/2022-09-08
conda activate base
HOST_FILE=$(echo $PBS_NODEFILE)
export LD_LIBRARY_PATH=/soft/datascience/conda/2022-09-08/mconda3/lib:$LD_LIBRARY_PATH

# Run
echo 3 > input.config
echo $PPN $NGPU 1 >> input.config
echo BATCH_REPLACE 3 224 >> input.config
echo mpiexec --np $RANKS --ppn $PPN ../safe/src/clientFtn.exe
mpiexec --np $RANKS --ppn $PPN ../src/clientFtn.exe 2>&1 | tee torch_inf.out

# Handle output
JOBID=$(echo $PBS_JOBID | awk '{split($1,a,"."); print a[1]}')
if [ $LOGGING = "verbose-perf" ]; then
    mkdir $JOBID
    mv torch_inf.out $JOBID
    mv *.log $JOBID
    mv input.config $JOBID
fi
