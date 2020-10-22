#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 13:22:12 2020

@author: Javi Rasero, adapted by Krista Bond.
"""

import flywheel

def download_qc_reports(lab, project, html_dir):


    api_key = 'bridge-center.flywheel.io:EnMp3OeZ0By95NuStL'
    fw = flywheel.Client(api_key)


    pid = fw.lookup(lab + '/' + project).id


    for subject in fw.get_project_subjects(project_id=pid):
        for session in fw.get_subject_sessions(subject.id):
            for acq in fw.get_session_acquisitions(session.id):
                mod = ''
                if 'func-bold_task-lokicat_run-' in acq.label:
                    mod = 'loki1'
                elif acq.label == 'anat-T1w_acq-mprage':
                    mod = 't1'

                print('acq label: ', acq.label)
                print('mod: ', mod)

                if mod:
                    for file in acq.files:
                        if (file.type == 'qa') & (file.name.endswith('.html')):
                            output_dir = html_dir.joinpath('sub-' + subject.label,
                                                           session.label)
                            output_dir.mkdir(parents = True, exist_ok=True)

                            print("Downloading html report for subject {}, "
                                  "session {} and modality {}".format(subject.label,
                                                                      session.label,
                                                                      mod)
                                  )

                            dest_file = output_dir.joinpath(mod + "_" + file.name)
                            file.download(dest_file.absolute().as_posix())

            print(" ")


    return "html reports have been downloaded"
