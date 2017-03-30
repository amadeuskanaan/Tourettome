import os

from utilities.utils import mkdir_path
from variables.subject_list import *
from nipype.interfaces.ants.segmentation import KellyKapowski


# Registration based cortical thickness measurement.
# Das et al., Neuroimage. 2009 Apr 15;45(3):867-79. doi: 10.1016/j.neuroimage.2008.12.016. Epub 2008 Dec 25.

# assert len(sys.argv)== 2
# subject_index=int(sys.argv[1])

def make_cortical_thickness(population, workspace):

    for subject in population:
        # subject = population[subject_index]
        print '========================================================================================'
        print 'Runing Kelly Kapowski diffeomorphic registration based cortical thickness %s' % (subject)

        subdir   = os.path.join(workspace, subject)
        kellydir = mkdir_path(os.path.join(subdir, 'THICKNESS'))
        os.chdir(kellydir)

        prob_gm = os.path.join(subdir, 'ANATOMICAL/seg_spm/c1ANATOMICAL.nii')
        prob_wm = os.path.join(subdir, 'ANATOMICAL/seg_spm/c2ANATOMICAL.nii')
        first   = os.path.join(subdir, 'ANATOMICAL/seg_first/FIRST.nii.gz')


        if not os.path.isfile(os.path.join(kellydir, 'segmentation0_cortical_thickness.nii.gz')):

            # combine gm and wm with correect labels for DIRECT

            os.system('fslmaths %s -thr 0.5 -bin -sub %s -bin -mul 2 gm' %(prob_gm, first))
            os.system('fslmaths %s -thr 0.5 -bin -add %s -bin -mul 3 wm' %(prob_wm, first))
            os.system('fslmaths gm -add wm segmentation0.nii.gz')

            # Run ANTS-DIRECT
            # os.system('KellyKapowski '
            #          '--image-dimensionality 3 '
            #          '--segmentation-image "[segmentation0.nii.gz,2,3]" '
            #          '--convergence "[45,0.0,10]" '
            #          '--output "[segmentation0_cortical_thickness.nii.gz, segmentation0_warped_white_matter.nii.gz]" '
            #          '--gradient-step 0.025000 '
            #          '--number-of-integration-points 10 '
            #          '--smoothing-variance 1.000000 '
            #          '--smoothing-velocity-field-parameter 1.500000 '
            #          '--thickness-prior-estimate 10.000000')

            kk = KellyKapowski()
            kk.inputs.dimension = 3
            kk.inputs.segmentation_image = "[segmentation0.nii.gz,2,3]"
            kk.inputs.convergence = "[45,0.0,10]"
            kk.inputs.gradient_step = 0.025
            kk.inputs.smoothing_variance = 1.0
            kk.inputs.smoothing_velocity_field = 1.5
            #kk.inputs.use_bspline_smoothing = False
            kk.inputs.number_integration_points = 10
            kk.inputs.thickness_prior_estimate = 10
            kk.inputs.num_threads = 26
            kk.run()


make_cortical_thickness(['PA072'], tourettome_workspace)
