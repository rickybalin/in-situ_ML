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
This operation takes approximately 20 minutes to complete.

You can load the Conda environment with 
```
conda activate /path/to/installation_directory/ssim
```


## Source Code Description
The source code used for the various scaling tests presented in Section 3 of the paper are contained in the [scaling directory](./scaling).
Each scaling test contains directory called `src` which holds the code for the Fotran reproducer and the SmartSim driver script.
The `src` directories also contain bash scripts to setup the build environment on Polaris, configure the build and compile the code.

For example, to build the code used for the in situ inference weak and strong scaling tests (Figure 8 in the paper), execute the following steps:
- Change directory to the `src` directory for this test with `cd scaling/inference/scaling/src`
- Set the environment on a Polaris login node with `source env.sh`
- Configure and build the executable with `./doConfig.sh`. Note that this script links to the SmartRedis library built during the software installation step and assumes the directory structure set up in this repository.
- You can clean the build directory executing `./clean.sh`


## Launching the Artifacts and Processing Output Data
For each of the scaling tests in [scaling directory](./scaling) and Section 3 of the paper, this repository also contains the run, submit and post-ptocessing scripts used to generate the results and plots presented. Note these scripts include details specific to Polaris.

In the case of the single node tests exploring the impact of the co-located database size, the size of the data, and differences in performance between the proposed framework and LibTorch, the runs can be executed as follows:
- Change directory to the particular test, for example `cd scaling/data_transfer/coDB_size`
- Submit an interactive job to get a compute node with `./subInteractive.sh`. Note one will have to select an appropriate account name to run on Polaris. Additionally, note that for the test exploring the data size with a clustered database deployment, two nodes must be requested.
- Run the battery of tests with `./run_scaling.sh`. This can be run multiple times to gather data for different nodes and instances.
- Extract the data and plot it with `./extract_scaling.sh`. This produces a figure in `.png` format in the test directory.

In the other cases, which require submitting jobs to run on multiple nodes, the runs can be executed as follows:
- Change directory to the particular test, for example `cd scaling/data_transfer/weak_scaling`
- Launch the battery of tests with `./launch_scaling_coDB.sh` or `./launch_scaling_clDB.sh` for the co-located or clustered deployment of the database, respectively. These jobs are submitted to the queue and therefore will take some time to execute. Note one will have to select an appropriate account name to run on Polaris and this can be run multiple times to gather data for different instances.
- Extract the data and plot it with `./extract_scaling.sh`. This produces a figure in `.png` format in the test directory.


