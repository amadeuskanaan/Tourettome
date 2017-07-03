__author__ = 'kanaan_01.07.2017'

import os
from utilities.utils import *




def prep_hamburg_data(population, original_datadir, afs_dir):

    print '###########################################'
    print '  Creating clean folder for PARIS data'
    print '###########################################'


    count = 0
    HM_subjects = dict()

    for subject in population:
        count += 1

        for group in ['TS', 'Controls']:
            if os.path.isdir(os.path.join(original_datadir, group, subject)):
                orig_nifti_dir = os.path.join(original_datadir, group, subject)
                group_id =  group


        nifti_dir = mkdir_path(os.path.join(afs_dir, subject, 'NIFTI'))
        rest_dir = os.path.join(orig_nifti_dir, 'REST1')
        anat_dir = os.path.join(orig_nifti_dir, 'T1')


        os.chdir(nifti_dir)


        # convert all img/hdr to nifti
        os.system('fslmerge -t REST_.nii.gz %s/*' %rest_dir)
        os.system('fslchfiletype NIFTI %s/*hdr ANATOMICAL_.nii.gz' %anat_dir)

        # swap dims
        os.system('fslswapdim ANATOMICAL_ ANATOMICAL')
        os.system('fslswapdim REST_ REST')
        os.system('rm -rf *_*')

        # quick reg
        os.system('flirt -in REST -ref ANATOMICAL -dof 6 -cost corratio -out test_func2anat')



prep_hamburg_data(['HM001'],  , tourettome_afs)