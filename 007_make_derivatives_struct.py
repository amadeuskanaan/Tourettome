__author__ = 'kanaan 01.01.2018'

import os
from utilities.utils import *
from variables.subject_list import *

# Calculate structural derivatives for classification
# Cortical Features include
### 1- Cortical Thickness
### 2- Geodesic Distance
### 3- Subcortical Volume
### 4- Surface Area



def make_derivatives_struct(population, workspace_dir, freesurfer_dir, derivatives_dir) :

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
        freesurfer_dir  = os.path.join(freesurfer_dir, subject)
        ct_dir          = mkdir_path(os.path.join(derivatives_dir, 'cortical_thickness'))


        print '##################################'
        print '1- Extracting Cortical Thickness'

        FWHM_CT = '20'
        fsaverage = 'fsaverage5'

        for hemi in ['lh', 'rh']:
            surf2surf = ['mri_surf2surf ',
                         '--s '          + subject,
                         '--sval '       + os.path.join(freesurfer_dir, 'surf/%s.thickness'%hemi),
                         '--hemi '       + hemi,
                         '--trgsubject ' + fsaverage,
                         '--fwhm-src '   + FWHM_CT,
                         '--tval '       + os.path.join(ct_dir, '%s_%s2%s_fwhm%s.mgh' % (subject,hemi, fsaverage, FWHM_CT)),
                         '--cortex '
                         '--noreshape '
                         ]

            print ' '.join(surf2surf)

        print '##################################'
        print '2- Extracting Geodesic Distance'



make_derivatives_struct(['PA005'], tourettome_workspace, tourettome_freesurfer, tourettome_derivatives )