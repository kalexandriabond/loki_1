"""

This script BIDS-ignores tabular data (events, physio).

"""

import flywheel
from os.path import join as opj



import os
import api_config

# log in
fw = flywheel.Client(os.environ['API_KEY'])

lab = "coax"
project_label = "LOKI1"

project = fw.lookup((opj(lab, project_label)).replace('\\','/'))

# create and format the query to find acquisitions
query = (
    'label=~.*func-bold,'
    'parents.project={}'
)

query = query.format(project.id)

# find acquisitions matching query
acq_list = fw.acquisitions.find(query)

# iterate over returned acquisitions
for acq in acq_list:
    print(acq.label)
    # iterate over all files in that acquisition
    for file in acq.files:
        if file.type == 'tabular data':

            print(file)

            print('modifying the metadata for ')
            print('session %s of subject %s '
                          'in project %s' % (fw.get(acq['parents'].session).label,
                                             fw.get(acq['parents'].subject).label,
                                             project_label))

            # initialise update dict
            update_dict = dict()
            # get subject and session label
            subject_label = fw.get(acq['parents'].subject).label
            session_label = fw.get(acq['parents'].session).label
            # for custom info that is hierarchical, we must copy
            bids_dict = file['info'].get('BIDS')
            print('BIDS dict ', bids_dict)
            # only do something if BIDS exists on file
            if isinstance(bids_dict, dict):
                bids_dict['ignore'] = "True"
                update_dict['BIDS'] = bids_dict
                acq.update_file_info(file['name'], update_dict)
            else:
                print('there is no BIDS info for session %s of subject %s '
                      'in project %s' % (fw.get(acq['parents'].session).label,
                                         fw.get(acq['parents'].subject).label,
                                         project_label)
                      )
