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

            print os_system(surf2surf)

        print '##################################'
        print '2- Extracting Geodesic Distance'

        print '##################################'
        print '3- Extracting Surface Area'

        print '##################################'
        print '4- Extracting Intensity Contrast'

        print '##################################'
        print '5- Extracting Subcortical Volumes'

        # ####### Count number of non-zero voxels for FSL-FIRST subcortical segmentations
        #
        # # create bilateral masks
        # for roi in ['Caud', 'Puta', 'Pall',  'Amyg', 'Hipp', 'Accu', 'Thal']:
        #     if not os.path.isfile(os.path.join(anatdir, 'seg_first/FIRST-%s_first.nii.gz'%roi)):
        #         os.chdir(firstdir)
        #         os.system('fslmaths FIRST-R_%s_first.nii.gz -add FIRST-L_%s_first.nii.gz -bin FIRST-%s_first.nii.gz' %(roi, roi, roi))
        #
        # # Get jacobian deteminant from anat2mni.mat and multiply by bincount
        # jacobian_det = np.linalg.det(np.genfromtxt(os.path.join(anatdir, 'seg_first', 'anat2mni.mat')))
        # print jacobian_det
        #
        # # Make count
        # df = pd.DataFrame(index = ['%s'%subject], columns = rois)
        # if not os.path.isfile(os.path.join(anatdir, 'seg_first/first_count_jac.csv')):
        #     for roi in rois:
        #         first = os.path.join(firstdir,'FIRST-%s_first.nii.gz' %roi )
        #         count = np.count_nonzero(nb.load(first).get_data()) * jacobian_det
        #         df.ix['%s'%subject, roi] = count
        #
        # df.to_csv(os.path.join(firstdir, 'bin_count_jac.csv'))
        # print df


make_derivatives_struct(['PA005'], tourettome_workspace, tourettome_freesurfer, tourettome_derivatives )