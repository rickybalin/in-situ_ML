#!/bin/bash

CC=cc
CXX=CC
FC=ftn

cmake \
-DCMAKE_Fortran_FLAGS="-O3 -fallow-argument-mismatch" \
-DCMAKE_CXX_FLAGS="-O3" \
-DCMAKE_C_FLAGS="-O3" \
-DSSIMLIB=../../../../installation/SmartRedis \
./

make
