'''

This script BIDS-ignores tabular data (events, physio).

'''
import os
os.chdir(os.path.join(os.path.expanduser('~'), 'Desktop/loki_1/')) # go to working directory

import flywheel
from os.path import join as opj
from utils import api_config

fw = flywheel.Client(os.environ['API_KEY']) # log in


lab = 'coax'
project_label = 'LOKI1'

project = fw.lookup((opj(lab, project_label)).replace('\\','/'))

# create and format the query to find acquisitions
query = (
    'parents.project={}'
)

query = query.format(project.id)

acquisitions = fw.acquisitions.find(query) # find acquisitions matching query


tabular_files = list()

for acq in acquisitions:

    acq = acq.reload()

    [tabular_files.append(f) if f.type == 'tabular data' else print(f.type) for f in acq.files] # get only files of type 'tabular data'


for file in tabular_files:

    if file.info['BIDS'] != 'NA': # if the file contains BIDS metadata

        print('modifying the metadata for file %s %s of subject %s '
                      'in project %s' % (file.name,
                                        fw.get(acq.parents.session).label,
                                        fw.get(acq.parents.subject).label,
                                        project_label))

        info = file.info
        info['BIDS']['ignore'] = True
        file.replace_info(info)

    elif file.info['BIDS'] == 'NA':

        print('No BIDS metadata found for %s' % file.name)
