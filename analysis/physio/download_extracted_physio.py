import flywheel as fw
import os

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
    ses.download_tar(os.path.join(physio_data_path,'physio_extract_sub' + subject + '_ses' + session_n + '.tar'), include_types=['log'])
