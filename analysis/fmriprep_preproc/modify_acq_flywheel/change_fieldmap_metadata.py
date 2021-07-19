"""

This script changes the phase encoding direction, echo times, and modality label
for the relevant field map acquisitions of a certain project in Flywheel.

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
acquisitions = fw.acquisitions.find(query)



# Acq should be epi
# modality should be either magnitude1 or phasediff
# phase encoding direction should be (j) NOT (j-)

new_phase_encoding_direction = 'j'

phase_diff_echo_time_1 = 0.00487
phase_diff_echo_time_2 = 0.00733

nifti_files = list()

for acq in acquisitions:

    acq = acq.reload()

    [nifti_files.append(f) if f.type == 'nifti' else print(f.type) for f in acq.files] # get only files of type 'tabular data'


for file in nifti_files:

    if file['classification']['Intent'][0] == 'Fieldmap':
            print('modifying the metadata for file %s %s of subject %s '
                          'in project %s' % (file.name,
                                            fw.get(acq.parents.session).label,
                                            fw.get(acq.parents.subject).label,
                                            project_label))

            info = file.info
            info['BIDS']['Acq'] = "epi"
            info['PhaseEncodingDirection'] = new_phase_encoding_direction

            if 'phasediff' in info['BIDS']['Filename']:
                print('phasediff fieldmap found')

                info['BIDS']['Modality'] = 'phasediff'

                info["EchoTime1"] = phase_diff_echo_time_1
                info["EchoTime2"] = phase_diff_echo_time_2

                info.pop('EchoTime', None) # get rid of old EchoTime (replaced by above)

            elif 'magnitude' in info['BIDS']['Filename']:
                print('magnitude fieldmap found')

                info['BIDS']['Modality'] = 'magnitude1'


            file.replace_info(info)

            print("fieldmap info update finished")
