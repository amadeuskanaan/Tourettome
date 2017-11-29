__author__ = 'kanaan_16.04.2017'

import os
import sys

from utilities.utils import mkdir_path
from variables.subject_list import *



def make_r1_surf(population, workspace, freesurfer_dir):

    for subject in population:
        print '========================================================================================'
        print '%s-Preprocessing T1MAPSfor %s' %(subject, subject)

        # I/O
        T1MAPS = os.path.join(workspace, subject, 'RAW', 'T1MAPS.nii.gz')
        T1MGZ  = os.path.join(freesurfer_dir, subject, 'mri', 'T1.mgz')
        mask   = os.path.join(workspace, subject, 'ANATOMICAL','ANATOMICAL_BRAIN_MASK.nii.gz')
        t1_dir = mkdir_path(os.path.join(workspace, subject, 'T1MAPS'))

        os.chdir(t1_dir)

        if not os.path.isfile(os.path.join(t1_dir, 'R1.mgz')):
            # Deskull
            os.system('fslmaths %s -mul %s T1MAPS_brain.nii.gz '%(T1MAPS, mask))
            # Swapdim
            os.system('fslswapdim T1MAPS_brain LR SI PA T1MAPS_brain_rsp')
            # get fs t1
            os.system('mri_convert %s T1mgz.nii.gz'%T1MGZ)
            # reg
            os.system('flirt -in T1MAPS_brain_rsp -ref T1mgz -dof 6 -cost mutualinfo -out T1MAPS_fs -omat NATIVE2FS.mat')

            #get reciprocal
            os.system('fslmaths T1MAPS_fs -recip -mul 10000 R1')
            os.system('mri_convert R1.nii.gz R1.mgz')

        #mri_vol2surf --mov R1.mgz --regheader LZ050 --projfrac 0.2 0.4 0.1 --hemi --interp nearest --out depth2.mgh
        #mri_surf2surf --s LZ050 --sval depth2.mgh --trgsubject fsaverage5 --tval depth2_fs5.mgh --fwhm 6 --hemi lh --cortex


        proj_fracs = {'depth1': '0.0 0.2 0.1', 'depth2': '0.2 0.4 0.1','depth3': '0.4 0.6 0.1',
                      'depth4': '0.6 0.8 0.1', 'depth5': '0.8 1.0 0.1'}
        fwhm = 6

        # vol2surf iterate of five laminar layers
        if not os.path.isfile(os.path.join(t1_dir, '%s_depth5_rh_R1.mgh' % subject)):
            for hemi in ['lh', 'rh']:
                for depth in proj_fracs.keys():
                    print hemi, proj_fracs

                    os.system('mri_vol2surf --mov R1.mgz --regheader %s --projfrac-avg %s --interp nearest --hemi %s '
                              '--out %s_%s_%s_R1.mgh '
                              %(subject, proj_fracs[depth], hemi,
                                subject, depth, hemi,
                                ))

                    os.system('mri_surf2surf --s %s --sval  %s_%s_%s_R1.mgh --trgsubject fsaverage5 '
                              '--tval %s_%s_%s_fs5_R1.mgh --hemi %s --noreshape --cortex --fwhm %s '
                              %(subject,
                                subject, depth, hemi,
                                subject, depth, hemi,
                                hemi,
                                fwhm,
                                ))


        ################################################################################################################
        ################################################################################################################
        ################################################################################################################

#         qsm_dir = mkdir_path(os.path.join(workspace, subject, 'QSM'))
#
#         if not os.path.isfile('QSMnorm2FS_rsp.mgz'):
#             # Grab T1 from Tourettome freesurfer dir
#
#             # invert xfm
#             os.system('convert_xfm -omat NATIVE2FS.mat -inverse %s'
#                       % (os.path.join(subject_dir, 'SEGMENTATION/FREESURFER/FS2NATIVE.mat')))
#
#             # concat xfms
#             os.system('convert_xfm -omat QSM2FS.mat -concat NATIVE2FS.mat %s'
#                       % (os.path.join(subject_dir, 'REGISTRATION', 'FLASH', 'FLASH2MP2RAGE.mat')))
#
#             # trasnform qsm to mp2rage space
#             os.system('flirt -in %s -ref T1_RPI -applyxfm -init QSM2FS.mat -out QSMnorm2FS.nii.gz'
#                       % (os.path.join(subject_dir, 'QSM', 'QSM_norm.nii.gz')))
#
#             # swapdim
#             os.system('fslswapdim QSMnorm2FS RL SI PA QSMnorm2FS_rsp')
#
#             # convert to mgz
#             os.system('mri_convert QSMnorm2FS_rsp.nii.gz QSMnorm2FS_rsp.mgz')
#
# make_r1_surf(leipzig, tourettome_workspace, tourettome_freesurfer)
#
