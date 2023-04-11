# In Situ Framework for Coupling Simulation and Machine Learning with Application to CFD

This repository contains the artifacts created for an SC23 paper submission presenting a framework for scalable in situ ML for CFD simulations.
The artifacts were run on the Polaris supercomputer at the Argonne Leadership Computing Facility (ALCF).
Follow the instructions below to run the artifacts on Polaris and reproduce the results.

## Software Installation
First, build the Conda environment needed to run the framework.
Move to the [installation directory](./installation) and submit and interactive job to obtain a compute node with
```
./subInteractive.sh
```
making sure to update the project name in the script.

Then, from the [installation directory](./installation), run the build script with
```
source build_SSIM_Polaris.sh
```
to create a new Conda environment with all the dependencies needed by the framework.
This operation takes approximately 10 minutes to complete.

You can load the Conda environment with 
```
conda activate /path/to/installation_directory/ssim
```


## Souce Code Description


## Launching the Artifacts and Processing Output Data


## The QuadConv Autoencoeder Model


