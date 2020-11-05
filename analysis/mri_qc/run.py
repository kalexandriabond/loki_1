#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This is the main script to
update the QC info for LOKI1 & LOKICAT

"""
#import pandas as pd
import matplotlib.pylab as plt
import os

import argparse
from pathlib import Path

from log import create_log_files
from reports import download_qc_reports

parser = argparse.ArgumentParser(description = 'Generate Log files')

parser.add_argument('-p', dest='project_list',action = 'append',
                    choices = ['LOKI1', 'LOKICAT'],
                    help = 'Select the project to generate the QC files')

parser.add_argument('-o', dest= 'output_dir', type = Path,
                    help = 'destination folder where to store the QC files')

parser.add_argument('--html',  action='store_true',
                    help = ('whether or not download html reports')
                    )


parser.add_argument('--subjects', dest='subjects', action='append',
                        help = ('list of subs to run QC on')
                        )

args = parser.parse_args()


# set project list
if args.project_list:
    project_list = args.project_list
else:
    project_list = ['LOKI1', 'LOKICAT']

if 'LOKI1' in project_list:
    lab = 'coax'
elif 'LOKICAT' in project_list:
    lab = 'mtarrlab'


if args.subjects:
    subjects = args.subjects # # TODO: reformat to be consistent with flywheel notation
else:
    subjects = [790, 811, 813, 860] # # TODO: reformat to be consistent with flywheel notation

# Set output directory
if args.output_dir:
    output_dir = args.output_dir
else:
    output_dir = Path(os.getcwd())

output_dir = output_dir.joinpath('QC_outputs')
output_dir.mkdir(parents = True, exist_ok=True)

html = args.html


#TODO: Check if output dir exist, if not create
# if output_dir.exists():
#     reset = args.reset
#     #if reset, remove folder and create again
#     if reset:
#         shutil.rmtree(output_dir.absolute().as_posix())
#     #create folder structure
# else:
#     reset = True

# # #create folders in the case of reset project outputs
# # if reset:
# #     for project in project_list:
# #         output_dir.joinpath(project).mkdir(exist_ok=True, parents=True)

for project in project_list:

    print(" Generating QC info for project {}".format(project))
    # save csvs
    logs_dir = output_dir.joinpath(project, 'logs')
    logs_dir.mkdir(parents = True, exist_ok = True)

    plots_dir = output_dir.joinpath(project, 'plots')
    plots_dir.mkdir(parents = True, exist_ok = True)

    qc_log_dict = create_log_files(lab, project, subjects)

    for mod, log_df in qc_log_dict.items():

        out_log_file = logs_dir.joinpath(project + "_" + mod + "_QC.csv")
        # save as csv
        log_df.to_csv(out_log_file.absolute().as_posix(), index=False)

        # Generate the plots
        if mod == 't1':
            vars_plot = ['cnr', 'fwhm_avg',
                         'snr_total', 'snrd_total']
            plot_file = plots_dir.joinpath(project + "_" + mod + "_QC.png")
        else:
            vars_plot = ['tsnr', 'fwhm_avg', 'fd_mean',
                         'dvars_nstd', 'gcor', 'snr']
            plot_file = plots_dir.joinpath(project + "_" + mod + "_EPI_QC.png")


        log_df.loc[:, vars_plot].plot(kind='box',
                                      subplots=True,
                                      layout = (2,3),
                                      figsize = (15, 15))
        plt.savefig(plot_file.absolute().as_posix(), dpi=300)


    if html:
        htmls_dir = output_dir.joinpath(project, 'htmls')
        htmls_dir.mkdir(parents = True, exist_ok = True)

        finished_download = download_qc_reports(lab, project, subjects, htmls_dir)

        print(finished_download)
