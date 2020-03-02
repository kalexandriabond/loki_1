import json
import numpy as np
import argparse
import csv
import pandas


def load_response(subj, sess, run):
    greeble_list, level_list, response_list = list(), list(), list()

    rpath = "data/BIDS/sub-0{}/ses-{}/func/sub-0{}_ses-{}_task-level_run-0{}_events.tsv".format(subj, sess, subj,
                                                                                                sess, run)
    with open(rpath) as r:
        responses = csv.reader(r, delimiter="\t")
        next(responses)
        for row in responses:
            greeble_list.append(row[2].split("/")[-1].split(".")[0])
            level_list.append(row[3])
            response_list.append(row[5])
    return greeble_list, level_list, response_list

def get_answer(match, sample, level):
    right = 76
    wrong = 82
    # right = 82
    # wrong = 76
    if level == "Sex":
        if match[0] == sample[0]:
            return right
        else:
            return wrong
    else: #Family
        if match[1] == sample[1]:
            return right
        else:
            return wrong

def calculate_accuracy(greeble_list, level_list, response_list):
    answers = list()
    for i, l in enumerate(level_list):
        if response_list[i] == 'nan':
            match = greeble_list[i]
            continue
        else:
            ans = get_answer(match, greeble_list[i], l)
            answers.append(ans)
    answers = np.array(answers)
    all_real_ans = np.array([int(r) for r in response_list if r != 'nan'])
    acc = np.sum(all_real_ans == answers)/len(answers)
    return acc


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject_id", type=str)
    parser.add_argument("--session", type=str, default="01")
    parser.add_argument("--run", type=str, default="all")

args = parser.parse_args()
if args.run != "all":
    responses = load_response(args.subject_id, args.session, args.run)
    acc = calculate_accuracy(responses[0], responses[1], responses[2])
    print(acc)
else:
    acc_all = list()
    for run in range(6):
        responses = load_response(args.subject_id, args.session, run+1)
        acc = calculate_accuracy(responses[0], responses[1], responses[2])
        acc_all.append(acc)
        print(acc)

    print("Average accuracy is: " + str(sum(acc_all)/len(acc_all)))