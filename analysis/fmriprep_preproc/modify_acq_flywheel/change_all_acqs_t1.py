"""

This script changes the phase encoding direction and modality label 
for all the field map acquisitions of a certain project in Flywheel.

"""

import flywheel
from os.path import join as opj

# Initialise first flywheel client
api_key = "bridge-center.flywheel.io:Y86teOyF7LfgZ2yLb9"
fw = flywheel.Client(api_key)

# Define new modality label and phase encoding direction
new_mod_label = "T1w" 
mew_ph_enc_dir = "j"

# Define project and look them up on the client
lab = "coax"
project_label = "LOKI1"

project = fw.lookup((opj(lab, project_label)).replace('\\','/'))

# crete and format the query to find acquisitions 
query = (
    'label=~.*t1w.*,'
    'parents.project={}'    
)
query = query.format(project.id)

# Find acquisitions matching query
acq_list = fw.acquisitions.find(query)
# Iterate over returned acquisitions
for acq in acq_list:
    # Iterate over all files in that acquisition
    for file in acq.files:
        # We just want to modify the niftis
        if file['type'] == 'nifti':
            # Initialise update dict
            update_dict = dict()
            #get subject and session label
            subject_label = fw.get(acq['parents'].subject).label
            session_label = fw.get(acq['parents'].session).label
            # For custom info that is hierarchical, we must copy
            bids_dict = file['info'].get('BIDS')
            # Only do something if BIDS exists on file
            if isinstance(bids_dict, dict):
                bids_dict['Modality'] = new_mod_label 
                bids_dict['template'] = 'anat_file'
                bids_dict['Filename'] = f"sub-{subject_label}_{session_label}_T1w.nii.gz"
                     
                update_dict['BIDS'] = bids_dict
                # For flat key-value pairs, no need to copy - just set
                update_dict['PhaseEncodingDirection'] = mew_ph_enc_dir
                # Uncomment below to actually update
                acq.update_file_info(file['name'], update_dict)
                
                print("Nifti info update finished")
            else:
                print('there is no BIDS info for session %s of subject %s '
                      'in project %s' % (fw.get(acq['parents'].session).label,  
                                         fw.get(acq['parents'].subject).label, 
                                         project_label)
                      )
                
