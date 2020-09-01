"""

This script changes the phase encoding direction and modality label of 
the field map inFlywheel to the opposite of that of the BOLD images. 

"""
import flywheel
from os.path import join as opj

# Initialise first flywheel client
api_key = "bridge-center.flywheel.io:Y86teOyF7LfgZ2yLb9"
fw = flywheel.Client(api_key)

# Define new modality label and phase encoding direction
new_mod_label = "T1w" #TODO: Maybe this should be magnitude?
mew_ph_enc_dir = "j"

# Define porject, subject and session
# and look them up on the client
lab = "coax"
project_label = "LOKI1"
subject_label = "790"
session_label = "ses-05"

project = fw.lookup((opj(lab, project_label)).replace("\\",'/'))
subject = fw.lookup((opj(lab, project_label, subject_label)).replace("\\",'/'))
session = fw.lookup((opj(lab, project_label, subject_label, session_label)).replace("\\",'/'))

# crete and format the query to find acquisition 
query = (
    'label=~.*t1w.*,'
    'parents.project={0},'
    'parents.subject={1},'
    'parents.session={2}'
)
query = query.format(project.id, subject.id, session.id)

# Find acquisitions matching query
acq_list = fw.acquisitions.find(query)
# Iterate over returned acquisitions
for acq in acq_list:
    # Iterate over all files, which should just one in this case
    for file in acq.files:
        # We just want to modify the niftis
        if file['type'] == 'nifti':
            # Initialise update dict
            update_dict = dict()
            # For custom info that is hierarchical, we must copy
            bids_dict = file['info'].get('BIDS')
            # Only do something if BIDS exists on file
            if isinstance(bids_dict, dict):
                bids_dict['Modality'] = new_mod_label 
                bids_dict['template'] = 'anat_file'
                bids_dict['Filename'] = f"sub-{subject_label}_{session_label}_T1w.nii.gz"
                
                try:
                    bids_dict.pop('Dir')
                except:
                     print('Dir attributed was already popped. '
                           'Maybe in a previous run?')
                     
                update_dict['BIDS'] = bids_dict
                # For flat key-value pairs, no need to copy - just set
                update_dict['PhaseEncodingDirection'] = 'j'
                # Uncomment below to actually update
                acq.update_file_info(file['name'], update_dict)
                
                print("Nifti info update finished")
                
            else:
                print('there is no BIDS info for session %s of subject %s '
                      'in project %s' % (fw.get(acq['parents'].session).label,  
                                         fw.get(acq['parents'].subject).label, 
                                         project_label)
                      )
                