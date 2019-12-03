from pupil_parse.preprocess_utils import config as cf
from pupil_parse.preprocess_utils import extract_session_metadata as md

from pupil_parse.preprocess_utils import deblink_delimit as dd
from pupil_parse.preprocess_utils import edf2pd as ep


import time

def main():

    (raw_data_path, intermediate_data_path,
    processed_data_path, figure_path, simulated_data_path) = cf.path_config(root_folder='Documents/loki_1/',
    data_folder='data/BIDS_copy/')

    print('raw data path ', raw_data_path)

    unique_subjects, unique_sessions, unique_reward_codes = md.extract_subjects_sessions(raw_data_path,
     n_subjects=2, reward_task=1, n_runs=5, session_min=2, session_max=10)

    start_time = time.time()

    for subj_id in unique_subjects:
        for session_n in unique_sessions:

            subj_data_file, subj_data_file_raw, reward_code = ep.find_data_files(subj_id=subj_id,
            session_n=session_n, reward_task=1, lum_task=0,
            raw_data_path=raw_data_path, n_runs=5)

            for raw_data_file in subj_data_file_raw:

                run_n = raw_data_file[-5]
                print('run_n ', run_n)

                print('deblinking and interpolating subject {}'.format(subj_id) +
                ' session {}'.format(session_n) + ' run {}'.format(run_n))

                time.sleep(1)

                prop_invalid_data_deblink_list = []
                prop_invalid_data_outlier_list = []
                n_failed_interp_data_list = []

                reward_samples = ep.read_hdf5('samples', subj_id, session_n,
                intermediate_data_path, reward_code=reward_code, id_str='seg', run_n=run_n)
                reward_messages = ep.read_hdf5('messages', subj_id, session_n,
                intermediate_data_path, reward_code=reward_code, id_str='seg', run_n=run_n)
                reward_events = ep.read_hdf5('events', subj_id, session_n,
                intermediate_data_path, reward_code=reward_code, id_str='seg', run_n=run_n)

                deblinked_reward_samples, prop_invalid_data_deblink = dd.deblink(reward_samples,
                reward_events)
                print('deblinking complete')
                # outlier_removed_reward_samples, prop_invalid_data_outlier = dd.outlier_removal(deblinked_reward_samples)
                # print('outliers removed')
                interpolated_reward_samples, prop_interp_data_success, n_failed_interp_data = dd.interpolate(deblinked_reward_samples)
                print('data interpolated')


                prop_invalid_data_deblink_list.append(prop_invalid_data_deblink)
                n_failed_interp_data_list.append(n_failed_interp_data)


                hdf = ep.save_hdf5(interpolated_reward_samples, reward_events, reward_messages,
                subj_id, session_n, processed_data_path,
                reward_code=reward_code, id_str='clean', run_n=run_n)
                print('clean data saved')

                print('deblink data invalid ', prop_invalid_data_deblink_list)
                print('outlier data invalid ', prop_invalid_data_outlier_list)
                print('data unsuccessfully interpolated ', n_failed_interp_data_list)

    end_time = time.time()

    time_elapsed = end_time - start_time
    print('time elapsed: ', time_elapsed)


if __name__ == '__main__':

    main()
