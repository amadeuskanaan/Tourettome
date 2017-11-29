__author__ = 'kanaan 21.04.2017_____ Island-Lifestyle-Cafe, Honolulu, Hawaii!'

import os
from variables.subject_list import *

def extract_seed_timeseries(population, workspace):

    for subject in population:

        print 'Extracting timeseries'

        #I/O
        subject_dir   = os.path.join(workspace, subject)
        func_denoised = os.path.join(subject_dir, 'DENOISE', 'REST_MNI2mm_detrend_wmcsf_moco24_bp.nii.gz')





os.system('3dROIstats -quiet -mask_f2short -mask %s %s > rest_native.1d'%(mask, pproc))