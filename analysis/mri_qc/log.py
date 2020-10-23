#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Functions to create the log QC info. Adapted by Javi Rasero & Krista Bond. Created by Tim Verstynen.

"""
import pandas as pd
import flywheel


def epi_log(acq, date, subject, session, df):
    for files in acq.files:
        if files.type == 'qa':

            #this is to correct lack of timestamp in flywheel
            if acq.timestamp:
                timestamp = acq.timestamp.timestamp()
            else:
                timestamp = "n/a"

            df = df.append({
                "date": date.date(),
                "timestamp": timestamp,
                "subject": subject.label,
                "session": session.label,
                "tsnr": files.info.get('tsnr'),
                "fwhm_avg": files.info.get('fwhm_avg'),
                "dvars_nstd": files.info.get('dvars_nstd'),
                "fd_mean": files.info.get('fd_mean'),
                "gcor": files.info.get('gcor'),
                "snr": files.info.get('snr')
                }, ignore_index=True)

    return df

def t1_log(acq, date, subject, session, df):
    for files in acq.files:
        if files.type == 'qa':

            #this is to correct lack of timestamp in flywheel
            if acq.timestamp:
                timestamp = acq.timestamp.timestamp()
            else:
                timestamp = "n/a"

            df = df.append({
                "date": date.date(),
                "timestamp": timestamp,
                "subject": subject.label,
                "session": session.label,
                "cnr": files.info.get('cnr'),
                "fwhm_avg": files.info.get('fwhm_avg'),
                "snr_total": files.info.get('snr_total'),
                "snrd_total": files.info.get('snrd_total'),
                }, ignore_index=True)

    return df

def create_log_files(lab, project):


    api_key = ''
    fw = flywheel.Client(api_key)

    pid = fw.lookup(lab + '/' + project).id


    vars_epi = ['subject', 'session', 'date','timestamp', 'tsnr',
               'fwhm_avg','dvars_nstd','fd_mean','gcor','snr']
    vars_t1 = ['subject', 'session', 'date','timestamp',
              'cnr','fwhm_avg','snr_total','snrd_total']

    if 'LOKI1'in project:
        RL_task_df = pd.DataFrame(columns=vars_epi)

    t1_df = pd.DataFrame(columns=vars_t1)

    acq_labels = []
    #T1:  cnr, fwhm_avg, snr_total, snrd_total
    #BOLD image: dvars_nstd, fd_mean, fwhm_avg, gcor, snr, tsnr
    for subject in fw.get_project_subjects(project_id=pid):
        for session in fw.get_subject_sessions(subject.id):
            for acquisition in fw.get_session_acquisitions(session.id):
                acq = fw.get_acquisition(acquisition.id)
                date = acq.created
                acq_labels.append(acq.label)

                if 'func-bold_task-lokicat_run-' in acq.label:
                    RL_task_df = epi_log(acq, date, subject, session, RL_task_df)
                elif acq.label == 'anat-T1w_acq-mprage':
                    t1_df = t1_log(acq, date, subject, session, t1_df)

    print(acq_labels)
    # Save these dataframes to a dictionary

    if 'LOKI1' in project:
        qc_log_dict = {'RL_task': RL_task_df.loc[:, vars_epi],
                       't1': t1_df.loc[:, vars_t1]}
    else:
        qc_log_dict = {'t1': t1_df.loc[:, vars_t1]}


    return qc_log_dict
