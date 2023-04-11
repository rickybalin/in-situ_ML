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
databases = ["co"]
backends = ["redis", "keydb"]
fname = "data_transfer.dat"
coDB_size_list = [1, 2, 4, 8, 16, 32]
test_dir = "_".join([databases[0],backends[0],str(coDB_size_list[0])])
fpath = "/".join([base_dir,test_dir,fname])
print(f'Looking for dara at the example path: \n{fpath}\n')
coDBSize = data_transfer_class(len(databases),len(backends),len(coDB_size_list),store_all_data=False)

# Loop over runs and compute statistics
for idb in range(len(databases)):
    for ibknd in range(len(backends)):
        for isize in range(len(coDB_size_list)):
            test_dir = "_".join([databases[idb],backends[ibknd],str(coDB_size_list[isize])])
            fpath = "/".join([base_dir,test_dir,fname])
            coDBSize.get_data_transfer_data(fpath,idb,ibknd,isize)
            
print(f'Example means: {coDBSize.mean[0,0,:,0]}')

# Plot data send time for 4 combinations
x_plt = coDB_size_list
#labels = [['Redis: Send','Redis: Receive'],['KeyDB: Send','KeyDB: Receive']]
labels = ['Redis','KeyDB']
fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))
errors = np.vstack((np.minimum(coDBSize.mean[0,0,:,0]-coDBSize.min[0,0,:,0],coDBSize.std[0,0,:,0]),
                           coDBSize.std[0,0,:,0]))
axs[0].errorbar(x_plt, coDBSize.mean[0,0,:,0], errors, 
                          fmt='o-', linewidth=2, capsize=6, markersize=7, label=labels[0])
errors = np.vstack((np.minimum(coDBSize.mean[0,1,:,0]-coDBSize.min[0,1,:,0],coDBSize.std[0,1,:,0]),
                           coDBSize.std[0,1,:,0]))
axs[0].errorbar(x_plt, coDBSize.mean[0,1,:,0], errors, 
                          fmt='s--', linewidth=2, capsize=6, markersize=7, label=labels[1])
errors = np.vstack((np.minimum(coDBSize.mean[0,0,:,1]-coDBSize.min[0,0,:,1],coDBSize.std[0,0,:,1]),
                           coDBSize.std[0,0,:,1]))
axs[1].errorbar(x_plt, coDBSize.mean[0,0,:,1], errors, 
                          fmt='o-', linewidth=2, capsize=6, markersize=7, label=labels[0])
errors = np.vstack((np.minimum(coDBSize.mean[0,1,:,1]-coDBSize.min[0,1,:,1],coDBSize.std[0,1,:,1]),
                           coDBSize.std[0,1,:,1]))
axs[1].errorbar(x_plt, coDBSize.mean[0,1,:,1], errors, 
                          fmt='s--', linewidth=2, capsize=6, markersize=7, label=labels[1])

fig.tight_layout(pad=3.0)
axs[0].grid()
axs[0].set_yscale("log")
axs[0].set_ylim(bottom=2.0e-4, top=0.3)
axs[0].set_ylabel('Time [sec]')
axs[0].set_xlabel('Logical CPU Cores')
axs[0].set_title('Data Send')
axs[0].legend()
axs[1].grid()
axs[1].set_yscale("log")
axs[1].set_ylim(bottom=2.0e-4, top=0.3)
axs[1].set_ylabel('Time [sec]')
axs[1].set_xlabel('Logical CPU Cores')
axs[1].set_title('Data Receive')
axs[1].legend()
fig_name = base_dir+"/"+"coDB_size.png"
plt.savefig(fig_name, dpi='figure', format="png")






