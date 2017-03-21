__author__ = 'kanaan 03.12.2015'

import os
from variables.subject_list import *
from utilities.utils import *
import nibabel as nb
import shutil
import nipype.interfaces.ants as ants


def register(population, workspace_dir):

    for subject in population:
        print '========================================================================================'
        print 'Preprocessing functional data for %s' % (subject)

        #input
        subdir   = os.path.join(workspace_dir, subject)
        anat     = os.path.join(subdir, 'ANATOMICAL/ANATOMICAL_BRAIN.nii.gz')
        anat_wm  = os.path.join(subdir, 'ANATOMICAL/ANATOMICAL_WM.nii.gz')
        func     = os.path.join(subdir, 'FUNCTIONAL/REST_EDIT_MOCO_BRAIN_MEAN.nii.gz')

        #output
        regdir          = mkdir_path(os.path.join(subdir, 'REGISTRATION'))
        regdir_anat = mkdir_path(os.path.join(regdir, 'reg_anat'))
        regdir_mni  = mkdir_path(os.path.join(regdir, 'reg_mni'))


        # Functional to anatomical registration
        print '-Linear transformation: functional to anatomical space'

        # reample anat to 2mm
        # os.chdir(regdir_anat)
        # os.system('flirt -in %s -ref %s -out ANAT_2mm -applyisoxfm 2.0 -datatype float' % (anat, anat))
        #
        # # run corratio linear xfm
        # os.system('flirt -in        %s '
        #                 '-ref       ANAT_2mm '
        #                 '-cost      corratio '
        #                 '-dof       6  '
        #                 '-noresample    '
        #                 '-interp    spline '
        #                 '-omat      rest2anat_1.mat '
        #                 '-out       rest2anat_1.nii.gz '
        #           %(func,))
        #
        # # run bbr linear xfm
        # os.system('flirt -in  %s '
        #           '-ref       ANAT_2mm '
        #           '-cost      bbr '
        #           '-wmseg     %s '
        #           '-dof       6 '
        #           '-init      rest2anat_1.mat '
        #           '-schedule  /usr/share/fsl/5.0/etc/flirtsch/bbr.sch '
        #           '-noresample    '
        #           '-interp    spline '
        #           '-omat      rest2anat_2.mat '
        #           '-out       rest2anat_2.nii.gz '
        #           % (func, anat_wm))


        # if not os.path.isfile('./rest2anat_step_1_corratio.mat'):
        #     os.system('flirt -in %s -ref %s -cost corratio -dof 6 -noresample -out rest2anat_step_1_corratio -omat rest2anat_step_1_corratio.mat'
        #               %(func_native, anat_native))
        #
        # print '..... linear xfm step 2: bbr'
        # if not os.path.isfile('./rest2anat_step_2_bbr.mat'):
        #     os.system('flirt -in %s -ref %s -noresample -cost bbr -wmseg %s -dof 6 -init rest2anat_step_1_corratio.mat -schedule /usr/share/fsl/5.0/etc/flirtsch/bbr.sch '
        #               '-out rest2anat_step_2_bbr -omat rest2anat_step_2_bbr.mat' %(func_native, anat_native, anat_wm))
        #
        #     # resample anat image to func resolution... use this as a reference, so that we dont resample the func and view the reg quality easily.
        #     anat_native_resample = resample_to_img(anat_native, os.path.join(regdir_funcanat, 'rest2anat_step_1_corratio.nii.gz'))
        #     nb.save(anat_native_resample, '%s/anat_resample.nii.gz' % regdir_funcanat)
        #
        # print '..... unifying moco and linear xfm affines and applying on each 4D frame'
        #
        # if not os.path.isfile(os.path.join(regdir, 'REST2ANAT.nii.gz')):
        #     # split volumes of func data (with 5 dropped TRs and RPI orientation )
        #     mats_dir = mkdir_path(os.path.join(regdir_funcanat, 'mats_unified'))
        #     os.chdir(mats_dir)
        #     os.system('fslsplit %s/REST.nii.gz -t' % os.path.join(subdir, 'FUNCTIONAL'))
        #
        #     # combine affines
        #     frames = [0, nb.load(os.path.join(subdir, 'FUNCTIONAL/REST.nii.gz')).get_data().shape[3]-1]
        #     for i in xrange(frames[0], frames[1]):
        #         frame = '{0:0>4}'.format(i)
        #         print frame,
        #         os.system('convert_xfm -omat UNIMAT_%s.mat -concat ../rest2anat_step_2_bbr.mat %s/moco/MATS/MAT_%s' % (frame, os.path.join(subdir,'FUNCTIONAL'), frame))
        #         os.system('flirt -in vol%s.nii.gz -ref %s -applyxfm -init UNIMAT_%s.mat -out flirt_uni_%s.nii.gz' % (frame, anat_native, frame, frame))
        #
        #     os.system('fslmerge -t ../REST2ANAT.nii.gz flirt_uni_*')
        #     os.system('rm -rf vol* flirt_uni_*')
        #



        ##############################################
        # MNI registration
        print '- Non-Linear transformation: functional to MNI'

    
	import os.path as op
	from nipype.interfaces.ants import Registration
	reg = Registration()
	reg.inputs.dimension = 3
	reg.inputs.fixed_image = mni_brain_1mm
	reg.inputs.moving_image =  anat
	reg.inputs.interpolation = 'Linear'
	reg.inputs.output_transform_prefix = "transform"
	reg.inputs.output_warped_image = 'transform_Warped.nii.gz'
	reg.inputs.initial_moving_transform_com = False
	reg.inputs.collapse_output_transforms = False
	reg.inputs.num_threads= 16
	reg.inputs.transforms = ['Rigid', 'Affine']
	reg.inputs.transform_parameters = [(0.1,), (0.1,)]
	reg.inputs.number_of_iterations = [[15, 10, 5], [15, 10, 5]]
	reg.inputs.smoothing_sigmas = [[4,2,0], [2,1,0]]
	reg.inputs.metric = ['Mattes', 'Mattes']
	reg.inputs.radius_or_number_of_bins = [32, 32]
	reg.inputs.shrink_factors = [[8,4,2], [3,2,1]]
	reg.inputs.use_histogram_matching = [True] * 2
	reg.inputs.metric_weight = [1] * 2
	reg.inputs.sampling_strategy = ['Regular', 'Regular']
	reg.inputs.convergence_threshold = [1.e-8, 1.e-8]
	reg.inputs.convergence_window_size = [10, 10]
	reg.inputs.sampling_percentage = [0.25, 0.25]
	reg.inputs.collapse_output_transforms = True
	reg.inputs.write_composite_transform = True
	res = reg.run()
	print reg.cmdline	


        #os.system('WarpImageMultiTransform 3 %s %s -i transform0Affine.mat transform1InverseWarp.nii.gz'% (anat, mni_brain_1mm))


register(['HB012'], tourettome_workspace)


