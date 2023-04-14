#!/bin/bash

CC=cc
CXX=CC
FC=ftn

export CUDNN_LIBRARY_PATH=/soft/libraries/cudnn/cudnn-11.6-linux-x64-v8.4.1.50/lib
export CUDNN_INCLUDE_PATH=/soft/libraries/cudnn/cudnn-11.6-linux-x64-v8.4.1.50/include
export PATH=$PATH:$CUDNN_LIBRARY_PATH:$CUDNN_INCLUDE_PATH
export LIBRARY_PATH=/soft/datascience/conda/2022-09-08/mconda3/lib

cmake \
-DCMAKE_Fortran_FLAGS="-g -fallow-argument-mismatch" \
-DCMAKE_CXX_FLAGS="-g" \
-DCMAKE_C_FLAGS="-g" \
-DCMAKE_PREFIX_PATH=`python -c 'import torch;print(torch.utils.cmake_prefix_path)'` \
./

make


#-DCMAKE_PREFIX_PATH=`python -c 'import torch;print(torch.utils.cmake_prefix_path)'` \
#-DCMAKE_PREFIX_PATH=/soft/datascience/conda/2022-09-08/mconda3/lib/python3.8/site-packages/torch/share/cmake \
