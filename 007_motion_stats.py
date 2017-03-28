__author__ = 'kanaan 23.03.2017'

import os
import numpy as np
from utilities.utils import *
from variables.subject_list import *
from motion.motion_statistics import *
from nipype.algorithms.misc import TSNR


def quality_control(population, workspace):


    for subject in population:
        print '###############################################################################'
        print 'Denoising Functional Data for subject %s' % subject
        print ''


        #input
        subdir       = os.path.join(workspace, subject)
        movpar       = os.path.join(subdir, 'FUNCTIONAL', 'moco/REST_EDIT_moco2.par')
        maxdsp       = os.path.join(subdir, 'FUNCTIONAL', 'moco/REST_EDIT_moco2_MX.1D')
        gm           = os.path.join(subdir, 'REGISTRATION', 'ANATOMICAL_GM_MNI2mm.nii.gz')
        func_edit    = os.path.join(subdir, 'FUNCTIONAL', 'REST_EDIT_MOCO_BRAIN.nii.gz')
        func_wmcsf   = os.path.join(subdir, 'DENOISE', 'REST_MNI2mm_detrend_wmcsf_moco24_bp.nii.gz')
        func_compcor = os.path.join(subdir, 'DENOISE', 'REST_MNI2mm_detrend_compcor_moco24_bp.nii.gz')
        func_aroma   = os.path.join(subdir, 'DENOISE', 'REST_MNI2mm_fwhm_aroma_detrend_compcor_moco24_bp.nii.gz')

        #output
        qcdir = mkdir_path(os.path.join(subdir, 'QUALITY'))
        os.chdir(qcdir)

        #######################################
        # Calculate Framewise-Displacment
        FD1D = np.loadtxt(calculate_FD_Power(movpar))
        frames_in = [ frame for frame, val in enumerate(FD1D) if val<0.2]

        print frames_in

        #######################################
        # Calculate DVARS
        if not os.path.isfile(DVARS):
            DVARS = calculate_DVARS(func_wmcsf, gm)

        #######################################
        if not os.path.isfile(os.path.join(qcdir, 'REST_PPROC_NATIVE_BRAIN_tsnr.nii.gz')):
            tsnr = TSNR()
            tsnr.inputs.in_file = func_edit
            tsnr.run()






quality_control(['PA072'], tourettome_workspace)