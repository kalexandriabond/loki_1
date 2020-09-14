
#import flywheel
from os.path import join as opj
import os
import sys
import argparse
import shutil

#add your api-key
api_key = "bridge-center.flywheel.io:Y86teOyF7LfgZ2yLb9"
fw = flywheel.Client(api_key)

#Initiate argparse for user input
parser = argparse.ArgumentParser()
parser.add_argument("sub", help="subject number")
parser.add_argument("ses", help="input session number - input 2 digit format'XX'")
args, unknown = parser.parse_known_args()

#initialize user arguments
subject_label = args.sub
session = int(args.ses)

# Define lab and project
lab = "mtarrlab"
project_label = "LOKICAT"

#Download files from LOKICAT
path_download = f"{lab}/{project_label}/{subject_label}/ses-0{session}/anat-T1w_acq-mprage"
src_acq = fw.lookup(path_download)
os.mkdir(f't1/{subject_label}')
src_acq.download_file(f'{src_acq.uid}.dicom.zip', f't1/{subject_label}/{src_acq.uid}.dicom.zip')
src_acq.download_file(f'{src_acq.uid}.nii.gz', f't1/{subject_label}/{src_acq.uid}.nii.gz')
src_acq.download_file(f'{src_acq.uid}_mriqc.qa.html', f't1/{subject_label}/{src_acq.uid}_mriqc.qa.html')

print("files downloaded")
