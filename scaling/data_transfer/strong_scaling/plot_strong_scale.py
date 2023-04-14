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
scale_type = "strong"
databases = ["co"]
backends = ["redis"]
fname = "data_transfer.dat"
coDB_node_list = [1, 4, 16, 64, 256, 448]
test_dir = "_".join([scale_type,databases[0],backends[0],str(coDB_node_list[0])])
fpath = "/".join([base_dir,test_dir,fname])
print(f'Looking for dara at the example path: \n{fpath}\n')
coDBStrong = data_transfer_class(1,len(backends),len(coDB_node_list),store_all_data=False)

# Loop over runs and compute statistics
# Colocated DB
for idb in range(len(databases)):
    for ibknd in range(len(backends)):
        for isize in range(len(coDB_node_list)):
            test_dir = "_".join([scale_type,databases[idb],backends[ibknd],str(coDB_node_list[isize])])
            fpath = "/".join([base_dir,test_dir,fname])
            coDBStrong.get_data_transfer_data(fpath,idb,ibknd,isize)
            
print(f'Example means: {coDBStrong.mean[0,0,:,0]}')

# Plot data send time and receive for colocated DB
x_simNodes = coDB_node_list
x_simRanks = [i*24 for i in x_simNodes]
line = [(coDBStrong.mean[0,0,0,0]*2)/i for i in x_simNodes]
fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(9, 6))

axs.errorbar(x_simRanks, coDBStrong.mean[0,0,:,0], coDBStrong.std[0,0,:,0], 
                          fmt='o-', linewidth=2, capsize=6, markersize=7, label='Send')
axs.errorbar(x_simRanks, coDBStrong.mean[0,0,:,1], coDBStrong.std[0,0,:,1], 
                          fmt='^--', linewidth=2, capsize=6, markersize=7, label='Receive')
axs.plot(x_simRanks, line, 'k:', linewidth=2, label='Perfect Scaling')

axs.set_yscale("log")
axs.set_xscale("log")
axs.grid()
axs.set_ylim(bottom=1.0e-3, top=5.0e0)
#axs[icol,ibck].set_xlim(left=0.5, right=1.0e3)


fig.tight_layout(pad=3.0)
axs.set_ylabel('Time [sec]')
axs.set_xlabel('Number of Simulation Ranks')
axs.set_title('Redis Co-Located DB')
axs.legend()

fig_name = base_dir+"/"+"dataTransfer_strongScale_ranks.png"
plt.savefig(fig_name, dpi='figure', format="png")


