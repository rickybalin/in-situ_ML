#!/bin/bash

runtime=01:00:00
project=PROJECT_NAME
queue=debug
#queue=debug-scaling
#queue=preemptable
nodes=2

qsub -I -l select=$nodes:ncpus=64:ngpus=4,walltime=$runtime,filesystems=home:eagle:grand -q $queue -A $project
