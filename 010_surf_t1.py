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




make_r1_surf(['LZ002'], tourettome_workspace, tourettome_freesurfer)

