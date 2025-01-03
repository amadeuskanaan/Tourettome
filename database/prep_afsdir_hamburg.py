__author__ = 'kanaan_01.07.2017'

import os, sys
sys.path.append(os.path.expanduser('/scr/malta1/Github/Tourettome'))
import pandas as pd
from utilities.utils import *
from variables.subject_list_original import *

def prep_hamburg_data(population, original_datadir, afs_dir):

    print '###########################################'
    print '  Creating clean folders for HAMBURG data'
    print '###########################################'

    count = 0
    HM_subjects = dict()

    for subject in population:
        count += 1
        HM_subjects[subject] = subject

        print subject

        for group in ['probands', 'patients']:
            if os.path.isdir(os.path.join(original_datadir, group, subject)):
                orig_nifti_dir = os.path.join(original_datadir, group, subject)
                group_id =  group

        subject_dir = mkdir_path(os.path.join(afs_dir, subject))
        nifti_dir = mkdir_path(os.path.join(subject_dir, 'NIFTI'))
        os.chdir(nifti_dir)

        rest_dir  = os.path.join(orig_nifti_dir, 'Rest1')
        anat_dir  = os.path.join(orig_nifti_dir, 'T1')

        if not os.path.isfile(os.path.join(nifti_dir, 'ANATOMICAL.nii.gz')):
            # convert all img/hdr to nifti
            os.system('fslmerge -t REST_.nii.gz %s/*hdr' %rest_dir)
            os.system('fslchfiletype NIFTI %s/*hdr ANATOMICAL_.nii.gz' %anat_dir)

            # swap dims
            os.system('fslswapdim ANATOMICAL_ RL PA IS ANATOMICAL')
            os.system('fslswapdim REST_ RL PA IS REST')
            os.system('rm -rf *_*')

            # quick reg
            os.system('flirt -in REST -ref ANATOMICAL -dof 6 -cost corratio -out test_func2anat')

        # create subject dataframe
        columns = ['Name', 'Site', 'Group', 'ScanDate', 'Scanner', 'NCoils', 'Sequence', 'TR',
                   'TE', 'Resolution', 'NVols', 'FlipAngle']
        df = pd.DataFrame(index=['%s' % subject], columns=columns)

        if group_id =='patients':
            group_id = 'patients'
        elif group_id =='probands':
            group_id = 'controls'

        df.loc['%s' % subject] = pd.Series({'Name'      : subject,
                                               'Group'     : group_id,
                                               #'Age'       : '', This column is grabeed from the clinical df
                                               #'Sex'       : '', This column is grabeed from the clinical df
                                               'ScanDate'  : '3.5x3.5x3',
                                               'Scanner'   : '3T-SIEMENS-Trio',
                                               'Sequence'  : 'EPI-REST',
                                               'NCoils'    : '12',
                                               'TR'        : '2.28',
                                               'TE'        : '30',
                                               'Resolution': '',
                                               'NVols'     : '75',
                                               'FlipAngle' : '80',
                                               'Site'      : 'HAMBURG'
                                               })

        df.to_csv(os.path.join(subject_dir, '%s_param.csv' % subject))

    print HM_subjects

    # grab all header info into one df
    param_group = []
    for subject in population:
        param_subject = pd.read_csv( os.path.join(afs_dir, HM_subjects[subject], '%s_param.csv' % HM_subjects[subject]),index_col=0)
        param_group.append(param_subject)

    param_group = pd.concat(param_group, ignore_index=False)  # .sort(columns='Age')
    param_group.to_csv(os.path.join(tourettome_phenotypic, 'df_dcm/dicomhdr_hamburg.csv'))

prep_hamburg_data(sorted(HMABURG_CONTROLS+HAMBURG_PATIENTS), HAMBURG_orig_datadir , tourettome_afs)