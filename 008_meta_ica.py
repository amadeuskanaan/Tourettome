__author__ = 'kanaan 23.05.2017'

# -*- coding: utf-8 -*-
import os
import numpy as np
from variables.subject_list import *
from utilities.utils import *
from quality.motion_statistics import calculate_FD_Power

def prep_meta_ica(population, workspace):

    for subject in population:

        # Input/Output
        subject_dir = os.path.join(workspace, subject)
        ica_dir     = mkdir_path(os.path.join(subject_dir, 'ICA'))
        func_2mm    = os.path.join(subject_dir,'REGISTRATION', 'REST_EDIT_UNI_BRAIN_MNI2mm.nii.gz')

        os.chdir(ica_dir)

        # Resample data to 4mm
        #os.system('flirt -in %s -ref %s -applyisoxfm 4 -nosearch -out REST_EDIT_UNI_BRAIN_MNI4mm'%(func_2mm, mni_brain_2mm))

        # Cut data to shortest time-point length
        ### n_vols: PA=196; LZ=418; HA=271; HB=174
        ### TR: PA=2.4; LZ=1.4; HA=2.0; HA=2.4; HB= 2.0. Average TR=2.05
        #os.system('fslroi REST_EDIT_UNI_BRAIN_MNI4mm REST_EDIT_UNI_BRAIN_MNI4mm_n174 0 174')

        # Calculate mean_FD for the modified time-series
        movpar = os.path.join(subject_dir, 'FUNCTIONAL', 'moco/REST_EDIT_moco2.par')
        FD = calculate_FD_Power(movpar)
        print FD
        print np.mean(FD)
        print np.mean(FD[:174])

prep_meta_ica(['LZ030'], tourettome_workspace)






