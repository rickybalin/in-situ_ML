#!/bin/bash -e

DRIVER=./driver.py
MODULE=conda/2022-09-08
CONDA_ENV=/lus/grand/projects/datascience/balin/SC23/in-situ_ML/installation/ssim
LOGGING="verbose-perf"

# Set env
module load $MODULE
conda activate $CONDA_ENV
export MPICH_GPU_SUPPORT_ENABLED=1
export SR_LOG_FILE=stdout
export SR_LOG_LEVEL=QUIET
export SR_CONN_INTERVAL=10 # default is 1000 ms
export SR_CONN_TIMEOUT=1000 # default is 100 ms
export SR_CMD_INTERVAL=10 # default is 1000 ms
export SR_CMD_TIMEOUT=1000 # default is 100 ms
export SR_THREAD_COUNT=4 # default is 4
HOST_FILE=$(echo $PBS_NODEFILE)

# Run
echo python $DRIVER
python $DRIVER

# Handle output
JOBID=$(echo $PBS_JOBID | awk '{split($1,a,"."); print a[1]}')
if [ $LOGGING = "verbose-perf" ]; then
    mkdir $JOBID
    mv *.log $JOBID
    mv client.* $JOBID
    cp conf/config.yaml $JOBID/config.yaml
fi
