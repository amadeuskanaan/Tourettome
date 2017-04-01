__author__ = 'kanaan_02.12.2016'

import os
import sys

from utilities.utils import mkdir_path
from variables.subject_list import *


#assert len(sys.argv)== 2
#subject_index=int(sys.argv[1])

def preprocess_anatomical(population, afs_dir, workspace, freesurfer_dir):

    for subject in population:
        #subject = population[subject_index]
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

            # Runs thick2surf

            if not os.path.isfile(os.path.join(freesurfer_dir, "CT", "%s_rh2fsaverage5_20.mgh" %subject)):
                print '.... Running thick2surf'
                os.system('sh /scr/sambesi1/workspace/Projects/Tourettome/quality/thick2surf.sh %s %s %s %s %s'
                          %(subject,
                            os.path.join(freesurfer_dir, subject),
                            '20',  # FWHM
                            os.path.join(freesurfer_dir, 'CT'),
                            '5'    # FSAVERAGE5
                            ))


preprocess_anatomical(population = ['HA002'], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)












