__author__ = 'kanaan 23.03.2017'

import os
import numpy as np

from utilities.utils import *
from variables.subject_list import *
from motion.motion_statistics import *



def generate_motion_stats(population, workspace):


    for subject in population:
        print '###############################################################################'
        print 'Denoising Functional Data for subject %s' % subject
        print ''


        #input
        subdir = os.path.join(workspace, subject)
        movpar = os.path.join(subdir, 'FUNCTIONAL/moco/REST_EDIT_moco2.1D')
        maxdsp = os.path.join(subdir, 'FUNCTIONAL/moco/REST_EDIT_moco2_MX.1D')
        func_pproc   = os.path.join(subdir, 'FUNCTIONAL/moco/REST_EDIT_moco2_MX.1D')
        func_denoise = os.path.join(subdir, 'FUNCTIONAL/moco/REST_EDIT_moco2_MX.1D')

        #output
        qcdir = mkdir_path(os.path.join(subdir, 'QUALITY'))
        os.chdir(qcdir)

        #calculate Framewise-Displacment
        calculate_FD_Power(movpar)

        #calculate DVARS
        calculate_DVARS()



generate_motion_stats(['PA013'], tourettome_workspace)