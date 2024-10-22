import flywheel as fw
import os
import api_config
import pandas as pd

fw_instance = fw.Client(os.environ['API_KEY'])

# set the project
lab = 'coax'
project_label = 'LOKI1'
project = fw_instance.lookup(os.path.join(lab,project_label))

# get gear
gear = fw_instance.lookup('gears/extract-cmrr-physio')

job_list = list()


# iterate over the subjects and sessions in the project
for sub in project.subjects.iter():
    for ses in sub.sessions.iter():
        ses = ses.reload()

        # find physio acquisitions
        physio_acquisitions = ses.acquisitions.find('label=~PhysioLog')


        for acq in physio_acquisitions:
            acq = acq.reload()

            # find all files in the acquisition that are of type "dicom"
            dicom_files = [f for f in acq.files if f.type == 'dicom']

            # extract dicom file from list
            assert len(dicom_files) == 1, 'check dicom_files'
            dicom = dicom_files[0]
            print('dicom :', dicom)

            # create a gear input object consisting of key/value pairs, where the keys
            # are the names of input items as found in the gears manifest (e.g. https://github.com/flywheel-apps/extract-cmrr-physio/blob/1.2.4/manifest.json#L21), and the values
            # are the input value.  we pass in the flywheel file object.
            inputs = {'DICOM_ARCHIVE': dicom}

            # to set config options:
            # config = {'Dry-Run': True}
            # job_id = gear.run(config=config, inputs=inputs, destination=acq)

            # to use default config:
            job_id = gear.run(inputs=inputs, destination=dicom.parent)
            print(f'Job {job_id} submitted for {sub.label} {ses.label} {acq.label}')
            job_list.append(job_id)

# check status of jobs

jobs = fw_instance.get_current_user_jobs(gear='extract-cmrr-physio')

job_df = []
for job in jobs.jobs:
    d = {
        'job_id' : job.id,
        'job_state' : job.state,
        'job_gear_id': job.gear_id,
        'job_gear_name' : job.gear_info['name'],
        'job_gear_vsn' : job.gear_info['version']
    }
    job_df.append(d)

job_df = pd.DataFrame(job_df)

job_df.to_csv('~/Desktop/loki_1/analysis/physio/physio_extraction_job_data.csv')
