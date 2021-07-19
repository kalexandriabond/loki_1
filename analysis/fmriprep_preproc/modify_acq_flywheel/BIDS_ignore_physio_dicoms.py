"""

This script BIDS-ignores physio DICOMs.

"""

import os
os.chdir(os.path.join(os.path.expanduser('~'), 'Desktop/loki_1/')) # go to working directory

import flywheel
from os.path import join as opj
from utils import api_config

fw = flywheel.Client(os.environ['API_KEY']) # log in


lab = "coax"
project_label = "LOKI1"

project = fw.lookup((opj(lab, project_label)).replace('\\','/'))

# create and format the query to find acquisitions
query = (
    'label=~.*Physio,'
    'parents.project={}'
)

query = query.format(project.id)

dicom_files = list()

acquisitions = fw.acquisitions.find(query) # find acquisitions matching query


for acq in acquisitions: # iterate over returned acquisitions

    acq = acq.reload()

    [dicom_files.append(f) if f.type == 'dicom' else print(f.type) for f in acq.files] # get only files of type 'dicom'


for file in dicom_files:

    if file.info['BIDS'] != 'NA': # if the file contains BIDS metadata

        print('modifying the metadata for file %s %s of subject %s '
                      'in project %s' % (file.info['SeriesDescription'],
                                        fw.get(acq.parents.session).label,
                                        fw.get(acq.parents.subject).label,
                                        project_label))

        info = file.info
        info['BIDS']['ignore'] = True
        file.replace_info(info)

    elif file.info['BIDS'] == 'NA':

        print('No BIDS metadata found for %s' % file.info['SeriesDescription'])
