import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

import warnings
import os
import glob
import nibabel as nib
from itertools import compress
import scipy.io as sio

warnings.simplefilter(action="ignore", category=FutureWarning)
warnings. filterwarnings(action="ignore", category=DeprecationWarning)

plt.switch_backend('Agg')
plt.ioff()

subject = input('Subject: ')
session = input('Session: ')


stim_dur = 1.5 # not sure about this for button press analysis, but keeping trial length for now
TR = 0.75
n_volumes = 738
n_trials = 60
n_runs = 5


def generate_design_matrix(events, tr, n_volumes):
    """ Generate a design matrix for subsequent analyses.

    Args:
        events (pd.df): the conditions of interest
       tr (float): a scalar sampling rate for the BOLD data in seconds
        n_volumes (int): the number of volumes (or number of samples) acquired per run

    Returns:
        dm: a design matrix of shape (n_volumes, n_conditions)
    """
    # loop over conditions
    conditions = np.unique(events.trial_type)
    n_conditions = len(set(events['trial_type'].values))

    print('conditions: ', conditions, n_conditions)

    dm = np.zeros((n_volumes, n_conditions))

    for i, cond in enumerate(conditions):

        # onset times for qth condition in run p
        otimes = np.array(
            events[events['trial_type'] == cond]['onset'].values//tr).astype(int)
        print(otimes)
        yvals = np.zeros((n_volumes))
        for r in otimes:
            yvals[r] = 1
        dm[:, i] = yvals

        assert dm.shape == (n_volumes, n_conditions), 'check design matrix dimensions'

    return dm



def viz_design_matrix(dm, fig_path=None, savefig=None, str_id=None):
    """ Visualize a design matrix.

    Args:
        dm (np.ndarray): the design matrix
        fig_path (str): path for figures (optional)
        save_fig (bool): whether to save the figure (optional)
        str_id (str): an identifying string for saving the figure

    Returns:
        None
    """

    fig, ax = plt.subplots(1,1)
    ax.imshow(dm, cmap='gray', aspect='auto')
    plt.title('Design matrix')
    plt.xlabel('condition'); plt.ylabel('volume / time')
    ax.set_xticks(np.arange(dm.shape[1]))
    ax.set_xticklabels(['left', 'right'])

    if savefig:
        plt.savefig(os.path.join(fig_path,
        ('design_matrix_{}.pdf').format(str_id)))

    return None

def save_as_cell_array(data):

    n_runs = len(data)

    obj_arr = np.zeros((n_runs,), dtype=np.object)

    for i, dat in enumerate(data):
            obj_arr[i] = dat

    return obj_arr


"""
Load data
"""

# source_data_path = ('/Users/67981492/Desktop/loki_1/data/BOLD/sub-{}/fmriprep/sub-{}').format(subject,subject) # starting with one sub

source_data_path = ('/data/loki_1/data/BOLD/sub-{}/fmriprep/sub-{}').format(subject,subject) # starting with one sub
session_data_path = (os.path.join(source_data_path, 'ses-{}/mat/')).format(session) # starting with one session


if not os.path.exists(session_data_path):
	os.makedirs(session_data_path)


runs_source = glob.glob(os.path.join(source_data_path, ('ses-{}').format(session), 'func', '*T1w*preproc*nii.gz'))
runs_source.sort()
assert runs_source, 'check preprocessed nii.gz path'


events_source = glob.glob(os.path.join(source_data_path,  ('ses-{}').format(session), 'func', '*LR_events.tsv'))
events_source.sort()
assert events_source, 'check events path'

runs_comp = compress(runs_source, np.ones_like(runs_source))
events_comp = compress(events_source, np.ones_like(events_source))


design = []


for i, (run, event) in enumerate(zip(runs_comp, events_comp)):
    print('event ', event)
    print('run {} {}'.format(run, i+1))
   data_obj_arr = np.zeros((1,), dtype=np.object)

   y = nib.load(run).get_data().astype(np.float32)
   dims = y.shape # dim = x,y,z,time/n_volumes
   print(dims)
   assert dims[-1] == n_volumes, 'check data dimensions'
   data_obj_arr[0] = y
   sio.savemat(os.path.join(session_data_path, 'data_run{}.mat'.format(i+1)), {'run_BOLD_data'.format(i) : data_obj_arr})

    # load onsets and items
    try:
      onsets = pd.read_csv(event, delim_whitespace=True)
      onsets.dropna(inplace=True)
      onsets.button_press_onset

      items = pd.read_csv(event, delim_whitespace=True)
      items.dropna(inplace=True)
      items = items["LR"].values
    except:
      onsets = pd.read_csv(event, sep=r'\,|\t',engine='python')
      onsets.dropna(inplace=True)
      onsets.button_press_onset

      items = pd.read_csv(event, sep=r'\,|\t',engine='python')
      items.dropna(inplace=True)
      items = items["LR"].values


    onsets = onsets["button_press_onset"].values
    n_events = len(onsets)

    # initialize design matrix
    events = pd.DataFrame()
    events["duration"] = [stim_dur] * n_events
    events["onset"] = onsets
    events["trial_type"] = items

    design.append(events)

assert len(design) == n_runs, 'check run data'

full_design_m = []

for i, des in enumerate(design):

    full_dm_temp = generate_design_matrix(des, TR, n_volumes)
    viz_design_matrix(full_dm_temp, fig_path=session_data_path,
     savefig=True, str_id=('LR_run{}').format(i+1))

    full_design_m.append(full_dm_temp)

design_cell_arr = save_as_cell_array(full_design_m)
sio.savemat(os.path.join(session_data_path, 'design_LR.mat'), {'design': design_cell_arr})
