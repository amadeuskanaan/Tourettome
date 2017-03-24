import os
import sys
from utilities.utils import mkdir_path
from variables.subject_list import *


# Registration based cortical thickness measurement.
# Das et al., Neuroimage. 2009 Apr 15;45(3):867-79. doi: 10.1016/j.neuroimage.2008.12.016. Epub 2008 Dec 25.


def make_cortical_thickness(population, workspace):

    for subject in population:
        print '========================================================================================'
        print 'Runing Kelly Kapowski diffeomorphic registration based cortical thickness %s' % (subject)

        subdir   = os.path.join(workspace, subject)
        kellydir = mkdir_path(os.path.join(subdir, 'THICKNESS'))
        os.chdir(kellydir)

        # combine gm and wm with correect labels for DIRECT
        os.system('fslmaths %s -mul 2 gm' % (os.path.join(subdir, 'ANATOMICAL/seg_spm/c1ANATOMICAL')))
        os.system('fslmaths %s -mul 3 wm' % (os.path.join(subdir, 'ANATOMICAL/seg_spm/c2ANATOMICAL')))
        os.system('fslmaths gm -add wm segmentation0.nii.gz')

        # Run ANTS-DIRECT
        os.system('KellyKapowski '
                  '--image-dimensionality 3 '
                  '--segmentation-image "[segmentation0.nii.gz,2,3]" '
                  '--convergence "[45,0.0,10]" '
                  '--output "[segmentation0_cortical_thickness.nii.gz, segmentation0_warped_white_matter.nii.gz]" '
                  '--gradient-step 0.025000 '
                  '--number-of-integration-points 10 '
                  '--smoothing-variance 1.000000 '
                  '--smoothing-velocity-field-parameter 1.500000 '
                  '--thickness-prior-estimate 10.000000')


make_cortical_thickness(['HA020'], tourettome_workspace)