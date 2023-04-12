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


# Create a class that contains all statistics for all runs
class torch_class:
    def __init__(self,n_db,n_backend,n_test,store_all_data=False):
        self.n_db = n_db
        self.n_bknd = n_backend
        self.n_sizes = n_test
        self.mean = np.zeros((n_db,n_backend,n_test,1))
        self.std = np.zeros((n_db,n_backend,n_test,1))
        self.max = np.zeros((n_db,n_backend,n_test,1))
        self.min = np.zeros((n_db,n_backend,n_test,1))
        self.median = np.zeros((n_db,n_backend,n_test,1))
        self.store_all_data = store_all_data
        self.all_data = None
        self.all_data_initialize = False
        
    def compute_stats(self,data,idb,ibknd,isize):
        self.mean[idb,ibknd,isize,0] = np.mean(data, axis=0)
        self.std[idb,ibknd,isize,0] = np.std(data, axis=0)
        self.max[idb,ibknd,isize,0] = np.amax(data, axis=0)
        self.min[idb,ibknd,isize,0] = np.amin(data, axis=0)
        self.median[idb,ibknd,isize,0] = np.median(data, axis=0)
        
    def get_inference_data(self,fname,idb,ibknd,isize):
        if (os.path.exists(fname)):
            fh = open(fname, 'r')
            run_data = np.genfromtxt(fh)
            fh.close()
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
databases = ["co"]
backends = ["redis"]
fname = "data_transfer.dat"
batch_list = [1, 4, 16]
gpu_list = [4]
test_dir = "_".join([databases[0],backends[0],str(batch_list[0]),str(gpu_list[0])])
fpath = "/".join([base_dir,test_dir,fname])
print(f'Looking for data at the example path: \n{fpath}\n')

ssim = inference_class(len(databases),len(backends),len(batch_list),store_all_data=False)
for idb in range(len(databases)):
    for ibknd in range(len(backends)):
        for isize in range(len(batch_list)):
            test_dir = "_".join([databases[idb],backends[ibknd],str(batch_list[isize]),str(gpu_list[0])])
            fpath = "/".join([base_dir,test_dir,fname])
            ssim.get_inference_data(fpath,idb,ibknd,isize)     
print(f'Example means: {ssim.mean[0,0,:,1]}\n')


databases = ["torch"]
backends = ["redis"]
fname = "data_transfer.dat"
test_dir = "_".join([databases[0],str(batch_list[0]),str(gpu_list[0])])
fpath = "/".join([base_dir,"../single_node_torch",test_dir,fname])
print(f'Looking for data at the example path: \n{fpath}\n')

torch = torch_class(len(databases),len(backends),len(batch_list),store_all_data=False)
for idb in range(len(databases)):
    for ibknd in range(len(backends)):
        for isize in range(len(batch_list)):
            test_dir = "_".join([databases[0],str(batch_list[isize]),str(gpu_list[0])])
            fpath = "/".join([base_dir,"../single_node_torch",test_dir,fname])
            torch.get_inference_data(fpath,idb,ibknd,isize)     
print(f'Example means: {torch.mean[0,0,:,0]}\n')


# Plot data send time and receive for colocated DB
labels = ['1', '4', '16']
x = np.arange(len(labels))  # the label locations
width = 0.2  # the width of the bars
fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(9, 7))

# Plot SmartSim inference components
send_means = [ssim.mean[:,:,0,0].item(), ssim.mean[:,:,1,0].item(), ssim.mean[:,:,2,0].item()]
send_std = [ssim.std[:,:,0,0].item(), ssim.std[:,:,1,0].item(), ssim.std[:,:,2,0].item()]
run_means = [ssim.mean[:,:,0,1].item(), ssim.mean[:,:,1,1].item(), ssim.mean[:,:,2,1].item()]
run_std = [ssim.std[:,:,0,1].item(), ssim.std[:,:,1,1].item(), ssim.std[:,:,2,1].item()]
rcv_means = [ssim.mean[:,:,0,2].item(), ssim.mean[:,:,1,2].item(), ssim.mean[:,:,2,2].item()]
rcv_std = [ssim.std[:,:,0,2].item(), ssim.std[:,:,1,2].item(), ssim.std[:,:,2,2].item()]
tot_means = [ssim.mean[:,:,0,3].item(), ssim.mean[:,:,1,3].item(), ssim.mean[:,:,2,3].item()]
tot_std = [ssim.std[:,:,0,3].item(), ssim.std[:,:,1,3].item(), ssim.std[:,:,2,3].item()]
torch_means = [torch.mean[:,:,0,0].item(), torch.mean[:,:,1,0].item(), torch.mean[:,:,2,0].item()]
torch_std = [torch.std[:,:,0,0].item(), torch.std[:,:,1,0].item(), torch.std[:,:,2,0].item()]

axs.bar(x-width/2, run_means, width, yerr=run_std, label='Model Evaluation')
axs.bar(x-width/2, send_means, width, yerr=send_std, bottom=run_means,
       label='Send')
axs.bar(x-width/2, rcv_means, width, yerr=rcv_std, bottom=[sum(x) for x in zip(run_means, send_means)],
       label='Retrieve')
axs.bar(x+width/2, torch_means, width, yerr=torch_std, label='LibTorch')
axs.set_ylabel('Time [sec]')
axs.set_xlabel('Batch Size')
#axs.set_title('Components of SmartSim Inference')
axs.set_xticks(x);axs.set_xticklabels(labels)
#axs.set_xticks(x, labels)
axs.legend()
axs.grid(axis='y')

#rects1 = ax.bar(x - width, inf_stats[:3,0], width, label='Torch', yerr=inf_stats[:3,1])
#rects2 = ax.bar(x, inf_stats[3:6,0], width, label='OpenVINO', yerr=inf_stats[3:6,1])
#ax.set_ylabel('Time [sec]')
#ax.set_title('Total inference time')
#ax.set_xticks(x, labels)
#ax.legend()

fig.tight_layout(pad=3.0)

fig_name = base_dir+"/"+"inference_components.png"
plt.savefig(fig_name, dpi='figure', format="png")

