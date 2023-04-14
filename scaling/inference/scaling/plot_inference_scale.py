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
class inference_class:
    def __init__(self,n_db,n_backend,n_test,store_all_data=False):
        self.n_db = n_db
        self.n_bknd = n_backend
        self.n_sizes = n_test
        self.mean = np.zeros((n_db,n_backend,n_test,4))
        self.std = np.zeros((n_db,n_backend,n_test,4))
        self.max = np.zeros((n_db,n_backend,n_test,4))
        self.min = np.zeros((n_db,n_backend,n_test,4))
        self.median = np.zeros((n_db,n_backend,n_test,4))
        self.store_all_data = store_all_data
        self.all_data = None
        self.all_data_initialize = False
        
    def compute_stats(self,data,idb,ibknd,isize):
        self.mean[idb,ibknd,isize,:] = np.mean(data, axis=0)
        self.std[idb,ibknd,isize,:] = np.std(data, axis=0)
        self.max[idb,ibknd,isize,:] = np.amax(data, axis=0)
        self.min[idb,ibknd,isize,:] = np.amin(data, axis=0)
        self.median[idb,ibknd,isize,:] = np.median(data, axis=0)
        
    def get_inference_data(self,fname,idb,ibknd,isize):
        if (os.path.exists(fname)):
            fh = open(fname, 'r')
            run_data = np.genfromtxt(fh)
            fh.close()
            run_data = np.hstack((run_data,np.sum(run_data,axis=1,keepdims=True)))
            if self.store_all_data:
                if not self.all_data_initialize:
                    nsamples = run_data.shape[0]
                    self.all_data = np.zeros((self.n_db,self.n_bknd,self.n_sizes,nsamples,3))
                    self.all_data_initialize = True
                self.all_data[idb,ibknd,isize,:,:] = run_data
            self.compute_stats(run_data,idb,ibknd,isize)
        else:
            print(f"ERROR: file not found at {fname}")


# Define the cases run and file path
scale_type = "weak"
databases = ["co", "cl"]
backends = ["redis"]
fname = "data_transfer.dat"
coDB_node_list = [1, 4, 16, 64, 256, 448]
test_dir = "_".join([scale_type,databases[0],backends[0],str(coDB_node_list[0])])
fpath = "/".join([base_dir,test_dir,fname])
print(f'Looking for data at the example path: \n{fpath}\n')

# Loop over runs and compute statistics
# Colocated DB
databases = ["co"]
coDBWeak = inference_class(1,len(backends),len(coDB_node_list),store_all_data=False)
for idb in range(len(databases)):
    for ibknd in range(len(backends)):
        for isize in range(len(coDB_node_list)):
            test_dir = "_".join([scale_type,databases[idb],backends[ibknd],str(coDB_node_list[isize])])
            fpath = "/".join([base_dir,test_dir,fname])
            coDBWeak.get_inference_data(fpath,idb,ibknd,isize)
print(f'Example means: {coDBWeak.mean[0,0,:,0]}\n')



scale_type = "strong"
coDBStrong = inference_class(1,len(backends),len(coDB_node_list),store_all_data=False)
for idb in range(len(databases)):
    for ibknd in range(len(backends)):
        for isize in range(len(coDB_node_list)):
            test_dir = "_".join([scale_type,databases[idb],backends[ibknd],str(coDB_node_list[isize])])
            fpath = "/".join([base_dir,test_dir,fname])
            coDBStrong.get_inference_data(fpath,idb,ibknd,isize)
print(f'Example means: {coDBStrong.mean[0,0,:,0]}\n')



# Plot data send time and receive for colocated DB
x_simNodes = coDB_node_list
x_simRanks = [i*24 for i in x_simNodes]
fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))

axs[0].errorbar(x_simRanks, coDBWeak.mean[0,0,:,1], coDBWeak.std[0,0,:,1], 
                          fmt='^--', linewidth=2, capsize=6, markersize=7, label='Model evaluation')
axs[0].errorbar(x_simRanks, coDBWeak.mean[0,0,:,3], coDBWeak.std[0,0,:,3], 
                          fmt='^--', linewidth=2, capsize=6, markersize=7, label='Total inference')
line = [(coDBWeak.mean[0,0,0,1]/2) for i in x_simNodes]
axs[0].plot(x_simRanks, line, 'k:', linewidth=2, label='Perfect Scaling')

axs[1].errorbar(x_simRanks, coDBStrong.mean[0,0,:,1], coDBStrong.std[0,0,:,1], 
                          fmt='^--', linewidth=2, capsize=6, markersize=7, label='Model evaluation')
axs[1].errorbar(x_simRanks, coDBStrong.mean[0,0,:,3], coDBStrong.std[0,0,:,3], 
                          fmt='^--', linewidth=2, capsize=6, markersize=7, label='Total infernece')
line = [(coDBStrong.mean[0,0,0,3]*2)/i for i in x_simNodes]
axs[1].plot(x_simRanks, line, 'k:', linewidth=2, label='Perfect Scaling')

axs[0].set_yscale("log")
axs[0].set_xscale("log")
axs[0].grid()
axs[0].set_ylim(bottom=5.0e-3, top=1.0e0)

axs[1].set_yscale("log")
axs[1].set_xscale("log")
axs[1].grid()
axs[1].set_ylim(bottom=1.0e-3, top=20.0e0)
#axs[icol,ibck].set_xlim(left=0.5, right=1.0e3)


fig.tight_layout(pad=3.0)
axs[0].set_ylabel('Time [sec]')
axs[0].set_xlabel('Number of Simulation Ranks')
axs[0].set_title('Weak Scaling')
axs[0].legend()
axs[1].set_ylabel('Time [sec]')
axs[1].set_xlabel('Number of Simulation Ranks')
axs[1].set_title('Strong Scaling')
axs[1].legend()

fig_name = base_dir+"/"+"inference_scale_ranks.png"
plt.savefig(fig_name, dpi='figure', format="png")

