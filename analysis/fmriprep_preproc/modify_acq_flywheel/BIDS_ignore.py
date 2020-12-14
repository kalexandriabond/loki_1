"""

This script BIDS-ignores physio files (or other relevant files).

"""

import flywheel
from os.path import join as opj

# Initialise first flywheel client
api_key = "bridge-center.flywheel.io:Y86teOyF7LfgZ2yLb9"
fw = flywheel.Client(api_key)



# Define project and look them up on the client
lab = "coax"
project_label = "LOKI1"

project = fw.lookup((opj(lab, project_label)).replace('\\','/'))

# crete and format the query to find acquisitions
query = (
    'label=~.*Physio,'
    'parents.project={}'
)


query = query.format(project.id)

# Find acquisitions matching query
acq_list = fw.acquisitions.find(query)

# Iterate over returned acquisitions
for acq in acq_list:
    print(acq.label)
    # Iterate over all files in that acquisition
    for file in acq.files:

        if file['type'] == 'tabular data':

            print(file)

            print('modifying the metadata for ')
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
                bids_dict['ignore'] = "True"
                update_dict['BIDS'] = bids_dict
                # For flat key-value pairs, no need to copy - just set
                # Uncomment below to actually update
                acq.update_file_info(file['name'], update_dict)

                print("physio file BIDS-ignored")
            else:
                print('there is no BIDS info for session %s of subject %s '
                      'in project %s' % (fw.get(acq['parents'].session).label,
                                         fw.get(acq['parents'].subject).label,
                                         project_label)
                      )
