__author__ = 'kanaan 01.01.2018'

import os
import shutil
import subprocess
from algorithms.fast_ecm import fastECM
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



def make_group_masks(population, workspace_dir, derivatives_dir):

    print '##############################'
    print 'Creating Group GM Mask '
    derivatives_dir = mkdir_path(os.path.join(derivatives_dir, 'MASKS'))
    gm_group_mask = os.path.join(derivatives_dir, 'GROUP_GM_FUNC_3mm.nii')

    if not os.path.isfile(gm_group_mask):
        gm_masks_list = ' '.join(['%s -add' %(os.path.join(workspace_dir, subject, 'REGISTRATION/REST_GM_MNI3mm.nii.gz'))
                        for subject in population])[:-4]

        os.system('fslmaths %s -thrp 55 -bin %s' %(gm_masks_list, gm_group_mask))
        os.system('gunzip %s'%gm_group_mask)

make_group_masks(tourettome_subjects, tourettome_workspace, tourettome_derivatives)



    #return gm_group_mask


def make_functional_derivatives(population, workspace_dir, freesurfer_dir, derivatives_dir):

    print '========================================================================================'
    print ''
    print '                Tourettome - 008. CREATING FUNCTIONAL FEATURES                          '
    print ''
    print '========================================================================================'

    ecm_dir       = mkdir_path(os.path.join(derivatives_dir, 'FUNC_CENTRALITY'))
    #sca_dir      = mkdir_path(os.path.join(derivatives_dir, 'FUNC_SEED_CORRELATION'))
    #alff_dir     = mkdir_path(os.path.join(derivatives_dir, 'FUNC_ALFF'))
    gm_group_mask = os.path.join(derivatives_dir, 'MASKS/GROUP_GM_FUNC_3mm.nii')


    count = 0
    for subject in population:
        count +=1

        print 'Extracting structural features for subject %s' %subject

        #I/0
        subject_dir     = os.path.join(workspace_dir, subject)
        func_denoised   = os.path.join(subject_dir, 'DENOISE/residuals_compcor/residual_bp_z_fwhm6.nii.gz')


        print '##################################################################'
        print '1. Calculating Centrality Measures'

        subject_dir_ecm = mkdir_path(os.path.join(ecm_dir, subject))
        os.chdir(subject_dir_ecm)

        # gunzip for matlab
        if not os.path.isfile('%s/residual.nii'%subject_dir_ecm):
            shutil.copy(func_denoised, './residual.nii.gz')
            os.system('gunzip residual.nii.gz')
            os.system('rm -rf residual.nii.gz')


        if not os.path.isfile('residual_fastECM.nii'):
            # Run Fast ECM
            matlab_cmd = ['matlab', '-nodesktop', '-nosplash', '-nojvm',
                          '-r "fastECM(\'%s\', \'1\', \'1\', \'1\', \'20\', \'%s\') ; quit;"'
                          % (os.path.join(subject_dir_ecm, 'residual.nii'), gm_group_mask)]
            subprocess.call(matlab_cmd)

        if not os.path.isfile(os.path.join(subject_dir_ecm, 'residual_fastECM_rh.mgh')):
            print '...... project to surface'  #### take non-smoothed data and smooth on surface
            for hemi in ['lh', 'rh']:
                os.system('mri_vol2surf '
                          '--mov residual_fastECM.nii '
                          '--reg %s '
                          '--trgsubject fsaverage5 '
                          '--projfrac-avg 0.2 0.8 0.1 '
                          '--hemi %s '
                          '--interp nearest '
                          '--cortex '
                          '--o residual_fastECM_%s.mgh'
                          % (fs_mni_reg, hemi, hemi))

        # z-score
        def z_score_centrality(image, outname):
            print '...... z-scoring %s' % outname
            std  = commands.getoutput('fslstats %s -k %s -s | awk \'{print $1}\'' % (image, group_gm_mask))
            mean = commands.getoutput('fslstats %s -k %s -m | awk \'{print $1}\'' % (image, group_gm_mask))
            os.system('fslmaths %s -sub %s -div %s -mas %s %s' % (image, mean, std, group_gm_mask, outname))

        z_score_centrality('residual_fastECM.nii', 'zscore_fastECM')
        z_score_centrality('residual_degCM.nii', 'zscore_degCM')
        z_score_centrality('residual_normECM.nii', 'zscore_normECM')
        z_score_centrality('residual_rankECM.nii', 'zscore_rankECM')


make_functional_derivatives(['PA060'], tourettome_workspace, tourettome_freesurfer, tourettome_derivatives)



# print '#######################'
    # print '2. Calculating Seed Correlation Measures'
    #
    # seeds = ['STR', 'STR3_MOTOR', 'STR3_LIMBIC', 'STR3_EXECUTIVE',
    #          'INSULA', 'ACC', 'M1', '']
    #
    # print '#######################'
    # print '3. Calculating fractional Amplitude of low frequency fluctuations'


# def run_sca(pproc, mask, mask_name, string):
#     sca_dir        = os.path.join(subject_dir, 'SCA/%s'%mask_name)
#     mkdir_path(sca_dir)
#     os.chdir(sca_dir)
#
#     print string
#     if not os.path.isfile('SCA_Z_%s.nii.gz'%string):
#
#         ##'1. Extract Timeseries'
#         os.system('3dROIstats -quiet -mask_f2short -mask %s %s > rest_native.1d'%(mask, pproc))
#
#         ##'2. Compute voxel-wise correlation with Seed Timeseries'
#         os.system('3dfim+ -input %s -ideal_file rest_native.1d -out Correlation -bucket corr.nii.gz'%pproc)
#
#         ##'3. Z-transform correlation'
#         eq = ['log((a+1)/(a-1))/2']
#         os.system('3dcalc -a corr.nii.gz -expr %s -prefix SCA_Z_%s.nii.gz'%(eq,string))
#         os.system('rm -rf rest_native.1d corr.nii.gz')





