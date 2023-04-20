#!/bin/bash

runtime=01:00:00
project=PROJECT_NAME
queue=debug

qsub -I -l select=1:ncpus=64:ngpus=4,walltime=$runtime,filesystems=home:eagle:grand -q $queue -A $project
