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
        subdir     = os.path.join(workspace_dir, subject)
        anat       = os.path.join(subdir, 'ANATOMICAL/ANATOMICAL_BRAIN.nii.gz')
        anat_skull = os.path.join(subdir, 'ANATOMICAL/ANATOMICAL_BRAIN.nii.gz')
        anat_wm    = os.path.join(subdir, 'ANATOMICAL/seg_spm/c2ANATOMICAL.nii')
        func       = os.path.join(subdir, 'FUNCTIONAL/REST_EDIT_MOCO_BRAIN_MEAN.nii.gz')
        func_vols  = os.path.join(subdir, 'FUNCTIONAL/REST_EDIT_MOCO_BRAIN_MEAN.nii.gz')

        #output
        regdir          = mkdir_path(os.path.join(subdir, 'REGISTRATION'))
        regdir_anat = mkdir_path(os.path.join(regdir, 'reg_anat'))
        regdir_mni  = mkdir_path(os.path.join(regdir, 'reg_mni'))


        # Functional to anatomical registration
        print '--Linear transformation: functional to anatomical space'

        if not os.path.isfile(os.path.join(regdir, 'REST_EDIT_MOCO_BRAIN_MEAN_ANAT1mm.nii.gz')):

            # threshold wmseg
            os.chdir(regdir_anat)
            os.system('fslmaths %s -thr 0.5 -bin anat_wm' %anat_wm)

            # run corratio linear xfm
            print '......flirt corratio'
            os.system('flirt -in %s -ref %s -cost mutualinfo -dof 6 -omat rest2anat_1.mat -out rest2anat_1.nii.gz ' %(func,anat))

            # run bbr linear xfm
            print '......flirt bbr'
            os.system('flirt '
                      '-in        %s '
                      '-ref       %s '
                      '-dof       6 '
                      '-cost      bbr '
                      '-wmseg     anat_wm '
                      '-init      rest2anat_1.mat '
                      '-schedule  /usr/share/fsl/5.0/etc/flirtsch/bbr.sch '
                      '-omat      rest2anat_2.mat '
                      '-out       rest2anat_2.nii.gz '
                      % (func, anat))
            os.system('cp rest2anat_2.nii.gz ../REST_EDIT_MOCO_BRAIN_MEAN_ANAT1mm.nii.gz')

        print '..... unifying moco and linear affines'

        if not os.path.isfile(os.path.join(regdir, 'REST2ANAT.nii.gz')):
            # split volumes of func data (with 5 dropped TRs and RPI orientation )
            mats_dir = mkdir_path(os.path.join(regdir_anat, 'mats_unified'))
            os.chdir(mats_dir)
            os.system('fslsplit %s/REST.nii.gz -t' % os.path.join(subdir, 'FUNCTIONAL'))

            # combine affines
            frames = [0, nb.load(os.path.join(subdir, 'FUNCTIONAL/REST.nii.gz')).get_data().shape[3]-1]
            for i in xrange(frames[0], frames[1]):
                frame = '{0:0>4}'.format(i)
                print frame,
                os.system('convert_xfm -omat UNIMAT_%s.mat -concat ../rest2anat_step_2_bbr.mat %s/moco/MATS/MAT_%s' % (frame, os.path.join(subdir,'FUNCTIONAL'), frame))
                os.system('flirt -in vol%s.nii.gz -ref %s -applyxfm -init UNIMAT_%s.mat -out flirt_uni_%s.nii.gz' % (frame, anat_native, frame, frame))

            os.system('fslmerge -t ../REST2ANAT.nii.gz flirt_uni_*')
            os.system('rm -rf vol* flirt_uni_*')


        ##############################################
        # MNI registration
        print '--Non-Linear transformation: functional to MNI'

        if not os.path.isfile(os.path.join(regdir, 'ANATOMICAL_BRAIN_MNI1mm.nii.gz')):
            os.chdir(regdir_mni)
            anat2mni = ants.Registration()
            anat2mni.inputs.moving_image= anat
            anat2mni.inputs.fixed_image= mni_brain_1mm
            anat2mni.inputs.dimension=3
            anat2mni.inputs.transforms=['Rigid','Affine','SyN']
            anat2mni.inputs.metric=['MI','MI','CC']
            anat2mni.inputs.metric_weight=[1,1,1]
            anat2mni.inputs.number_of_iterations=[[1000,500,250,100],[1000,500,250,100],[100,70,50,20]]
            anat2mni.inputs.convergence_threshold=[1e-6,1e-6,1e-6]
            anat2mni.inputs.convergence_window_size=[10,10,10]
            anat2mni.inputs.shrink_factors=[[8,4,2,1],[8,4,2,1],[8,4,2,1]]
            anat2mni.inputs.smoothing_sigmas=[[3,2,1,0],[3,2,1,0],[3,2,1,0]]
            anat2mni.inputs.sigma_units=['vox','vox','vox']
            anat2mni.inputs.initial_moving_transform_com=1
            anat2mni.inputs.transform_parameters=[(0.1,),(0.1,),(0.1,3.0,0.0)]
            anat2mni.inputs.sampling_strategy=['Regular', 'Regular', 'None']
            anat2mni.inputs.sampling_percentage=[0.25,0.25,1]
            anat2mni.inputs.radius_or_number_of_bins=[32,32,4]
            anat2mni.inputs.num_threads = 30
            anat2mni.inputs.interpolation='Linear'
            anat2mni.inputs.winsorize_lower_quantile=0.005
            anat2mni.inputs.winsorize_upper_quantile=0.995
            anat2mni.inputs.collapse_output_transforms=True
            anat2mni.inputs.output_inverse_warped_image=True
            anat2mni.inputs.output_warped_image=True
            anat2mni.inputs.use_histogram_matching=True
            anat2mni.run()
            os.system('cp transform_Warped.nii.gz ../ANATOMICAL_BRAIN_MNI1mm.nii.gz')

            os.chdir(regdir_anat)
            os.system('/scr/sambesi1/Software/C3D/bin/c3d_affine_tool -ref %s -src %s rest2anat_2.mat -fsl2ras -oitk rest2anat_bbr.tfm' % (anat, func))

        os.chdir(regdir_mni)
        # os.system('WarpImageMultiTransform 3 %s func2mni.nii.gz -r %s transform1Warp.nii.gz transform0GenericAffine.mat ../reg_anat/rest2anat_bbr.tfm' %(func, mni_brain_2mm ) )
        os.system('antsApplyTransforms '
                  '-d 3 '
                  '-i %s '
                  '-o func2mni.nii.gz '
                  '-r %s '
                  '-n Bspline '
                  '-t transform1Warp.nii.gz transform0GenericAffine.mat ../reg_anat/rest2anat_bbr.tfm'
                  %(func, mni_brain_1mm ) )


#$   -i T_template0.nii -o test.nii.gz -r T_template0.nii -n Linear -t ~/Desktop/testTransform.tfm -v 1


register(['HB012'], tourettome_workspace)
# register(['PA001'], tourettome_workspace)


