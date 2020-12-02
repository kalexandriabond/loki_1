import flywheel as fw
import os
import api_config

physio_data_path = ('/Users/67981492/Desktop/loki_1/data/physio')

fw_instance = fw.Client(os.environ['API_KEY'])

# set the project
lab = 'coax'
project_label = 'LOKI1'
project = fw_instance.lookup(os.path.join(lab,project_label))

collection = fw_instance.collections.find_first('label=valid_subs')

for ses in collection.sessions.iter():
    ses = ses.reload()
    session_n = ses.info['BIDS']['Label']
    subject = ses.info['BIDS']['Subject']

    # if ses. # # TODO: check if ses has log files
    # sessions 3-10 are legacy physio for sub 790
    try:
        ses.download_tar(os.path.join(physio_data_path,'physio_extract_sub' + subject + '_ses' + session_n + '.tar'), include_types=['log'])
    except:
        print('no logs found.')
        continue
