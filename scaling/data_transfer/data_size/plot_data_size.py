import os
import pathlib
import matplotlib
from matplotlib import pyplot as plt
import numpy as np

font = {
        'weight' : 'normal',
        'size'   : 20}

matplotlib.rc('font', **font)
matplotlib.rc('text', usetex=False)

import matplotlib.font_manager

base_dir = "."

# Create a class that contains all statistics for all runs
class data_transfer_class:
    def __init__(self,n_db,n_backend,n_test,store_all_data=False):
        self.n_db = n_db
        self.n_bknd = n_backend
        self.n_sizes = n_test
        self.mean = np.full([n_db,n_backend,n_test,2], np.nan)
        self.std = np.full([n_db,n_backend,n_test,2], np.nan)
        self.max = np.full([n_db,n_backend,n_test,2], np.nan)
        self.min = np.full([n_db,n_backend,n_test,2], np.nan)
        self.median = np.full([n_db,n_backend,n_test,2], np.nan)
        self.mean_tp = np.full([n_db,n_backend,n_test,2], np.nan)
        self.std_tp = np.full([n_db,n_backend,n_test,2], np.nan)
        self.max_tp = np.full([n_db,n_backend,n_test,2], np.nan)
        self.min_tp = np.full([n_db,n_backend,n_test,2], np.nan)
        self.median_tp = np.full([n_db,n_backend,n_test,2], np.nan)
        self.store_all_data = store_all_data
        self.all_data = None
        self.all_data_initialize = False
        
    def compute_stats(self,data,idb,ibknd,isize):
        self.mean[idb,ibknd,isize,:] = np.mean(data, axis=0)
        self.std[idb,ibknd,isize,:] = np.std(data, axis=0)
        self.max[idb,ibknd,isize,:] = np.amax(data, axis=0)
        self.min[idb,ibknd,isize,:] = np.amin(data, axis=0)
        self.median[idb,ibknd,isize,:] = np.median(data, axis=0)
        
    def compute_stats_throughput(self,data,idb,ibknd,isize):
        self.mean_tp[idb,ibknd,isize,:] = np.mean(data, axis=0)
        self.std_tp[idb,ibknd,isize,:] = np.std(data, axis=0)
        self.max_tp[idb,ibknd,isize,:] = np.amax(data, axis=0)
        self.min_tp[idb,ibknd,isize,:] = np.amin(data, axis=0)
        self.median_tp[idb,ibknd,isize,:] = np.median(data, axis=0)
        
    def get_data_transfer_data(self,fname,idb,ibknd,isize):
        if (os.path.exists(fname)):
            fh = open(fname, 'r')
            run_data = np.genfromtxt(fh)
            fh.close()
            if self.store_all_data:
                if not self.all_data_initialize:
                    nsamples = run_data.shape[0]
                    self.all_data = np.zeros((self.n_db,self.n_bknd,self.n_sizes,nsamples,2))
                    self.all_data_initialize = True
                self.all_data[idb,ibknd,isize,:,:] = run_data
            self.compute_stats(run_data,idb,ibknd,isize)
        else:
            print(f"ERROR: file not found at {fname}")
            
    def get_throughput_data(self,fname,idb,ibknd,isize,data_size):
        if (os.path.exists(fname)):
            fh = open(fname, 'r')
            run_data = np.genfromtxt(fh)
            fh.close()
            run_data = data_size / run_data
            self.compute_stats_throughput(run_data,idb,ibknd,isize)
        else:
            print(f"ERROR: file not found at {fname}")


# Define the cases run and file path
databases = ["co", "cl"]
backends = ["redis", "keydb"]
fname = "data_transfer.dat"
data_size_list = [8, 16, 32, 64, 128, 256]
array_size = "x".join([str(data_size_list[0]),str(data_size_list[0]),str(data_size_list[0])])
test_dir = "_".join([databases[0],backends[0],array_size])
fpath = "/".join([base_dir,test_dir,fname])
print(f'Looking for dara at the example path: \n{fpath}\n')
DataSize = data_transfer_class(len(databases),len(backends),len(data_size_list),store_all_data=False)

# Loop over runs and compute statistics
data_size = [i**3*8/1024/1024 for i in data_size_list]
for idb in range(len(databases)):
    for ibknd in range(len(backends)):
        for isize in range(len(data_size_list)):
            array_size = "x".join([str(data_size_list[isize]),str(data_size_list[isize]),str(data_size_list[isize])])
            test_dir = "_".join([databases[idb],backends[ibknd],array_size])
            fpath = "/".join([base_dir,test_dir,fname])
            DataSize.get_data_transfer_data(fpath,idb,ibknd,isize)
            DataSize.get_throughput_data(fpath,idb,ibknd,isize,data_size[isize])
            
print(f'Example means: {DataSize.mean[0,0,:,0]}')


# Plot data send and receive time for 4 combinations
x_plt = [i**3*8/1024/1024 for i in data_size_list]
labels = [['Redis: Send','Redis: Receive'],['KeyDB: Send','KeyDB: Receive']]
labels = ['Redis','KeyDB']
titles = [['Co-Located DB: Send','Co-Located DB: Receive'],['Clustered DB: Send','Clustered DB: Receive']]
fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(15, 10))

axs[0,0].errorbar(x_plt, DataSize.mean[0,0,:,0], DataSize.std[0,0,:,0], 
                          fmt='o-', linewidth=2, capsize=6, markersize=7, label=labels[0])
axs[0,0].errorbar(x_plt, DataSize.mean[0,1,:,0], DataSize.std[0,1,:,0], 
                          fmt='s--', linewidth=2, capsize=6, markersize=7, label=labels[1])

axs[0,1].errorbar(x_plt, DataSize.mean[0,0,:,1], DataSize.std[0,0,:,1], 
                          fmt='o-', linewidth=2, capsize=6, markersize=7, label=labels[0])
axs[0,1].errorbar(x_plt, DataSize.mean[0,1,:,1], DataSize.std[0,1,:,1], 
                          fmt='s--', linewidth=2, capsize=6, markersize=7, label=labels[1])

axs[1,0].errorbar(x_plt, DataSize.mean[1,0,:,0], DataSize.std[1,0,:,0], 
                          fmt='o-', linewidth=2, capsize=6, markersize=7, label=labels[0])
axs[1,0].errorbar(x_plt, DataSize.mean[1,1,:,0], DataSize.std[1,1,:,0], 
                          fmt='s--', linewidth=2, capsize=6, markersize=7, label=labels[1])

axs[1,1].errorbar(x_plt, DataSize.mean[1,0,:,1], DataSize.std[1,0,:,1], 
                          fmt='o-', linewidth=2, capsize=6, markersize=7, label=labels[0])
axs[1,1].errorbar(x_plt, DataSize.mean[1,1,:,1], DataSize.std[1,1,:,1], 
                          fmt='s--', linewidth=2, capsize=6, markersize=7, label=labels[1])

        
fig.tight_layout(pad=3.0)
for i in range(2):
    for j in range(2):
        axs[i,j].grid()
        axs[i,j].set_yscale("log")
        axs[i,j].set_xscale("log")
        axs[i,j].set_ylim(bottom=1.0e-5, top=1e1)
        axs[i,j].set_ylabel('Time [sec]')
        axs[i,j].set_xlabel('Data Size [MB]')
        axs[i,j].set_title(titles[i][j])
        axs[i,j].legend()
        
fig_name = base_dir+"/"+"dataSize_time.png"
plt.savefig(fig_name, dpi='figure', format="png")


# Plot data send and receive time for 4 combinations
x_plt = [i**3*8/1024/1024 for i in data_size_list]
labels = [['Redis: Send','Redis: Receive'],['KeyDB: Send','KeyDB: Receive']]
labels = ['Redis','KeyDB']
titles = [['Co-Located DB: Send','Co-Located DB: Receive'],['Clustered DB: Send','Clustered DB: Receive']]
fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(15, 10))

axs[0,0].errorbar(x_plt, DataSize.mean_tp[0,0,:,0], DataSize.std_tp[0,0,:,0], 
                          fmt='o-', linewidth=2, capsize=6, markersize=7, label=labels[0])
axs[0,0].errorbar(x_plt, DataSize.mean_tp[0,1,:,0], DataSize.std_tp[0,1,:,0], 
                          fmt='s--', linewidth=2, capsize=6, markersize=7, label=labels[1])

axs[0,1].errorbar(x_plt, DataSize.mean_tp[0,0,:,1], DataSize.std_tp[0,0,:,1], 
                          fmt='o-', linewidth=2, capsize=6, markersize=7, label=labels[0])
axs[0,1].errorbar(x_plt, DataSize.mean_tp[0,1,:,1], DataSize.std_tp[0,1,:,1], 
                          fmt='s--', linewidth=2, capsize=6, markersize=7, label=labels[1])

axs[1,0].errorbar(x_plt, DataSize.mean_tp[1,0,:,0], DataSize.std_tp[1,0,:,0], 
                          fmt='o-', linewidth=2, capsize=6, markersize=7, label=labels[0])
axs[1,0].errorbar(x_plt, DataSize.mean_tp[1,1,:,0], DataSize.std_tp[1,1,:,0], 
                          fmt='s--', linewidth=2, capsize=6, markersize=7, label=labels[1])

axs[1,1].errorbar(x_plt, DataSize.mean_tp[1,0,:,1], DataSize.std_tp[1,0,:,1], 
                          fmt='o-', linewidth=2, capsize=6, markersize=7, label=labels[0])
axs[1,1].errorbar(x_plt, DataSize.mean_tp[1,1,:,1], DataSize.std_tp[1,1,:,1], 
                          fmt='s--', linewidth=2, capsize=6, markersize=7, label=labels[1])

        
fig.tight_layout(pad=3.0)
for i in range(2):
    for j in range(2):
        axs[i,j].grid()
        axs[i,j].set_yscale("log")
        axs[i,j].set_xscale("log")
        axs[i,j].set_ylim(bottom=2., top=1e3)
        axs[i,j].set_ylabel('Throughput [MB/sec]')
        axs[i,j].set_xlabel('Data Size [MB]')
        axs[i,j].set_title(titles[i][j])
        axs[i,j].legend()
        
fig_name = base_dir+"/"+"dataSize_throughput.png"
plt.savefig(fig_name, dpi='figure', format="png")








