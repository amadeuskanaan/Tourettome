__author__ = 'kanaan_02.12.2016'

import os
import shutil
import numpy as np
import nibabel as nb
import pandas as pd
import nipype.interfaces.spm as spm

from utilities.utils import mkdir_path
from variables.subject_list import *


# Function to preprocess multi-site anatomical data (mprage and mp2rage)
# Needs FSL5, AFNI, SPM, FREESURFER, pyenv


def preprocess_anatomical(population, workspace):

    print '========================================================================================'
    print ''
    print '                    Tourettome - 001.Anatomical Data PreProcessing                      '
    print ''
    print '========================================================================================'


    for subject in population:
        print '========================================================================================'
        print '-Preprocessing anatomical data for %s' %subject

        rawdir    = mkdir_path(os.path.join(workspace, subject, 'RAW'))
        anatdir   = mkdir_path(os.path.join(workspace, subject, 'ANATOMICAL'))
        spmdir    = mkdir_path(os.path.join(anatdir, 'seg_spm'))
        firstdir  = mkdir_path(os.path.join(anatdir, 'seg_first'))


        ####### RUN SPM SEGMENTATION

        if not os.path.isfile(os.path.join(spmdir, 'c1ANATOMICAL.nii')):

            ### Deoblique ###  Replace transformation matrix in header with cardinal matrix.This option DOES NOT deoblique the volume.
            os.system('3drefit -deoblique %s' %os.path.join(rawdir, 'ANATOMICAL.nii.gz'))


            ### SEGMENT
            if not os.path.isfile(os.path.join(spmdir, 'mANATOMICAL.nii')):

                print '..... Running SPM segmentation'

                os.chdir(spmdir)
                shutil.copy(os.path.join(rawdir, 'ANATOMICAL.nii.gz'), os.path.join(spmdir, 'ANATOMICAL.nii.gz'))
                os.system('fslchfiletype NIFTI %s' % os.path.join(spmdir, 'ANATOMICAL'))

                seg = spm.NewSegment()
                seg.inputs.channel_files = os.path.join(spmdir, 'ANATOMICAL.nii')
                seg.inputs.channel_info = (0.0001, 60, (True, True))
                seg.base_dir = spmdir
                seg.run()


        ####### DESKULL data using segmentation

        if not os.path.isfile(os.path.join(anatdir, 'ANATOMICAL_BRAIN.nii.gz')):

            print '..... Deskulling'

            os.chdir(spmdir)
            os.system('fslmaths c1ANATOMICAL -thr 0.1 -bin c1ANATOMICAL_thr01')
            os.system('fslmaths c2ANATOMICAL -thr 0.1 -bin c2ANATOMICAL_thr01')
            os.system('fslmaths c3ANATOMICAL -thr 0.9 -bin c3ANATOMICAL_thr09')
            os.system('fslmaths c1ANATOMICAL_thr01 -add c2ANATOMICAL_thr01 -add c3ANATOMICAL_thr09 -bin -fillh -s 3 -thr 0.4 -bin ../ANATOMICAL_BRAIN_MASK')
            os.system('fslmaths mANATOMICAL -mas ../ANATOMICAL_BRAIN_MASK ../ANATOMICAL_BRAIN')


        ####### OPTIMIZE masks with FSL-FIRST subcortical segmentation

        if not os.path.isfile(os.path.join(anatdir, 'ANATOMICAL_GM.nii.gz')):

            print '..... Optimizing tissue masks'

            if not os.path.isfile(os.path.join(firstdir, 'FIRST_all_fast_firstseg.nii.gz')):
                os.chdir(firstdir)
                print '.........flirt anat2mni for priors'
                os.system('flirt -in ../ANATOMICAL_BRAIN.nii.gz -ref %s -omat anat2mni.mat -out anat2mni -cost mutualinfo -dof 12'%(mni_brain_1mm)) # no skulls. brain to brain.
                print '......... fsl-first'
                os.system('run_first_all -d -i ../ANATOMICAL_BRAIN -b -a anat2mni.mat -o FIRST')

            os.system('fslmaths FIRST_all_fast_firstseg -sub FIRST-BrStem_corr -bin FIRST')
            os.system('fslmaths %s/c1ANATOMICAL -thr 0.55 -bin -add FIRST -bin ../ANATOMICAL_GM'  %spmdir)
            os.system('fslmaths %s/c2ANATOMICAL -thr 0.9  -bin -sub FIRST -bin ../ANATOMICAL_WM'  %spmdir)
            os.system('fslmaths %s/c3ANATOMICAL -sub 0.9  -bin -sub FIRST -bin ../ANATOMICAL_CSF' %spmdir)



# for roi in mrs_rois:
#                 nucleus = os.path.join(workspace_dir, subject, 'SEGMENTATION/MRS/%s/%s_FLASH_BIN.nii.gz' % (roi,roi))
#                 if os.path.isfile(nucleus):
#                     mu = float(commands.getoutput('fslstats %s -k %s %s' % (img, nucleus, stat_type))) * XVAL
#                 else:
#                     mu = np.nan
#                 print roi, mu
#                 stats_df.loc[subject]['MRS_%s' % roi] = mu
#
#             stats_dir   = os.path.join(workspace_dir, subject, 'NUCLEUS_STATISTICS')
#             mkdir_path(stats_dir)
#
#             stats_df.ix[subject, 'Caud']  = np.mean((stats_df.loc['%s'%subject]['L_Caud'], stats_df.loc['%s'%subject]['R_Caud']))
#             stats_df.ix[subject, 'Puta']  = np.mean((stats_df.loc['%s'%subject]['L_Puta'], stats_df.loc['%s'%subject]['R_Puta']))
#             stats_df.ix[subject, 'Pall']  = np.mean((stats_df.loc['%s'%subject]['R_Pall'], stats_df.loc['%s'%subject]['L_Pall']))
#             stats_df.ix[subject, 'Amyg']  = np.mean((stats_df.loc['%s'%subject]['R_Amyg'], stats_df.loc['%s'%subject]['L_Amyg']))
#             stats_df.ix[subject, 'Hipp']  = np.mean((stats_df.loc['%s'%subject]['R_Hipp'], stats_df.loc['%s'%subject]['L_Hipp']))
#             stats_df.ix[subject, 'Accu']  = np.mean((stats_df.loc['%s'%subject]['R_Accu'], stats_df.loc['%s'%subject]['L_Accu']))
#             stats_df.ix[subject, 'Thal'] = np.mean((stats_df.loc['%s' % subject]['L_Thal'], stats_df.loc['%s' % subject]['R_Thal']))




        df = pd.DataFrame(index = ['count'], columns = rois)

        if not os.path.isfile(os.path.join(anatdir, 'sef_first/first_count.csv')):


            for roi in rois:
                count = np.count_nonzero(nb.load('FIRST-%s_first.nii.gz' %roi).get_data())

                df.ix['count','R_Caud'] = count


        print df







#preprocess_anatomical(population = ['HA053', 'HA054'], workspace = tourettome_workspace)
# preprocess_anatomical(population = tourettome_subjects , workspace = tourettome_workspace)
preprocess_anatomical(population = ['HA030'] , workspace = tourettome_workspace)

