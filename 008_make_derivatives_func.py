__author__ = 'kanaan 01.01.2018'

import os
import shutil
import subprocess
import commands
import numpy as np
import nibabel as nb
from nilearn.input_data import NiftiLabelsMasker
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

        os.system('fslmaths %s -thrp 25 -bin %s' %(gm_masks_list, gm_group_mask))
        os.system('gunzip %s'%gm_group_mask)

make_group_masks(tourettome_subjects, tourettome_workspace, tourettome_derivatives)

def make_functional_derivatives(population, workspace_dir, freesurfer_dir, derivatives_dir):

    print '========================================================================================'
    print ''
    print '                Tourettome - 008. CREATING FUNCTIONAL FEATURES                          '
    print ''
    print '========================================================================================'

    # global IO
    ecm_dir       = mkdir_path(os.path.join(derivatives_dir, 'func_centrality'))
    sca_dir       = mkdir_path(os.path.join(derivatives_dir, 'func_sca'))
    gm_group_mask = os.path.join(derivatives_dir, 'MASKS/GROUP_GM_FUNC_3mm.nii')

    count = 0
    for subject in population:
        count +=1
        print '###################################################################'
        print 'Extracting structural features for subject %s' % subject

        # subject I/0
        subject_dir = os.path.join(workspace_dir, subject)
        func_denoised = os.path.join(subject_dir, 'DENOISE/residuals_compcor/residual_bp.nii.gz')
        func_denoised_lh = os.path.join(subject_dir, 'DENOISE/residuals_compcor/residual_bp_z_lh.mgh')
        func_denoised_rh = os.path.join(subject_dir, 'DENOISE/residuals_compcor/residual_bp_z_rh.mgh')

        ################################################################################################################
        ### 1- Seed-Based Correlation
        ################################################################################################################

        seeds = {'STR'         : mask_str,
                 # 'STR3_MOTOR'  : mask_str_motor,
                 # 'STR3_LIMBIC' : mask_str_limbic,
                 # 'STR3_EXEC'   : mask_str_exec,
                 # 'CAUD'        : mask_caud,
                 # 'PUTA'        : mask_puta,
                 # 'ACCU'        : mask_accu,
                 # 'PALL'        : mask_pall,
                 # 'THAL'        : mask_thal,
                 # 'HIPP'        : mask_hipp,
                 # 'AMYG'        : mask_amyg,
                 }

        for seed in seeds:

            # Extract seed timeseries
            seed            = seeds[seed_name]
            masker_seed     = NiftiLabelsMasker(labels_img=seed, standardize=True, memory='nilearn_cache', verbose=1)
            timeseries_seed = masker_seed.fit_transform(func_denoised)

            # Extract surface timeseries
            masker_cortex =   NiftiLabelsMasker(labels_img=seed, standardize=True, memory='nilearn_cache', verbose=1)








        print '2. Calculating Seed-Based Correlation'
        if not os.path.isfile(os.path.join(sca_dir,'%s_STR3_MOTOR_sca_z.nii.gz'%subject)):

            seeds = {'STR3_MOTOR':   str3_motor,
                     'STR3_LIMBIC':  str3_limbic,
                     'STR3_EXEC':    str3_exec}

            for seed_name in seeds:
                seed = seeds[seed_name]

                seed_masker = NiftiLabelsMasker(labels_img=seed, standardize=True, memory='nilearn_cache', verbose=1)
                seed_time_series = seed_masker.fit_transform(func_denoised)

                brain_masker = input_data.NiftiMasker(smoothing_fwhm=6, detrend=None, standardize=True,
                                                      low_pass=None, high_pass=None, t_r=2., memory='nilearn_cache',
                                                      memory_level=1, verbose=0)
                brain_time_series = brain_masker.fit_transform(func_denoised)

                #  correlate the seed signal with the signal of each voxel.
                # see http://nilearn.github.io/auto_examples/03_connectivity/plot_seed_to_voxel_correlation.html#sphx-glr-auto-examples-03-connectivity-plot-seed-to-voxel-correlation-py
                seed_based_correlations = np.dot(brain_time_series.T, seed_time_series) / seed_time_series.shape[0]

                seed_based_correlations_fisher_z = np.arctanh(seed_based_correlations)
                print("seed-based correlation Fisher-z transformed: min = %.3f; max = %.3f" % (
                    seed_based_correlations_fisher_z.min(),seed_based_correlations_fisher_z.max()))

                seed_based_correlation_img = brain_masker.inverse_transform(seed_based_correlations.T)
                seed_based_correlation_img.to_filename(os.path.join(sca_dir,'%s_%s_sca_z.nii.gz'%(subject, seed_name)))

make_functional_derivatives(tourettome_subjects, tourettome_workspace, tourettome_freesurfer, tourettome_derivatives)




