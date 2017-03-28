__author__ = 'kanaan 23.03.2017'

import os

import numpy as np
import pandas as pd
from nipype.algorithms.misc import TSNR

from motion.motion_statistics import *
from utils import *


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
        # Calculate TSNR map
        if not os.path.isfile(os.path.join(qcdir, 'REST_PPROC_NATIVE_BRAIN_tsnr.nii.gz')):
            tsnr = TSNR()
            tsnr.inputs.in_file = func_edit
            tsnr.run()

        #######################################

        df = pd.Dataframe(index=subject, columns = ['FD', 'FD_in', 'FD_max', 'FD_q4', 'DVARS', 'TSNR' ])
        df.loc[subject]['FD']     = str(np.round(np.mean(FD1D), 3))
        df.loc[subject]['FD_in']  = str(np.round(len(frames_in), 3))
        quat = int(len(FD1D) / 4)
        df.loc[subject]['FD_topQua'] = str(np.round(np.mean(np.sort(FD1D)[::-1][:quat]), 3))
        df.loc[subject]['FD_max'] = str(np.round(np.max(FD1D), 3))
        df.loc[subject]['FD_RMS'] = str(np.round(np.sqrt(np.mean(FD1D)), 3))
        df.loc[subject]['DVARS'] = str(np.round(np.mean(np.load(DVARS)), 3))
        df.loc[subject]['TSNR'] = str(np.round(np.median(np.load('TSNR_data.npy')), 3))
        df.to_csv('quality_paramters.csv')



    """
Method to generate Power parameters for scrubbing

Parameters
----------
subject_id : string
    subject name or id
scan_id : string
    scan name or id
FD_ID: string
    framewise displacement(FD as per power et al., 2012) file path
FDJ_ID: string
    framewise displacement(FD as per jenkinson et al., 2002) file path
threshold : float
    scrubbing threshold set in the configuration
    by default the value is set to 1.0
DVARS : string
    path to numpy file containing DVARS





quality_control(['PA072'], tourettome_workspace)