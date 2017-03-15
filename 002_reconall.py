__author__ = 'kanaan_02.12.2016'

import os
from utilities.utils import mkdir_path
from variables.subject_list import *
import shutil
import sys
import nipype.interfaces.spm as spm

# Function to preprocess multi-site anatomical data (mprage and mp2rage)
# Needs FSL5, AFNI, SPM, FREESURFER, pyenv

assert len(sys.argv)== 2
subject_index=int(sys.argv[1])

def preprocess_anatomical(population, afs_dir, workspace, freesurfer_dir):
    #count = 0
    #for subject in population:
        subject = population[subject_index]
        #count += 1
        print '========================================================================================'
        print '%s-Preprocessing anatomical data for %s' %(subject, subject)

        # input
        anatdir = mkdir_path(os.path.join(workspace, subject, 'ANATOMICAL'))

        # Freesurfer Reconall
        ## For best results across the multi-site data, Reconall is run on skull stripped Anatomical data.
        ## This is mainly done since stripping out-of-head noise on MP2RAGE data usually fails with BET algorithms.
        if freesurfer_dir:
            if not os.path.isfile(os.path.join(freesurfer_dir, subject, 'mri', 'aparc.DKTatlas+aseg.mgz' )):
                print '... Running Freesurfer'
                from nipype.workflows.smri.freesurfer import create_skullstripped_recon_flow
                os.system('rm -rf %s' %(os.path.join(freesurfer_dir, subject)))
                recon_flow = create_skullstripped_recon_flow()
                recon_flow.inputs.inputspec.subject_id = subject
                recon_flow.inputs.inputspec.T1_files = os.path.join(anatdir, 'ANATOMICAL_BRAIN.nii.gz')
                recon_flow.inputs.inputspec.subjects_dir = freesurfer_dir
                recon_flow.run()
        else:
            print '....subject reconalled'

# test_sample = ['HB003']
# test_sample = ['HA001']
#test_sample = ['LZ002']
# test_sample = ['PA010']
xall = leipzig+paris+hannover_a + hannover_b
# preprocess_anatomical(population = hannover_a, afs_dir = afs_dir, workspace = workspace_dir, freesurfer_dir= freesurfer_dir)

xall = ['HB001', 'HB002', 'HB003', 'HB004', 'HB005', 'HB008', 'HB011', 'HB014', 'HB015', 'LZ001',
        'LZ008', 'LZ040', 'LZ044', 'LZ045', 'LZ052', 'LZ053', 'LZ057', 'LZ058', 'LZ062', 'LZ066',
        'LZ072', 'PA055']
preprocess_anatomical(population = xall, afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
# preprocess_anatomical(population = leipzig, afs_dir = afs_dir, workspace = workspace_dir, freesurfer_dir= freesurfer_dir)
# preprocess_anatomical(population = paris, afs_dir = afs_dir, workspace = workspace_dir, freesurfer_dir= freesurfer_dir)












