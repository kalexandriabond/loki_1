
import pandas as pd


def generate_participants_file(sub_IDs, ages, sexes,
handedness, path):

    """

    Update .tsv file with participant data in BIDS-compliant fashion.

    All inputs (other than path) should be lists.

    """

    assert all(isinstance(p, int) for p in participants), 'participant list must be int'
    assert all(isinstance(a, int) for a in ages), 'age list must be int'
    assert all(isinstance(s, str) for s in sexes), 'sex list must be str'
    assert all(isinstance(h, str) for h in handedness), 'handedness list must be str'


    participants = ['sub-0{}'.format(id) for id in sub_IDs] # format subject ids

    participant_data = {'PARTICIPANT': participants, 'AGE': ages, # store as dict
                        'SEX': sexes, 'HANDEDNESS': handedness}

    participant_df = pd.DataFrame(participant_data) # store as pandas df

    participant_df.to_csv(path + '/participants.tsv', index=None, sep='\t') # print to tsv


    return participant_df
