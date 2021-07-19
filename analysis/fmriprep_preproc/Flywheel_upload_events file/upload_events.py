import flywheel
from os.path import join as opj
import os
import sys
import argparse
import glob
import re
# #for FW CLI path
# fw_path = open("fw_file_path.txt")
# sys.path.insert(0,fw_path)

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

run_pattern = re.compile('run\d{2}')
run_n_pattern = re.compile('\d{2}')


#find event files from local repo and upload to FW in specific acqusitions
files = glob.glob(f"/data/loki_1/data/BIDS/sub-0{subject_label}/{session_label}/func/*lokicat*")
for file in files:

    fn = os.path.basename(file)

    if(fn.find('.tsv')>0):

        run_phrase = run_pattern.search(fn).group()
        run_n = run_n_pattern.search(run_phrase).group()

        print(run_phrase, fn)
        #This is the path  folder where acquisitions for this subject and session are located
        path=opj(lab, project_label, subject_label, session_label,f"func-bold_task-lokicat_run-{run_n}").replace("\\",'/')
        #confirm path
        print(path)
        # get id for specific acquisition
        acquisition_id = fw.lookup(path).id
        print(acquisition_id)
        # retrieve object of acquistion with this ID
        this_acq = fw.get(acquisition_id)
        print(fn)
        this_acq.upload_file(f"/data/loki_1/data/BIDS/sub-0{subject_label}/{session_label}/func/{fn}")
