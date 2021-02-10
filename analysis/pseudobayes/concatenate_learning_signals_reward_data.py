import os, glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


ls_path = (os.path.join(os.path.expanduser('~'), 'Desktop/loki_1/data/simulated_data/'))
reward_path = (os.path.join(os.path.expanduser('~'), 'Desktop/loki_1/data/BIDS/sub-*/*/beh/'))
aggregated_data_path = (os.path.join(os.path.expanduser('~'), 'Desktop/loki_1/analysis/aggregated_data/'))
test_fig_path = (os.path.join(os.path.expanduser('~'), 'Desktop/loki_1/figures/trial_structure_check_figs/'))

paths = [ls_path, aggregated_data_path, test_fig_path]

paths_exist = [os.path.exists(path) for path in paths]

assert (len(np.unique(paths_exist)) == 1) & (np.unique(paths_exist)[0] == True), 'check paths'

ls_fn_pattern = ('learning_signals.csv')
reward_fn_pattern = ('sub-[0-9]*_ses[0-9]*_task-lokicat_run*.tsv')
# sub-0790_ses02_task-lokicat_run01_08132019_150642.tsv

n_subjects = 4; n_sessions = 9; n_runs = 5


ls_file = glob.glob(os.path.join(ls_path, ls_fn_pattern))
# assert len(ls_files) == (n_subjects * n_sessions * n_runs), 'check number of learning signal files'

reward_files = glob.glob(os.path.join(reward_path, reward_fn_pattern), recursive=True)
reward_files.sort()
# assert len(reward_files) == (n_subjects * n_sessions * n_runs), 'check number of reward files'

reward_dfs = [pd.read_csv(file, sep='\t|\,', engine='python') for file in reward_files]
[df.rename(columns=lambda x: x.strip(), inplace=True) for df in reward_dfs]

# reward_dfs_truncated = [df.iloc[1:-1] for df in reward_dfs] # remove first and last observation to match pupil data
reward_df = pd.concat(reward_dfs).reset_index(drop=True)
reward_df.rename(columns={'run': 'run_n'}, inplace=True)

ls_df = pd.read_csv(ls_file[0])
# ls_dfs = [pd.read_csv(file) for file in ls_files] # this is already truncated & concatenated.
ls_df.groupby(['subj_id', 'reward_code', 'run_n']).size().apply(print)
reward_df.groupby(['subj_id', 'reward_code','run_n']).size().apply(print) # verify n_observations

reward_df.drop(reward_df.loc[(reward_df.subj_id == 790) & (reward_df.reward_code == 4)].index, inplace=True)

ls_df.reward_code = ls_df.reward_code.astype('int'); ls_df.subj_id = ls_df.subj_id.astype('int')
reward_df.reward_code = reward_df.reward_code.astype('int'); reward_df.subj_id = reward_df.subj_id.astype('int')
reward_df.condition = reward_df.condition.astype('int'); reward_df.trial = reward_df.trial.astype('int');
reward_df.run_n = reward_df.run_n.astype('int'); ls_df.run_n = ls_df.run_n.astype('int');




assert ls_df.subj_id.nunique() == reward_df.subj_id.nunique(), 'check subj_id'
assert ls_df.reward_code.nunique() == reward_df.reward_code.nunique(), 'check reward_code'
assert ls_df.run_n.nunique() == reward_df.run_n.nunique(), 'check run_n'

assert len(ls_df) == len(reward_df), 'check n_observations'

ls_df_sorted = ls_df.sort_values(by=['reward_code', 'subj_id', 'run_n']).reset_index(drop=True)
reward_df_sorted = reward_df.sort_values(by=['reward_code', 'subj_id', 'run_n']).reset_index(drop=True)

# check sorting
assert (ls_df_sorted.subj_id == reward_df_sorted.subj_id).sum() == len(ls_df_sorted), 'check subj_id'
assert (ls_df_sorted.reward_code == reward_df_sorted.reward_code).sum() == len(ls_df_sorted), 'check reward_code'
# assert (ls_df_sorted.trial == reward_df_sorted.trial).sum() == len(ls_df_sorted), 'check trial'

# extract relevant columns
ls_df_sorted_pared = ls_df_sorted[['cpp', 'b_t0', 'b_t1', 'MC',
'H', 'signed_B_diff', 'ideal_B', 'lambda_val', 'p_optimal']]

# merge
ls_reward_df = pd.concat([ls_df_sorted_pared, reward_df_sorted], axis=1)

# create shifted_epoch_trial variable to specify n_trials in previous epoch
# this would be epoch_trial[-2:] - epoch_len, so epoch_t = 0, epoch_t-1 = -1, ...
ls_reward_df['shifted_epoch_trial_run'] = ls_reward_df.groupby(['subj_id', 'reward_code', 'epoch_number', 'run_n']).epoch_trial.apply(lambda x: x - x.iloc[-1]-1).reset_index(drop=True)
ls_reward_df['shifted_epoch_trial'] = ls_reward_df.groupby(['subj_id', 'reward_code', 'epoch_number']).epoch_trial.apply(lambda x: x - x.iloc[-1]-1).reset_index(drop=True)

# replace the negative trials beyond the specified window with actual trials for ease of sns plotting
n_trials_back = 3
ls_reward_df.loc[ls_reward_df.shifted_epoch_trial < -n_trials_back, 'shifted_epoch_trial'] = ls_reward_df.loc[ls_reward_df.shifted_epoch_trial < -n_trials_back, 'epoch_trial']
ls_reward_df.loc[ls_reward_df.shifted_epoch_trial_run < -n_trials_back, 'shifted_epoch_trial_run'] = ls_reward_df.loc[ls_reward_df.shifted_epoch_trial_run < -n_trials_back, 'epoch_trial']


# test trial structure with ideal_B and cpp

# ideal_B should plummet at t=0 and asymptote at t=-n:-1
plt.figure(); sns.lineplot(x='shifted_epoch_trial', y='ideal_B', data=ls_reward_df.loc[ls_reward_df.shifted_epoch_trial < 9])
plt.savefig(os.path.join(test_fig_path, 'idealB_trial_check.png'))

# cpp should peak at t=0 and asymptote at t=-n:-1
plt.figure(); sns.lineplot(x='shifted_epoch_trial', y='cpp', data=ls_reward_df.loc[ls_reward_df.shifted_epoch_trial < 9])
plt.savefig(os.path.join(test_fig_path, 'cpp_trial_check.png'))

# accuracy should plummet at or after t=0 and asymptote at t=-n:-1
plt.figure(); sns.lineplot(x='shifted_epoch_trial', y='p_accuracy', data=ls_reward_df.loc[ls_reward_df.shifted_epoch_trial < 9].dropna())
plt.savefig(os.path.join(test_fig_path, 'acc_check.png'))

# rt might plummet at or after t=0 and asymptote at t=-n:-1, but likely messy
plt.figure(); sns.lineplot(x='shifted_epoch_trial', y='rt', data=ls_reward_df.loc[ls_reward_df.shifted_epoch_trial < 9].dropna())
plt.savefig(os.path.join(test_fig_path, 'rt_check.png'))


# print to aggregated_data_path
ls_reward_df.to_csv(os.path.join(aggregated_data_path, 'ls_reward_df.csv'), index=False)
