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
        func_denoised = os.path.join(subject_dir, 'DENOISE/residuals_compcor/residual_bp_fwhm.nii.gz')

        ################################################################################################################
        ### 1- Seed-Based Correlation
        ################################################################################################################

        print '1. Calculating Seed-Based Correlation'

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

        for seed_name in seeds:
            if not os.path.isfile(os.path.join(sca_dir, '%s_sca_z_fwhm6.nii.gz'%subject)):
                print seed_name

                # Extract seed timeseries
                seed = seeds[seed_name]
                masker_seed = NiftiLabelsMasker(labels_img=seed, smoothing_fwhm=None, standardize=True, memory='nilearn_cache', verbose=0)
                timeseries_seed = masker_seed.fit_transform(func_denoised)
                print 'seed_timeseries_shape', timeseries_seed.shape

                # Extract brain timeseries
                masker_brain = NiftiMasker(smoothing_fwhm=None, detrend=None, standardize=True, low_pass=None,
                                           high_pass=None, t_r=2., memory='nilearn_cache', memory_level=1, verbose=0)
                timeseries_brain = masker_brain.fit_transform(func_denoised)
                print 'brain_timeseries_shape', timeseries_brain.shape

                # Seed Based Correlation
                # see Nilearn http://nilearn.github.io/auto_examples/03_connectivity/plot_seed_to_voxel_correlation.html#sphx-glr-auto-examples-03-connectivity-plot-seed-to-voxel-correlation-py
                sca = np.dot(timeseries_brain.T, timeseries_seed) / timeseries_seed.shape[0]
                sca_rz = np.arctanh(sca)
                print("seed-based correlation Fisher-z transformed: min = %.3f; max = %.3f" % (sca_rz.min(), sca_rz.max()))

                # Save seed-to-brain correlation as a  Nifti image
                sca_img = masker_brain.inverse_transform(sca.T)
                sca_img.to_filename(os.path.join(sca_dir, '%s_sca_z_fwhm6.nii.gz'%subject))

                # Map seed-to-voxel onto surface
                sca_lh = surface.vol_to_surf(sca_img, fsaverage5['pial_left']).ravel()
                sca_rh = surface.vol_to_surf(sca_img, fsaverage5['pial_right']).ravel()

                # Save seed-to-vertex correlation as a txt file
                np.save(os.path.join(sca_dir, '%s_sca_z_fwhm6_lh.npy'%subject), sca_lh)
                np.save(os.path.join(sca_dir, '%s_sca_z_fwhm6_rh.npy'%subject), sca_rh)


make_functional_derivatives(['LZ006'], tourettome_workspace, tourettome_freesurfer, tourettome_derivatives)




