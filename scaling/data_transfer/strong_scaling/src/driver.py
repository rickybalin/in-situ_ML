# general imports
import os
import sys 
from omegaconf import DictConfig, OmegaConf
import hydra

# smartsim and smartredis imports
from smartsim import Experiment
from smartsim.settings import PalsMpiexecSettings


## Define function to parse node list
def parseNodeList(fname):
    with open(fname) as file:
        nodelist = file.readlines()
        nodelist = [line.rstrip() for line in nodelist]
        nodelist = [line.split('.')[0] for line in nodelist]
    nNodes = len(nodelist)
    return nodelist, nNodes


## Co-located DB launch
def launch_coDB(cfg, nodelist, nNodes):
    # Print nodelist
    print(f"\nRunning on {nNodes} total nodes on Polaris")
    print(nodelist, "\n")
    hosts = ','.join(nodelist)

    # Initialize the SmartSim Experiment
    PORT = cfg.database.port
    exp = Experiment(cfg.experiment.name, launcher=cfg.experiment.launcher)

    # Set the run settings, including the client executable and how to run it
    client_exe = cfg.sim.executable
    run_settings = PalsMpiexecSettings(
                   client_exe,
                   exe_args=None,
                   run_args=None,
                   env_vars=None
                   )
    run_settings.set_tasks(cfg.run_args.simprocs)
    run_settings.set_tasks_per_node(cfg.run_args.simprocs_pn)
    run_settings.set_hostlist(hosts)
    run_settings.set_cpu_binding_type(cfg.run_args.sim_cpu_bind)

    # Create the co-located database model
    colo_model = exp.create_model("client", run_settings)
    kwargs = {
        'maxclients': 100000,
        'threads_per_queue': 1, # affects inference 
        'inter_op_parallelism': 1,
        'intra_op_parallelism': 1,
        'cluster-node-timeout': 30000,
        }
    if (cfg.database.backend == "keydb"):
        kwargs['server_threads'] = 2 # keydb only
    if (cfg.database.network_interface=='uds'):
        colo_model.colocate_db_uds(
                db_cpus=cfg.run_args.dbprocs_pn,
                debug=False,
                limit_app_cpus=True,
                **kwargs
                )
    else:
        colo_model.colocate_db(
                port=PORT,
                db_cpus=cfg.run_args.dbprocs_pn,
                debug=False,
                limit_app_cpus=True,
                ifname=cfg.database.network_interface,
                **kwargs
                )

    # Add the ML model
    if (cfg.model.path):
        device_tag = 'CPU' if cfg.model.device=='cpu' else 'GPU'
        colo_model.add_ml_model('model',
                                cfg.model.backend,
                                model=None,  # this is used if model is in memory
                                model_path=cfg.model.path,
                                device=device_tag,
                                batch_size=cfg.model.batch,
                                min_batch_size=cfg.model.batch,
                                devices_per_node=cfg.model.devices_per_node, # only for GPU
                                inputs=None, outputs=None )

    # Start the co-located model
    exp.start(colo_model, block=True, summary=False)


## Clustered DB launch
def launch_clDB(cfg, nodelist, nNodes):
    # Split nodes between the components
    dbNodes = ','.join(nodelist[0: cfg.run_args.db_nodes])
    dbNodes_list = nodelist[0: cfg.run_args.db_nodes]
    simNodes = ','.join(nodelist[cfg.run_args.db_nodes: \
                                 cfg.run_args.db_nodes + cfg.run_args.sim_nodes])
    print(f"Database running on {cfg.run_args.db_nodes} nodes:")
    print(dbNodes)
    print(f"Simulatiom running on {cfg.run_args.sim_nodes} nodes:")
    print(simNodes)
    print("")

    # Set up database and start it
    PORT = cfg.database.port
    exp = Experiment(cfg.experiment.name, launcher=cfg.experiment.launcher)
    runArgs = {"np": 1, "ppn": 1, "cpu-bind": "numa"}
    kwargs = {
        'maxclients': 100000,
        'threads_per_queue': 1, # set to 4 for improved performance
        'inter_op_parallelism': 1,
        'intra_op_parallelism': 64,
        'cluster-node-timeout': 30000,
        }
    if (cfg.database.backend == "keydb"):
        kwargs['server_threads'] = 2 # keydb only
    db = exp.create_database(port=PORT, 
                             batch=False,
                             db_nodes=cfg.run_args.db_nodes,
                             run_command='mpiexec',
                             interface=cfg.database.network_interface, 
                             hosts=dbNodes_list,
                             run_args=runArgs,
                             single_cmd=True,
                             **kwargs
                            )
    exp.generate(db)
    print("Starting database ...")
    exp.start(db)
    print("Done\n")

    # Set the run settings, including the client executable and how to run it
    print("Launching the Fortran client ...")
    client_exe = cfg.sim.executable
    run_settings = PalsMpiexecSettings(client_exe,
                  exe_args=None,
                  run_args=None
                  )
    run_settings.set_tasks(cfg.run_args.simprocs)
    run_settings.set_tasks_per_node(cfg.run_args.simprocs_pn)
    run_settings.set_hostlist(simNodes)
    run_settings.set_cpu_binding_type(cfg.run_args.sim_cpu_bind)
    inf_exp = exp.create_model("client", run_settings)
   
    # Add the ML model
    if (cfg.model.path):
        device_tag = 'CPU' if cfg.model.device=='cpu' else 'GPU'
        inf_exp.add_ml_model('model',
                             cfg.model.backend,
                             model=None,  # this is used if model is in memory
                             model_path=cfg.model.path,
                             device=device_tag,
                             batch_size=cfg.model.batch,
                             min_batch_size=cfg.model.batch,
                             devices_per_node=cfg.model.devices_per_node, # only for GPU
                             inputs=None, outputs=None )

    # Start the inference model
    exp.start(inf_exp, summary=False, block=True)
    print("Done\n")

    # Stop database
    print("Stopping the Orchestrator ...")
    exp.stop(db)


## Main function
@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    # Get nodes of this allocation (job)
    hostfile = os.getenv('PBS_NODEFILE')
    nodelist, nNodes = parseNodeList(hostfile)

    # Write the input file for the client
    log_flag = 0 if cfg.logging=="no" else 1
    fh = open("input.config","w")
    fh.write('%d\n' % (3))
    fh.write('%d %d %d\n' % (cfg.run_args.db_nodes,
                             cfg.run_args.simprocs_pn,
                             log_flag))
    fh.write('%d %d %d\n' % (cfg.model.size[0],
                             cfg.model.size[1],
                             cfg.model.size[2]))
    fh.close()
    
    # Export KeyDB env variables if requested instead of Redis
    if (cfg.database.backend == "keydb"):
        stream = os.popen("which python")
        prefix = stream.read().split("ssim")[0]
        keydb_conf = prefix+"SmartSim/smartsim/_core/config/keydb.conf"
        keydb_bin = prefix+"keydb/src/keydb-server"
        os.environ['REDIS_PATH'] = keydb_bin
        os.environ['REDIS_CONF'] = keydb_conf

    # Call appropriate launcher
    if (cfg.database.launch == "colocated"):
        print(f"\nRunning {cfg.database.launch} DB with {cfg.database.backend} backend\n")
        launch_coDB(cfg,nodelist,nNodes)
    elif (cfg.database.launch == "clustered"):
        print(f"\nRunning {cfg.database.launch} DB with {cfg.database.backend} backend\n")
        launch_clDB(cfg,nodelist,nNodes)
    else:
        print("\nERROR: Launcher is either colocated or clustered\n")

    # Quit
    print("Done")
    print("Quitting")


## Run main
if __name__ == "__main__":
    main()
