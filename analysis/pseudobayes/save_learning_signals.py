#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  2 20:03:15 2019

@author: 67981492
"""

import os

home_path = os.path.expanduser('~')
analysis_path = os.path.join(home_path, 'Desktop/loki_1/analysis/pseudobayes/')

os.chdir(analysis_path)

import numpy as np
from pickle_objects import load_object
import pandas as pd


sim_data_path = home_path + '/Desktop/loki_1/data/simulated_data/'

condition_key_path = os.path.join(home_path, 'Desktop/loki_1')

condition_key_df = pd.read_csv(os.path.join(condition_key_path, 'reward_condition_key.csv')) #get reward codes
condition_order_df = pd.read_csv(os.path.join(condition_key_path, 'reward_condition_order.csv')) #get condition sequence & skip subject that dropped the task


subject_ids = condition_order_df.coax_id.dropna().astype('int').tolist()
reward_codes = condition_key_df.code.tolist()
lambda_vals = condition_key_df.volatility.tolist()
runs = np.arange(1,6)

av_model_sims = []

for subject_id in subject_ids:
    for reward_code in reward_codes:
        for run_n in runs:
            try:
                av_model_sims.append(load_object(sim_data_path + 'sim' + str(subject_id) + '_reward' + str(reward_code) + '_run' + str(run_n) + '.pkl'))
            except:
                continue

print('is all simulated data loaded?', len(av_model_sims) == (len(subject_ids) * len(reward_codes) * len(runs))) #check that all are loaded

#save learning signals
learning_signal_dfs = [pd.DataFrame(dict((key, value) for (key, value) in zip(['trial','epoch_trial', 'p_optimal', 'cpp', 'b_t0', 'b_t1', 'MC', 'H', 'signed_B_diff',
                                         'reward_code', 'subj_id', 'accuracy', 'target_choice', 'correct_target_choice', 'run_n'],
                      [sim.expParam.trial, sim.expParam.epoch_trial, sim.expParam.reward_p_t1.max(), sim.CPP, sim.B[:,0], sim.B[:,1],
                       sim.MC, sim.H, sim.signed_B_diff, sim.reward_code, sim.subject_id, sim.choiceAcc, sim.choices, sim.corrTarget, sim.run_n]))) for sim in av_model_sims]



learning_signals_df = pd.concat(learning_signal_dfs).reset_index(drop=True)
learning_signals_df['lambda_val'] = np.nan

for reward_code, lambda_val in zip(reward_codes, lambda_vals): #specify lambda for each reward code
    learning_signals_df.loc[learning_signals_df.reward_code == str(reward_code), 'lambda_val'] = lambda_val

#get the belief in the optimal choice
target_beliefs = learning_signals_df[['b_t0', 'b_t1']]

B_ideal_target = np.asarray([target_beliefs.iloc[t, learning_signals_df.correct_target_choice[t]] for t in range(len(target_beliefs))])
B_nonideal_target = np.asarray([target_beliefs.iloc[t, 1-learning_signals_df.correct_target_choice[t]] for t in range(len(target_beliefs))])

learning_signals_df['ideal_B'] = B_ideal_target - B_nonideal_target

print(learning_signals_df.groupby(["subj_id", "reward_code"]).run_n.unique())

learning_signals_df.to_csv(sim_data_path + 'learning_signals.csv', index=False)
