import os
import sys
from utilities.utils import mkdir_path
from variables.subject_list import *


# Registration based cortical thickness measurement.
# Das et al., Neuroimage. 2009 Apr 15;45(3):867-79. doi: 10.1016/j.neuroimage.2008.12.016. Epub 2008 Dec 25.

#assert len(sys.argv)== 2
#subject_index=int(sys.argv[1])

def make_cortical_thickness(population, workspace, freesurfer_dir, num_threads = 1):

    for subject in population:
        #subject = population[subject_index]
        print '========================================================================================'
        print 'Runing Cortical thickness estimation for %s' % (subject)

        subdir  = os.path.join(workspace, subject)
        ctdir   = mkdir_path(os.path.join(subdir, 'THICKNESS'))
        os.chdir(ctdir  )

        prob_gm = os.path.join(subdir, 'ANATOMICAL/seg_spm/c1ANATOMICAL.nii')
        prob_wm = os.path.join(subdir, 'ANATOMICAL/seg_spm/c2ANATOMICAL.nii')
        first   = os.path.join(subdir, 'ANATOMICAL/seg_first/FIRST.nii.gz')
        T1mgz   = os.path.join(freesurfer_dir, subject, 'mri/T1.mgz')

        if not os.path.isfile(os.path.join(ctdir, 'cortical_thickness_kellykapowski.nii.gz')):

            print '..... Running KellyKapowski DiReCT algorithm %s'%subject

            # Set number of cores
            os.system('export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=%s' %num_threads)

            # Combine gm and wm with correect labels for DIRECT
            os.system('fslmaths %s -thr 0.5 -bin -sub %s -bin -mul 2 gm' %(prob_gm, first))
            os.system('fslmaths %s -thr 0.5 -bin -add %s -bin -mul 3 wm' %(prob_wm, first))
            os.system('fslmaths gm -add wm segmentation0.nii.gz')

            ### Run
            os.system('KellyKapowski '
                     '--image-dimensionality 3 '
                     '--segmentation-image "[segmentation0.nii.gz,2,3]" '
                     '--gray-matter-probability-image %s'
                     '--white-matter-probability-image %s'
                     '--convergence "[45,0.0,10]" '
                     '--output "[cortical_thickness_kellykapowski.nii.gz, segmentation0_warped_white_matter.nii.gz]" '
                     '--gradient-step 0.025000 '
                     '--number-of-integration-points 10 '
                     '--smoothing-variance 1.000000 '
                     '--smoothing-velocity-field-parameter 1.500000 '
                     '--thickness-prior-estimate 10.000000'
                      %(prob_gm, prob_wm))

            # Transform to Freesurfer space
            os.system('mri_vol2vol '
                      '--mov cortical_thickness_kellykapowski.nii.gz '
                      '--targ %s '
                      '--o cortical_thickness_kellykapowski.mgz '
                      '--regheader' %(T1mgz))


        #Laplacian cortical thickness
        if not os.path.isfile(os.path.join(ctdir, 'cortical_thickness_laplacian.nii.gz')):

            print '..... Running LaplacianThickness algorithm'

            # Set number of cores
            os.system('export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=%s' %num_threads)

            # Run
            os.system('LaplacianThickness wm.nii.gz gm.nii.gz cortical_thickness_laplacian.nii.gz')

            # Transform to Freesurfer space
            os.system('mri_vol2vol '
                      '--mov cortical_thickness_laplacian.nii.gz '
                      '--targ %s '
                      '--o cortical_thickness_laplacian.mgz '
                      '--regheader' %(T1mgz))


make_cortical_thickness(population=['HA022'], workspace=tourettome_workspace, freesurfer_dir=tourettome_freesurfer, num_threads=100)

#make_cortical_thickness(population=paris1, workspace=tourettome_workspace)
#make_cortical_thickness(population=paris2, workspace=tourettome_workspace)
#make_cortical_thickness(population=leipzig1, workspace=tourettome_workspace)
#make_cortical_thickness(population=leipzig2, workspace=tourettome_workspace)
#make_cortical_thickness(population=hannover_a1, workspace=tourettome_workspace)
#make_cortical_thickness(population=hannover_a2, workspace=tourettome_workspace)
#make_cortical_thickness(population=hannover_b, workspace=tourettome_workspace)
