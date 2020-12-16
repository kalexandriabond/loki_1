import flywheel
from os.path import join as opj
import os
import sys
import argparse
import shutil

#add your api-key
api_key = 'bridge-center.flywheel.io:EnMp3OeZ0By95NuStL'
fw = flywheel.Client(api_key)

#Initiate argparse for user input
parser = argparse.ArgumentParser()
parser.add_argument("sub", help="subject number")
parser.add_argument("ses_s", help="input starting session number - input 2 digit format'XX'")
parser.add_argument("ses_e", help="input ending session number - input 2 digit format'XX'")
args, unknown = parser.parse_known_args()

#initialize user arguments
subject_label = args.sub
session_start = int(args.ses_s)
session_end = int(args.ses_e)

# Define lab and project
lab = "coax"
project_label = "LOKI1"

#add t1 image file to all given session range under given subject
counter = session_start
src_path= f"t1/{subject_label}"
while counter <= session_end:
    if counter < 10:
        session_label = f"0{counter}"
    else:
        session_label = str(counter)
    path=opj(lab, project_label, subject_label, f"ses-{session_label}").replace("\\",'/')
    #print(path)
    acquisition_id = fw.lookup(path)
    acquisition = acquisition_id.add_acquisition(label='anat-t1w-acq-mprage')
    files = os.listdir(src_path)
    for file in files:
        #print(file)
        acquisition.upload_file(f't1/{subject_label}/{file}')
    print (f"files uploaded to session {session_label}")
    counter = counter + 1
