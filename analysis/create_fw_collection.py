import flywheel as fw
import os
import pandas as pd
import api_config

fw_instance = fw.Client(os.environ['API_KEY'])

# set the project
lab = 'coax'
project_label = 'LOKI1'
project = fw_instance.lookup(os.path.join(lab,project_label))

subjects_to_include = pd.read_csv('~/Desktop/loki_1/participants.csv')
subjects_to_include['PARTICIPANT'] = subjects_to_include.PARTICIPANT.str.extract(r'(\d{4})')
subjects_to_include['PARTICIPANT'] = subjects_to_include.PARTICIPANT.str.lstrip('0')

collection_label = 'valid_subs'

collection_id = fw_instance.add_collection({'label': collection_label})
collection = fw_instance.get(collection_id)


subjects = project.subjects()
for sub in subjects:
    print(sub.label)
    if str(sub.label) in subjects_to_include.PARTICIPANT.values:
        for ses in sub.sessions():
            collection.add_sessions(ses.id)
