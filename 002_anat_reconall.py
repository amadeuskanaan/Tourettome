__author__ = 'kanaan_02.12.2016'

import os
import sys

from utilities.utils import mkdir_path
from variables.subject_list import *


assert len(sys.argv)== 2
subject_index=int(sys.argv[1])

def preprocess_anatomical(population, afs_dir, workspace, freesurfer_dir):

    #for subject in population:
        subject = population[subject_index]
        print '========================================================================================'
        print '%s-Preprocessing anatomical data for %s' %(subject, subject)

        # input
        anatdir = mkdir_path(os.path.join(workspace, subject, 'ANATOMICAL'))

        # Freesurfer Reconall
        ## For best results across the multi-site data, Reconall is run on skull stripped Anatomical data.
        ## This is mainly done since stripping out-of-head noise on MP2RAGE data usually fails with BET algorithms.
        ## Erroneous segmentation may also occur for MP2RAGE data with abnormal morphology

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

            # # Runs thick2surf
            # if not os.path.isfile(os.path.join(freesurfer_dir, "CT", "%s_rh2fsaverage5_20.mgh" %subject)):
            #     print '.... Running thick2surf'
            #     os.system('sh /scr/sambesi1/workspace/Projects/Tourettome/surfstats/thick2surf.sh %s %s %s %s %s'
            #               %(subject,
            #                 os.path.join(freesurfer_dir, subject),
            #                 '20',  # FWHM
            #                 os.path.join(freesurfer_dir, 'CT'),
            #                 '5'    # FSAVERAGE5
            #                 ))

            #  # Runs recon-checker
            # if not os.path.isfile(os.path.join(freesurfer_dir, 'QA', subject, 'rgb/snaps/%s.html'%subject)):
            #
            #     # Source freesurfer
            #     os.system('export SUBJECTS_DIR=%s'%freesurfer_dir)
            #     os.system('export QA_TOOLS=/scr/sambesi1/Software/QAtools_v1.2')
            #     os.system('$QA_TOOLS/recon_checker -s %s -snaps-out -snaps-detailed -gen-outputFOF'%(subject))

# recon_checker = [subject for subject in tourettome_subjects if subject not in missing]

#preprocess_anatomical(population = leipzig[1:], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
# preprocess_anatomical(population = leipzig[30:50], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
# preprocess_anatomical(population = leipzig[52:], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
# preprocess_anatomical(population = leipzig[65:], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
# preprocess_anatomical(population = hamburg, afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
# preprocess_anatomical(population = hannover_b, afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
# preprocess_anatomical(population = hannover_b[20:], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
# preprocess_anatomical(population = hannover_a[0:30], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
# preprocess_anatomical(population = hannover_a[30:], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
# preprocess_anatomical(population =paris[0:25], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
#preprocess_anatomical(population =paris[25:50], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
# preprocess_anatomical(population =paris[50:75], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
# preprocess_anatomical(population =paris[75:], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)
preprocess_anatomical(population = leipzig[20:22], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)