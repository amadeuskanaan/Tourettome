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

def make_derivatives_struct(population, workspace_dir, fs_dir, derivatives_dir) :

    print '========================================================================================'
    print ''
    print '                    Tourettome - 007. STRUCTURAL FEATURES                               '
    print ''
    print '========================================================================================'

    count = 0
    for subject in population:
        count +=1

        print '##################################'
        print 'Extracting structural features for subject %s' %subject

        fs_dir  = os.path.join(fs_dir, subject)
        ct_dir  = mkdir_path(os.path.join(derivatives_dir, 'struct_cortical_thickness'))
        vol_dir = mkdir_path(os.path.join(derivatives_dir, 'struct_subcortical_volume'))

        ################################################################################################################
        ### 1- Cortical Thickness
        ################################################################################################################

        if not os.path.isfile(os.path.join(ct_dir, '%s_ct2fsaverage5_fwhm20_rh.mgh'%subject)):
            print '1- Extracting Cortical Thickness'
            FWHM_CT = '20'
            fsaverage = 'fsaverage5'

            if os.path.isfile(os.path.join(fs_dir, 'surf/lh.thickness')):
                for hemi in ['lh', 'rh']:
                        surf2surf = ['mri_surf2surf ',
                                     '--s '          + subject,
                                     '--sval '       + os.path.join(fs_dir, 'surf/%s.thickness' % hemi),
                                     '--hemi '       + hemi,
                                     '--trgsubject ' + fsaverage,
                                     '--fwhm-src '   + FWHM_CT,
                                     '--tval '       + os.path.join(ct_dir, '%s_ct2%s_fwhm%s_%s.mgh' %
                                                                    (subject, fsaverage, FWHM_CT, hemi)),
                                     '--cortex '
                                     '--noreshape ']
                        os_system(surf2surf)

            else:
                print '..........Subject missing reconall data'
        ################################################################################################################
        ### 2- Subcortical Volume
        ################################################################################################################

        aseg_stats_out = os.path.join(vol_dir, 'aseg_stats_%s.txt'%subject)
        if not os.path.isfile(aseg_stats_out):
            print '2- Extracting Subcortical Volumes'
            if os.path.isfile(os.path.join(fs_dir, 'stats/aseg.stats')):
                os.system('asegstats2table -s %s --meas volume --delimiter comma -t %s'
                      %(subject,  aseg_stats_out))
            else:
                print '..........Subject missing reconall data'

tourettome_freesurfer = '/data/pt_nmr093_gts/freesurfer'
make_derivatives_struct(['PA050'], tourettome_workspace, tourettome_freesurfer, tourettome_derivatives )