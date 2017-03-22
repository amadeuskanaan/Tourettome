__author__ = 'kanaan 22.03.2017'

import os
from variables.subject_list import *
from utils.utils import *
from denoise.nuisance import *

import nipype
from nipype.utils import config
import CPAC



def nuisance_signal_regression(population, workspace_dir):

    for subject in population:
        print '###############################################################################'
        print 'Denoising Functional Data for subject %s' % subject
        print ''


        #input
        subdir           = os.path.join(workspace_dir, subject)
        func_native      = os.path.join(subdir, 'FUNCTIONAL/REST_EDIT_MOCO_BRAIN.nii.gz')
        func_native_mask = os.path.join(subdir, 'FUNCTIONAL/REST_EDIT_MOCO_BRAIN_MASK.nii.gz')
        func_native_wm   = os.path.join(subdir, 'FUNCTIONAL/REST_EDIT_MOCO_BRAIN_MASK.nii.gz')
        func_native_csf  = os.path.join(subdir, 'FUNCTIONAL/REST_EDIT_MOCO_BRAIN_MASK.nii.gz')

        #output
        nuisance_dir = mkdir_path(os.path.join(subdir, 'DENOISE'))


        # calculate friston paramters
        movpar  = os.path.join(subdir, 'FUNCTIONAL/REST_EDIT_moco2.1D' )
        friston = os.path.join(subdir, 'FUNC_DENOISE/FRISTON_24.1D')
        if not os.path.isfile(friston):
            calc_friston_twenty_four(movpar)

        # denoise native func
        print 'Denoising native functional'
        nuisance_dir_native = mkdir_path(os.path.join(nuisance_dir, 'native'))
        os.chdir(nuisance_dir_native)




