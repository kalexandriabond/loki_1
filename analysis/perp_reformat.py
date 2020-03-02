import csv
import argparse
import numpy as np
# from itertools import zip


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--subj", type=str)
    parser.add_argument("--session", type=str, default="01")
    # parser.add_argument("--run", type=str, default="all")

args = parser.parse_args()

to_reformat_dir = "data/BIDS/sub-0{}/ses-{}/func-old".format(args.subj, args.session)
output_dir = "data/BIDS/sub-0{}/ses-{}/func".format(args.subj, args.session)

for run in range(6):
    fpath = "{}/sub-0{}_ses-{}_task-level_run-0{}_events.tsv".format(to_reformat_dir, args.subj, args.session, run+1)
    reader = csv.reader(open(fpath, "r"))

    content_list = list()
    for i, row in enumerate(reader):
        tmp = row[0]
        content = tmp.strip('][').split('\t')

        if i in [0, 4, 6, 7]:
            continue

        elif i == 3:
            content = [item[1:-1] for item in content]

        elif i == 5:
            content = [item[1:-1] for item in content]
            content = list(np.repeat(content, 5))
        elif i in [8, 9]:
            for j in range(8):
                content.insert(5*j, np.nan)

        content_list.append(content)

    events_data = np.transpose(np.matrix(content_list))

    output_path = "analysis/output_tmp.tsv"
    events_header = "stim_onset, stim_duration, stim_greebles, trial_type, rt, choice"
    output_path = "{}/sub-0{}_ses-{}_task-level_run-0{}_events.tsv".format(output_dir, args.subj, args.session, run+1)

    np.savetxt(output_path, events_data, header=events_header, fmt="%s", delimiter="\t", comments="")
