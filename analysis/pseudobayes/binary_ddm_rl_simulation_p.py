import os


home_path = os.path.expanduser('~')

exp_parameter_path = os.path.join(home_path,'Desktop/loki_1/experimental_parameters/reward_parameters')
condition_key_path = os.path.join(home_path, 'Desktop/loki_1')
analysis_path = os.path.join(home_path, 'Desktop/loki_1/analysis/pseudobayes/')

os.chdir(analysis_path)

from simulation_functions_loki import Simulation
import numpy as np
from multiprocessing import Pool
from time import time
import glob

import pandas as pd

from pickle_objects import save_object



# alpha: belief lr
# beta: cpp lr

mod_alpha = 1
mod_beta = 1

learning_rates = {'alpha': mod_alpha,'beta': mod_beta}




"""hypothesized update for bound + drift"""

# filename structure: 786_reward2_cond6530.csv

condition_key_df = pd.read_csv(os.path.join(condition_key_path, 'reward_condition_key.csv')) # get reward codes
condition_order_df = pd.read_csv(os.path.join(condition_key_path, 'reward_condition_order.csv')) # get condition sequence & skip subject that dropped the task
subj_data_files = glob.glob(os.path.join(exp_parameter_path,'*_reward[0-9]*_cond[0-9]*.csv')) # match pattern for exp. data file


subj_data_files.sort()


subject_ids = condition_order_df.coax_id.dropna().tolist()
reward_codes = condition_key_df.code.tolist()
lambda_vals = condition_key_df.volatility.tolist()


def cpu_simulation(model, learning_rates, drift_start, bound_start, sp_start, tr_start,
                   pathstring, subject_id, reward_code, run_n):
    sim = Simulation(model, learning_rates, drift_start, bound_start, sp_start, tr_start,
                     pathstring, subject_id, reward_code, run_n)
    sim.adapt_ddm()
    return sim


av_model = 3
n_subjects = 4

drift_start = 0.001
bound_start = 0.3
sp_start = 0.5
tr_start = 0.2


args = [(av_model, learning_rates, drift_start,
bound_start, sp_start,
        tr_start, file, file.split('reward')[1][-4:-1], file.split('reward')[2][0], file.split('run')[1][0]) for file in subj_data_files]


sim_start_time = time()

with Pool() as p:
    av_model_sims=p.starmap(cpu_simulation, args)

sim_end_time = time()


sim_time = sim_end_time - sim_start_time

sim_data_path = os.path.expanduser('~') + '/Desktop/loki_1/data/simulated_data/'


# save each simulation as a pickled object
[save_object(sim, sim_data_path + 'sim' + sim.subject_id + '_reward' + sim.reward_code + '_run' + sim.run_n + '.pkl') for sim in av_model_sims]
