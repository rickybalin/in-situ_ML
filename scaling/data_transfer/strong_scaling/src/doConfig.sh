#!/bin/bash

CC=cc
CXX=CC
FC=ftn

cmake \
-DCMAKE_Fortran_FLAGS="-O0 -fallow-argument-mismatch" \
-DCMAKE_CXX_FLAGS="-O0" \
-DCMAKE_C_FLAGS="-O0" \
-DSSIMLIB=../../../../installation/SmartRedis \
./

make
