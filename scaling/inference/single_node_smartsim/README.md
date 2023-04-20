# Single Node Inference with SmartSim
This artifact reproduces Figure 7 in the paper.


## Build the source code
To build the Fortran simulation reproducer, execute
```
cd src
./clean.sh
source env.sh
./doConfig.sh
```

Note that the `doConfig.sh` script points to the SmartRedis library at the relative path `../../../../installation/SmartRedis`, therefore assumes that the software stack for these experiments was installed according to the [README](../../../README.md) instructions. The same is true for the `env.sh` script. Both scripts need to be updated if the Conda env is installed in another directory.

## Generate a Traced Version of the ResNet50 Model
The inference test requires a jit-traced version of the ResNet50 model. This is done using TorchScript and executing the following
```
module load conda/2022-09-08
conda activate /path/to/installation/ssim
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
 ./run_scaling.sh
 ```
 This bash script creates and configures a new directory for each run of the experiment and executes the run by launching `run_polaris.sh` within these directories.
 Note that the `run_polaris.sh` script assumes the Conda env was installed according to the instructions in the [README](../../../README.md) file.
 The output of each run is contained in the `data_transfer.log` file and is located in a directory with the name of the job ID within each of the run directories. 
 The output consists of the time, measured in seconds, taken to perform the data send, model evaluation and data retrieve operations by each rank on each loop iteration.
 
 
 In order to gather more data for this experiment, exit the interactive job and repeat the steps above.
 
 ## Post-process the output
 By executing the script
 ```
 ./extract_scaling.sh
 ```
 the outputs from each run of a particular configuration are collected into a single file called `data_transfer.dat` and then the Python script `plot_inference_comparison.py` is executed. 
 This Python script computes statistics on the output data and generates the plot of interest, saving it as a `.png` file. 
 Note that this script also looks for the output data of the [single node experiments with LibTorch](../single_node_torch) to generage Figure 7 in the paper. 
 
