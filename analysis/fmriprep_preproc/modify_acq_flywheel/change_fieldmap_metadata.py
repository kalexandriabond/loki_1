"""

This script changes the phase encoding direction and modality label
for all the field map acquisitions of a certain project in Flywheel.

"""

import os
os.chdir(os.path.join(os.path.expanduser('~'), 'Desktop/loki_1/')) # go to working directory


import flywheel
from os.path import join as opj
from utils import api_config

# log in
fw = flywheel.Client(os.environ['API_KEY'])


# Define project and look them up on the client
lab = "coax"
project_label = "LOKI1"

project = fw.lookup((opj(lab, project_label)).replace('\\','/'))

# crete and format the query to find acquisitions
query = (
    'label=~.*fmap,'
    'parents.project={}'
)


query = query.format(project.id)

# Find acquisitions matching query
acq_list = fw.acquisitions.find(query)


new_phase_encoding_direction = 'j'

# Acq should be epi
# modality should be either magnitude1 or phasediff
# phase encoding direction should be (j) NOT (j-)

# Iterate over returned acquisitions
for acq in acq_list:
    # Iterate over all files in that acquisition
    for file in acq.files:

        if file['type'] == 'nifti':

            if file['classification']['Intent'][0] == 'Fieldmap':
                print('modifying the metadata for ' + file.info['BIDS']['Filename'])
                print('session %s of subject %s '
                              'in project %s' % (fw.get(acq['parents'].session).label,
                                                 fw.get(acq['parents'].subject).label,
                                                 project_label))

                # Initialise update dict
                update_dict = dict()
                #get subject and session label
                subject_label = fw.get(acq['parents'].subject).label
                session_label = fw.get(acq['parents'].session).label
                # For custom info that is hierarchical, we must copy
                bids_dict = file['info'].get('BIDS')
                print('BIDS dict ', bids_dict)
                # Only do something if BIDS exists on file
                if isinstance(bids_dict, dict):
                    bids_dict['Acq'] = "epi"

                    if 'phasediff' in bids_dict['Filename']:
                        print('phasediff fieldmap found')

                        bids_dict['Modality'] = 'phasediff'

                    elif 'magnitude' in bids_dict['Filename']:
                        print('magnitude fieldmap found')

                        bids_dict['Modality'] = 'magnitude1'

                    update_dict['BIDS'] = bids_dict
                    # For flat key-value pairs, no need to copy - just set
                    update_dict['PhaseEncodingDirection'] = new_phase_encoding_direction
                    acq.update_file_info(file['name'], update_dict)

                    print("fieldmap info update finished")
                    print("updated info", file.info)
                else:
                    print('there is no BIDS info for session %s of subject %s '
                          'in project %s' % (fw.get(acq['parents'].session).label,
                                             fw.get(acq['parents'].subject).label,
                                             project_label)
                          )
