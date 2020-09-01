import flywheel
from os.path import join as opj
import os
import sys
import argparse

#for FW CLI path
fw_path = open("fw_file_path.txt")
sys.path.insert(0,fw_path)

#Add input arguments for command prompt
parser = argparse.ArgumentParser()
parser.add_argument("api", help="input fw login API starting with 'bridge-center...'")
parser.add_argument("sub", help="subject number")
parser.add_argument("ses", help="session number - input 2 digit format'XX'")
args, unknown = parser.parse_known_args()


# Initialise first flywheel client
api_key = args.api
fw = flywheel.Client(api_key)


# Define lab and project
lab = "coax"
project_label = "LOKI1"

#Define subject and session label
subject_label = args.sub
session_label = f"ses-{args.ses}"
print(session_label)

#find event files from local repo and upload to FW in specific acqusitions
files = os.listdir(f"loki_GitRepo/data/BIDS/sub-0{subject_label}/{session_label}/func")
for file in files:
    if(file.find('.tsv')>0):
        run_index = file.find("run")
        file_link = file[run_index+3:run_index+5]
        #This is the path  folder where acquisitions for this subject and session are located
        path=opj(lab, project_label, subject_label, session_label,f"func-bold_task-lokicat_run-{file_link}").replace("\\",'/')
        #confirm path
        print(path)
        # get id for specific acquisition
        acquistion_id = fw.lookup(path).id
        print(acquistion_id)
        # retrieve object of acquistion with this ID
        this_acq = fw.get(acquistion_id)
        print(file)
        this_acq.upload_file(f"loki_GitRepo/data/BIDS/sub-0{subject_label}/{session_label}/func/{file}")