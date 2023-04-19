# Weak Scaling of Send/Retrieve Operations
This artifact reproduces Figure 8 in the paper.


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
Since this experiment involves running on multiple nodes of Polaris (up to 448), a number of jobs must be submitted to the queue.
To do so, execute the bash scripts
```
./launch_scaling_coDB.sh
```
and
```
./launch_scaling_clDB.sh
```
 which will configure the run and submit a job. The scrips submit jobs for the co-located and clustered deployment, respectively. Note that the project name in the `submit_polaris.sh` script must be changed to a valid allocation and that the script assumes the Conda env was installed according to the instructions in the [README](../../../README.md) file.
 The output of each run is contained in the `data_transfer.log` file and is located in a directory with the name of the job ID within each of the run directories. 
 The output consists of the time, measured in seconds, taken to perform the data send, model evaluation and data retrieve operations by each rank on each loop iteration.
 
 
 In order to gather more data for this experiment, execute the launch scripts again.
 
 ## Post-process the output
 By executing the script
 ```
 ./extract_scaling.sh
 ```
 the outputs from each run of a particular configuration are collected into a single file called `data_transfer.dat` and then the Python script `plot_inference_scale.py` is executed. 
 This Python script computes statistics on the output data and generates the plot of interest, saving it as a `.png` file.
 
