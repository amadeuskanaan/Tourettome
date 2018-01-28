__author__ = 'kanaan 01.01.2018'

import os
import shutil
import subprocess
import commands
import numpy as np
import nibabel as nb
from nilearn.input_data import NiftiLabelsMasker, NiftiMasker
from sklearn import preprocessing
from nilearn import surface
from algorithms.fast_ecm import fastECM
from utilities.utils import *
from variables.subject_list import *
from plotting.plot_surf import return_fsaverage_data

freesurfer_dir = '/data/pt_nmr093_gts/freesurfer'
fsaverage5 = return_fsaverage_data(freesurfer_dir, 'fsaverage5')

# Calculate functional derivatives

FD_outliers = control_outliers + patient_outliers

def make_group_masks(population, workspace_dir, derivatives_dir, outliers):

    print '##############################'
    print 'Creating Group GM Mask '
    derivatives_dir = mkdir_path(os.path.join(derivatives_dir, 'func_centrality'))
    gm_group_mask = os.path.join(derivatives_dir, 'GROUP_GM_FUNC_3mm.nii')


    # drop outlier subjects
    population = [i for i in population if i not in outliers]

    if not os.path.isfile(gm_group_mask):
        gm_masks_list = ' '.join(['%s -add' %(os.path.join(workspace_dir, subject, 'REGISTRATION/REST_GM_MNI3mm.nii.gz'))
                        for subject in population])[:-4]

        os.system('fslmaths %s -thrp 25 -bin %s' %(gm_masks_list, gm_group_mask))
        os.system('gunzip %s'%gm_group_mask)


def make_functional_derivatives(population, workspace_dir, freesurfer_dir, derivatives_dir):

    print '========================================================================================'
    print ''
    print '                Tourettome - 008. CREATING FUNCTIONAL FEATURES                          '
    print ''
    print '========================================================================================'

    # global IO
    sca_dir       = mkdir_path(os.path.join(derivatives_dir, 'func_seed_correlation'))
    ecm_dir       = mkdir_path(os.path.join(derivatives_dir, 'func_centrality'))
    gm_group_mask = os.path.join(derivatives_dir, 'func_centrality/GROUP_GM_FUNC_3mm.nii')

    count = 0
    for subject in population:
        count +=1
        print '###################################################################'
        print 'Extracting functional derivatives for subject %s' % subject

        # subject I/0
        subject_dir = os.path.join(workspace_dir, subject)
        func_denoised = os.path.join(subject_dir, 'DENOISE', 'residuals_compcor', 'residual_bp_z.nii.gz')

        ################################################################################################################
        ### 1- Seed-Based Correlation
        ################################################################################################################

        print '1. Calculating Seed-Based Correlation'

        seeds = {'STR'         : mask_str,
                 'STR3_MOTOR'  : mask_str_motor,
                 'STR3_LIMBIC' : mask_str_limbic,
                 'STR3_EXEC'   : mask_str_exec,
                 # 'CAUD'        : mask_caud,
                 # 'PUTA'        : mask_puta,
                 # 'ACCU'        : mask_accu,
                 # 'PALL'        : mask_pall,
                 # 'THAL'        : mask_thal,
                 # 'HIPP'        : mask_hipp,
                 # 'AMYG'        : mask_amyg,
                 }

        for seed_name in seeds:
            if not os.path.isfile(os.path.join(sca_dir, seed_name, '%s_sca_z.nii.gz'%subject)):
                print seed_name
                seed_dir = mkdir_path(os.path.join(sca_dir, seed_name))

                # Extract seed timeseries
                seed = seeds[seed_name]
                masker_seed = NiftiLabelsMasker(labels_img=seed, smoothing_fwhm=None, standardize=True, memory='nilearn_cache', verbose=0)
                timeseries_seed = masker_seed.fit_transform(func_denoised)
                print 'seed_timeseries_shape', timeseries_seed.shape

                # Extract brain timeseries
                masker_brain = NiftiMasker(smoothing_fwhm=None, detrend=None, standardize=True, low_pass=None,
                                           high_pass=None, t_r=None, memory='nilearn_cache', memory_level=1, verbose=0)
                timeseries_brain = masker_brain.fit_transform(func_denoised)
                print 'brain_timeseries_shape', timeseries_brain.shape

                # Seed Based Correlation
                # see Nilearn http://nilearn.github.io/auto_examples/03_connectivity/plot_seed_to_voxel_correlation.html#sphx-glr-auto-examples-03-connectivity-plot-seed-to-voxel-correlation-py
                sca = np.dot(timeseries_brain.T, timeseries_seed) / timeseries_seed.shape[0]
                sca_rz = np.arctanh(sca)
                print("seed-based correlation Fisher-z transformed: min = %.3f; max = %.3f" % (sca_rz.min(), sca_rz.max()))

                # Save seed-to-brain correlation as a  Nifti image
                sca_img = masker_brain.inverse_transform(sca.T)
                sca_img.to_filename(os.path.join(seed_dir, '%s_sca_z.nii.gz'%subject))

                # skip the nilearn approach..... do it with freesurfer...
                # Map seed-to-voxel onto surface
                # sca_lh = surface.vol_to_surf(sca_img, fsaverage5['pial_left']).ravel()
                # sca_rh = surface.vol_to_surf(sca_img, fsaverage5['pial_right']).ravel()
                #
                # # Save seed-to-vertex correlation as a txt file
                # np.save(os.path.join(seed_dir, '%s_sca_z_fwhm6_lh.npy'%subject), sca_lh)
                # np.save(os.path.join(seed_dir, '%s_sca_z_fwhm6_rh.npy'%subject), sca_rh)

            seed_dir = os.path.join(sca_dir, seed_name)
            if not os.path.isfile(os.path.join(seed_dir, '%s_sca_z_fsaverage5_fwhm10_rh.mgh' % subject)):
                os.chdir(seed_dir)
                for hemi in  ['lh', 'rh']:
                    # vol2surf
                    os.system('mri_vol2surf '
                              '--mov %s_sca_z.nii.gz '
                              '--regheader %s '
                              '--projfrac-avg 0.2 0.8 0.1 '
                              '--interp nearest '
                              '--hemi %s '
                              '--out %s_sca_z_%s.mgh'
                              %(subject, subject, hemi, subject, hemi))
                    #surf2surf
                    os.system('mri_surf2surf '
                              '--s %s '
                              '--sval  %s_sca_z_%s.mgh '
                              '--hemi %s '
                              '--trgsubject fsaverage5 '
                              '--fwhm-src 10 '
                              '--tval %s_sca_z_fsaverage5_fwhm10_%s.mgh'
                              %(subject, subject, hemi, hemi, subject, hemi))


        #
        # ################################################################################################################
        # ### 2- Eigenvector Centrality
        # ################################################################################################################
        #
        # print '2. Calculating Eigenvector-centraliy'
        #
        # if not os.path.isfile(os.path.join(ecm_dir, subject, 'residual_bp_z_fwhm6_normECM.nii')):
        #     # Create ECM subject dir in derivatives folder....
        #     ecm_dir_subject = mkdir_path(os.path.join(ecm_dir, subject))
        #
        #     #copy denoised file locally. done since matlab code needs to be in the same folder..
        #     os.chdir(ecm_dir_subject)
        #     os.system('cp %s ./'%func_denoised)
        #
        #     # gzip.. important for maltab
        #     os.system('gunzip residual_bp_z_fwhm6.nii.gz')
        #
        #     print '...... Runnning ECM for subject', subject
        #     # run fast ecm
        #     matlab_cmd = ['matlab', '-version', '8.2', '-nodesktop', '-nosplash', '-nojvm',
        #                   # fastECM( inputfile, rankmap, normmap, degmap, maxiter, maskfile, atlasfile )
        #                   '-r "fastECM(\'residual_bp_z_fwhm6.nii\', \'1\', \'1\', \'1\', \'20\', \'%s\') ; quit;"' %
        #                   (gm_group_mask)]
        #     subprocess.call(matlab_cmd)
        #
        #     # clean folder
        #     os.system('rm -rf residual_bp_z_fwhm6.nii')
        #
        # # Map ECM to surface and save
        # if not os.path.isfile(os.path.join(ecm_dir, '%s_ecm_z_fwhm6_lh.npy' % subject)):
        #     ecm_lh = surface.vol_to_surf('residual_bp_z_fwhm6_normECM.nii', fsaverage5['pial_left']).ravel()
        #     ecm_rh = surface.vol_to_surf('residual_bp_z_fwhm6_normECM.nii', fsaverage5['pial_right']).ravel()
        #     np.save('../%s_ecm_z_fwhm6_lh.npy' % subject, ecm_lh)
        #     np.save('../%s_ecm_z_fwhm6_rh.npy' % subject, ecm_rh)



# make_group_masks(tourettome_subjects, tourettome_workspace, tourettome_derivatives, FD_outliers)
make_functional_derivatives(tourettome_subjects, tourettome_workspace, tourettome_freesurfer, tourettome_derivatives)
# make_functional_derivatives(hannover_a+hannover_b, tourettome_workspace, tourettome_freesurfer, tourettome_derivatives)
# make_functional_derivatives(paris[50:], tourettome_workspace, tourettome_freesurfer, tourettome_derivatives)




