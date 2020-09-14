

import flywheel as fw
import os
import numpy as np
import time

api_key = 'bridge-center.flywheel.io:Y86teOyF7LfgZ2yLb9'
fw_instance = fw.Client(api_key)

project_label = 'LOKI1'
project = fw_instance.projects.find_first('label='+project_label)
lab = project.group

def run_utility_gear(gear_name, fw_instance, session):

    gear_instance = fw_instance.lookup(os.path.join('gears', gear_name))

    config = gear_instance.get_default_config()

    config['entire_project'] = True

    print(config)

    analysis_id = gear_instance.run(config=config, inputs=[], destination=session)

    print(analysis_id)

    return analysis_id

for session in project.sessions.iter():

        session_id = session.label
        subject_id = session.subject.label

        session_lookup_string = os.path.join(lab, project_label, subject_id, session_id)

        session = fw_instance.lookup(session_lookup_string)

        print(session_lookup_string)

        bids_analysis_id = run_utility_gear('curate-bids', fw_instance, session)
        print('successful bids curation.')
        time.sleep(1)
