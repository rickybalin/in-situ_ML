# Single Node Inference with LibTorch
This artifact reproduces Figure 7 in the paper.


## Build the source code
To build the Fortran simulation reproducer, execute
```
cd src
./clean.sh
source env.sh
./doConfig.sh
```

## Generate a Traced Version of the ResNet50 Model
The inference test requires a jit-traced version of the ResNet50 model. This is done using TorchScript and executing the following
```
module load conda/2022-09-08
conda activate base
python resnet50_trace.py
```
which produces the model `resnet50_jit.pt`. This model is the loaded onto the database and used for inference during the experiment.

## Run the experiment
First, submit an interactive job to get a compute node on Polaris. This is done by executing
```
./subInteractive.sh
```
 noting that the project name must be changed to a valid allocation.
 
 Second, run the experiment executing
 ```
 ./run_scaling_torch.sh
 ```
 This bash script creates and configures a new directory for each run of the experiment and executes the run by launching `run_polaris.sh` within these directories.
 The output of each run is contained in the `data_transfer.log` file and is located in a directory with the name of the job ID within each of the run directories. 
 The output consists of the time, measured in seconds, taken to perform model inference by each rank on each loop iteration.
 
 
 In order to gather more data for this experiment, exit the interactive job and repeat the steps above.
 
 ## Post-process the output
 By executing the script
 ```
 ./extract_scaling.sh
 ```
 the outputs from each run of a particular configuration are collected into a single file called `data_transfer.dat`.
 Note that a plot is not produced by executing this script, instead the data from this experiment is plotted together with the [single node experiment with smartsim](../single_node_smartsim/extract_scaling.sh) in order to compare the two approaches.
 
 
