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

        # Deskull
        os.system('fslmaths %s -mul %s T1MAPS_brain.nii.gz '%(T1MAPS, mask))
        # Swapdim
        os.system('fslswapdim T1MAPS_brain LR SI PA T1MAPS_brain_rsp')
        # get fs t1
        os.system('mri_convert %s T1mgz.nii.gz'%T1MGZ)
        # reg
        os.system('flirt -in T1MAPS_brain_rsp -ref T1mgz -dof 6 -cost mutualinfo -out T1MAPS_fs -omat NATIVE2FS.mat')

        #get reciprocal
        os.system('fslmaths T1MAPS_fs -recip R1')
        os.system('mri_convert R1.nii.gz R1.mgz')

        proj_fracs = {'depth1': '0.0 0.2 0.2',
                      'depth2': '0.2 0.4 0.2',
                      'depth3': '0.4 0.6 0.2',
                      'depth4': '0.6 0.8 0.2',
                      'depth5': '0.8 1.0 0.2'}

        fwhm = 6

        # vol2surf iterate of six laminar layers
        for hemi in ['lh', 'rh']:

            for depth in proj_fracs.keys():

                os.system('mri_vol2surf '
                          '--mov R1.mgz '
                          '--regheader %s '
                          '--icoorder 5 '
                          '--projfrac-avg %s '
                          '--interp nearest'
                          '--hemi %s'
                          '--out %s_%s_%s_R1.mgh'
                          %(subject, proj_fracs[depth], subject,
                            subject, depth, hemi)
                          )

                os.system('mri_vol2surf '
                          '--s %s '
                          '--trgsubject fsaverage5 '
                          '--tval %s_%s_%s_fsavarege_%sfwhm.mgh'
                          '--fwhm %s '
                          '--noreshape '
                          '--cortex'
                          %(subject,
                            subject, depth, hemi, fwhm,
                            fwhm
                            ))

make_r1_surf(['LZ002'], tourettome_workspace, tourettome_freesurfer)

