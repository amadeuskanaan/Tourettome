__author__ = 'kanaan 03.12.2015'

import os
import sys
import nibabel as nb
import nipype.interfaces.ants as ants
from utilities.utils import *
from variables.subject_list import *


assert len(sys.argv)== 2
subject_index=int(sys.argv[1])

def register(population, workspace_dir):

    #for subject in population:
        subject = population[subject_index]
        print '========================================================================================'
        print 'Preprocessing functional data for %s' % (subject)

        anat_dir     = os.path.join(workspace_dir, subject, 'ANATOMICAL')
        func_dir     = os.path.join(workspace_dir, subject, 'FUNCTIONAL')
        matsdir      = os.path.join(workspace_dir, subject, 'FUNCTIONAL/moco/REST_EDIT_moco2.mat')
        regdir       = mkdir_path(os.path.join(workspace_dir, subject, 'REGISTRATION'))
        regdir_anat  = mkdir_path(os.path.join(regdir, 'reg_anat'))
        regdir_mni   = mkdir_path(os.path.join(regdir, 'reg_mni'))

        anat       = os.path.join(anat_dir, 'ANATOMICAL_BRAIN.nii.gz')
        anat_gm    = os.path.join(anat_dir, 'seg_spm/c1ANATOMICAL.nii')
        anat_wm    = os.path.join(anat_dir, 'seg_spm/c2ANATOMICAL.nii')
        anat_csf   = os.path.join(anat_dir, 'seg_spm/c3ANATOMICAL.nii')
        anat_first = os.path.join(anat_dir, 'seg_first/FIRST.nii.gz')
        func3d     = os.path.join(func_dir, 'REST_EDIT_MOCO_BRAIN_MEAN.nii.gz')
        func4d     = os.path.join(func_dir, 'REST_EDIT_BRAIN.nii.gz')

        ################################################################################################################
        # ##### Non-linear ANATOMICAL to MNI

        if not os.path.isfile(os.path.join(regdir, 'ANATOMICAL_BRAIN_MNI1mm.nii.gz')):
            print 'Non-linear ANTS - anat2mni non-linear '
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
            #anat2mni.inputs.num_threads = 26
            anat2mni.inputs.interpolation='Linear'
            anat2mni.inputs.winsorize_lower_quantile=0.005
            anat2mni.inputs.winsorize_upper_quantile=0.995
            anat2mni.inputs.collapse_output_transforms=True
            anat2mni.inputs.output_inverse_warped_image=True
            anat2mni.inputs.output_warped_image=True
            anat2mni.inputs.use_histogram_matching=True
            #anat2mni.cmdline
            anat2mni.run()
            os.system('cp transform_Warped.nii.gz ../ANATOMICAL_BRAIN_MNI1mm.nii.gz')

            # Warp anatomical tissue classess to MNI space

            for tissue_name, tissue_path in {'GM': anat_gm , 'WM': anat_wm,  'CSF': anat_csf}.iteritems():

                print '........ Warping tissue masks to MNI'

                # Subtract FSl-FIRST subcortical segmentation from WM/CSF
                if tissue_name == 'GM':
                    os.system('fslmaths %s -add %s anat_%s' %(tissue_path, anat_first, tissue_name))
                else:
                    os.system('fslmaths %s -sub %s anat_%s' %(tissue_path, anat_first, tissue_name))

                os.system('WarpImageMultiTransform 3 anat_%s anat_%s_MNI1mm.nii.gz -R %s transform1Warp.nii.gz transform0GenericAffine.mat'
                          %(tissue_name, tissue_name, mni_brain_1mm))
                os.system('fslmaths anat_%s_MNI1mm.nii.gz -thr 0.5 -bin ../ANATOMICAL_%s_MNI1mm.nii.gz' %(tissue_name, tissue_name))

                #Resample to 2mm
                os.system('flirt -in anat_%s_MNI1mm -ref %s -applyisoxfm 2 -out anat_%s_MNI2mm'
                          %(tissue_name,mni_brain_2mm, tissue_name))
                os.system('fslmaths anat_%s_MNI2mm -thr 0.5 -bin ../ANATOMICAL_%s_MNI2mm' %(tissue_name, tissue_name))


        ################################################################################################################
        ##### Linear FUNCTIONAL to ANATOMICAL

        print 'Two-step linear registration - func2anat'

        if not os.path.isfile(os.path.join(regdir, 'REST_EDIT_MOCO_BRAIN_MEAN_BBR_ANAT1mm.nii.gz')):

            os.chdir(regdir_anat)

            print '......flirt mutualinfo'

            #linear step 1  mutualinfo
            os.system('flirt -in %s -ref %s -cost mutualinfo -dof 6 -omat rest2anat_1.mat -out rest2anat_1.nii.gz ' %(func3d,anat))

            print '......flirt bbr'

            # linear step 2 - bbr
            os.system('fslmaths %s -thr 0.5 -bin anat_wm' %anat_wm)
            os.system('flirt -in %s -ref %s -dof 6 -cost bbr -wmseg anat_wm -schedule %s -init rest2anat_1.mat -omat rest2anat_2.mat -out rest2anat_2.nii.gz'
                      % (func3d, anat, bbr_schedule))
            os.system('cp rest2anat_2.nii.gz ../REST_EDIT_MOCO_BRAIN_MEAN_BBR_ANAT1mm.nii.gz')

        ################################################################################################################
        ##### Resample FUNCTIONAL to MNI linear

        if not os.path.isfile(os.path.join(regdir, 'REST_EDIT_BRAIN_UNIMOCO_MNI2mm.nii.gz')):

            print '..... Transforming func2mni in one step.....'
            print '...........concatenating moco-affine/func2anat-affine/anat2mni-affine/anat2mni-warp'

            concat_dir = mkdir_path(os.path.join(regdir_mni, 'concat'))
            os.chdir(concat_dir)

            # Split volumes of func_edit
            os.system('fslsplit %s -t' %func4d)

            # Convert BBR affine to ants-itk format
            os.system('c3d_affine_tool -ref %s -src %s %s/rest2anat_2.mat -fsl2ras -oitk rest2anat_2.tfm'%(anat, func3d, regdir_anat))

            # Concat
            frames = [0,nb.load(func4d).get_data().shape[3]]
            print 'N-frames', frames

            for i in xrange(frames[0], frames[1]):
                frame = '{0:0>4}'.format(i)

                # Concatenate motion-correction-affines and fun2anat-affine
                os.system('convert_xfm -omat MAT_UNI_%s.mat -concat %s/rest2anat_2.mat %s/MAT_%s' %(frame, regdir_anat,  matsdir, frame))

                # Convert unified mat to ants-itk format
                os.system('c3d_affine_tool -ref %s -src vol%s.nii.gz MAT_UNI_%s.mat -fsl2ras -oitk  MAT_UNI_%s.tfm'
                          %(anat, frame, frame, frame))

                # Apply all xfms
                os.system('antsApplyTransforms '
                          '-d 3 '
                          '-i vol%s.nii.gz '
                          '-o warped%s.nii.gz '
                          '-r %s '
                          '-n Linear '
                          '-t ../transform1Warp.nii.gz ../transform0GenericAffine.mat MAT_UNI_%s.tfm'
                          %(frame, frame, mni_brain_2mm,  frame))

            os.system('fslmerge -t %s/REST_EDIT_UNI_BRAIN_MNI2mm.nii.gz %s/warped*' %(regdir, concat_dir))
            os.system('rm -rf %s' %concat_dir)


register(tourettome_subjects, tourettome_workspace)
