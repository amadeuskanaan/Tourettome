__author__ = 'kanaan 01.01.2018'

import os
from utilities.utils import *
from variables.subject_list import *


# Calculate functional derivatives

### 1- Seed Correlation Analysis - STRIATUM
### 2- Seed Correlation Analysis - STR3_MOTOR
### 3- Seed Correlation Analysis - STR3_LIMBIC
### 4- Seed Correlation Analysis - STR4_EXEC

### 5- fALFF
### 6- ECM
### 7- DCM

#????

### 8- REHO
### 9- VHMC


def make_derivatives_func(population, workspace_dir, freesurfer_dir, derivatives_dir) :

    print '========================================================================================'
    print ''
    print '                    Tourettome - 007. STRUCTURAL FEATURES                               '
    print ''
    print '========================================================================================'

    count = 0
    for subject in population:
        count +=1

        print 'Extracting structural features for subject %s' %subject

        subject_dir     = os.path.join(workspace_dir, subject)
        ecm_dir         = mkdir_path(os.path.join(derivatives_dir, 'func_cenrality'))
        sca_dir         = mkdir_path(os.path.join(derivatives_dir, 'func_seedcorr'))
        alff_dir        = mkdir_path(os.path.join(derivatives_dir, 'func_alff'))

        print '#######################'
        print '1. Calculating Cenrality Measures '

        print '#######################'
        print '2. Calculating Seed Correlation Measures'

        seeds = ['STR', 'STR3_MOTOR', 'STR3_LIMBIC', 'STR3_EXECUTIVE',
                 'INSULA', 'ACC', 'M1', '']

        print '#######################'
        print '3. Calculating fractional Amplitude of low frequency fluctuations'










