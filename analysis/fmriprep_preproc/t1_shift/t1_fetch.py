
import os
import flywheel
from os.path import join as opj
import sys
import argparse
import shutil
from pathlib import Path

os.chdir(os.path.join(os.path.expanduser('~'), 'Desktop/loki_1/')) # go to working directory

from utils import api_config

# log in
fw = flywheel.Client(os.environ['API_KEY'])

#Initiate argparse for user input
parser = argparse.ArgumentParser()
parser.add_argument("sub", help="subject number")
parser.add_argument("ses", help="input session number - input 2 digit format'XX'")
args, unknown = parser.parse_known_args()

subject_label = 860
session = 1

#initialize user arguments
subject_label = args.sub
session = int(args.ses)

# Define lab and project
lab = "mtarrlab"
project_label = "LOKICAT"

#Download files from LOKICAT
path_download = f"{lab}/{project_label}/{subject_label}/ses-0{session}/anat-T1w_acq-mprage"
src_acq = fw.lookup(path_download)

path = Path(f'./t1/{subject_label}')
path.mkdir(parents=True, exist_ok=True)
src_acq.download_file(f'{src_acq.uid}.dicom.zip', f't1/{subject_label}/{src_acq.uid}.dicom.zip')
src_acq.download_file(f'{src_acq.uid}_c.nii.gz', f't1/{subject_label}/{src_acq.uid}.nii.gz')
src_acq.download_file(f'{src_acq.uid}_c_mriqc.qa.html', f't1/{subject_label}/{src_acq.uid}_mriqc.qa.html')

print("files downloaded")
