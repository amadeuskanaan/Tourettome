__author__ = 'kanaan 22.03.2017'

import os

import nibabel as nb
from CPAC.nuisance.nuisance import calc_residuals, extract_tissue_data

from utilities.utils import *
from variables.subject_list import *
from quality.motion_statistics import *

#assert len(sys.argv)== 2
#subject_index=int(sys.argv[1])

def nuisance_signal_regression(population, workspace_dir):

    for subject in population:
        #subject = population[subject_index]
        print '###############################################################################'
        print 'Denoising Functional Data for subject %s' % subject
        print ''

        # Input
        subdir   = os.path.join(workspace_dir, subject)
        func_mni = os.path.join(subdir, 'REGISTRATION/REST_EDIT_UNI_BRAIN_MNI2mm.nii.gz')
        TR       = nb.load(os.path.join(subdir, 'FUNCTIONAL/REST.nii.gz')).header['pixdim'][4]

        # Output
        nuisance_dir = mkdir_path(os.path.join(subdir, 'DENOISE'))
        #aroma_dir    = mkdir_path(os.path.join(nuisance_dir, 'residuals_ica_aroma'))
        #compcor_dir  = mkdir_path(os.path.join(nuisance_dir, 'residuals_compcor'))
        wmcsf_dir    = mkdir_path(os.path.join(nuisance_dir, 'residuals_wmcsf'))

        # Smoothing kernel
        FWHM     = 4.
        sigma    = FWHM / 2.35482004503

        # Band-pass frequencies
        lowpass_sigma  = 1./(2*TR*0.1)
        highpass_sigma = 1./(2*TR*0.01)

        print 'FWHM=', FWHM
        print 'Lowpass filter=', lowpass_sigma
        print 'Highpass filter=', highpass_sigma

        # Calculate Friston-24 paramters
        os.chdir(nuisance_dir)
        movpar  = os.path.join(subdir, 'FUNCTIONAL/moco/REST_EDIT_moco2.par')
        friston = os.path.join(subdir, 'DENOISE/FRISTON_24.1D')
        calc_friston_twenty_four(movpar)

        ################################################################################################################
        ######## Denoise MNI FUNC

        # 1- Detrend (Linear-Quadratic), Motion-24, WM/CSF mean signal
        # 2- Detrend (Linear-Quadratic), Motion-24, Compcor
        # 3- ICA-AROMA, Detrend (Linear-Quadratic), Motion-24, WM/CSF mean signal

        ################################################################################################################

        print '- Nuisance Signal regression :::: FUNC2mm_fwhm_detrend_wmcsf_moco24 '

        if not os.path.isfile(os.path.join(nuisance_dir, 'REST2mm_fwhm_detrend_wmcsf_moco24_bp.nii.gz')):
            print '......extracting tissue data'

            os.chdir(wmcsf_dir)

            extract_tissue_data(data_file= func_mni,
                                ventricles_mask_file=mni_HOLV_2mm,
                                wm_seg_file=os.path.join(subdir, 'REGISTRATION/ANATOMICAL_WM_MNI2mm.nii.gz'),
                                csf_seg_file=os.path.join(subdir, 'REGISTRATION/ANATOMICAL_CSF_MNI2mm.nii.gz'),
                                gm_seg_file=os.path.join(subdir, 'REGISTRATION/ANATOMICAL_GM_MNI2mm.nii.gz'))

            print '......calculating residual image'
            selector = {'wm': True, 'csf': True, 'motion': True, 'linear': True, 'quadratic': True,
                        'compcor': False, 'gm': False, 'global': False, 'pc1': False}
            calc_residuals(func_mni,
                           selector=selector,
                           wm_sig_file=os.path.join(wmcsf_dir, 'wm_signals.npy'),
                           csf_sig_file=os.path.join(wmcsf_dir, 'csf_signals.npy'),
                           gm_sig_file=os.path.join(wmcsf_dir, 'gm_signals.npy'),
                           motion_file=friston,
                           compcor_ncomponents=0)
            print '......bandpass filtering'
            os.system('fslmaths residual -bptf %s %s residual_bp' % (highpass_sigma, lowpass_sigma))
            os.system('cp residual_bp.nii.gz ../REST_MNI2mm_detrend_wmcsf_moco24_bp.nii.gz')


        # # project to surface
        #
        # os.chdir(nuisance_dir)
        #
        # for hemi in ['lh', 'rh']:
        #     os.system('mri_vol2surf '
        #               '--mov REST_MNI2mm_detrend_wmcsf_moco24_bp.nii.gz '
        #               '--reg %s '
        #               '--projfrac-avg 0.2 0.8 0.2 '
        #               '--hemi %s '
        #               '--interp nearest '
        #               '--surf-fwhm 6 '
        #               '--o REST_MNI2mm_detrend_wmcsf_moco24_bp.mgh'
        #               %(fs_mni_reg, hemi))



        #mri_vol2surf --mov zstat.nii.gz --hemi lh --surf white --reg mni152.register.dat --projfrac-avg 0 1 0.1 --surf-fwhm 3 --o pysurfer-v2sYDQWQ_.mgz


        # os.system('mri_vol2surf --mov R1.mgz --regheader %s --projfrac-avg %s --interp nearest --hemi %s '
        #           '--out %s_%s_%s_R1.mgh '
        #           % (subject, proj_fracs[depth], hemi,
        #              subject, depth, hemi,
        #              ))


        ################################################################################################################
        ################################################################################################################

        # print '- Nuisance Signal regression :::: FUNC2mm_fwhm_detrend_compcor_moco24 '
        #
        # if not os.path.isfile(os.path.join(nuisance_dir, 'REST2mm_fwhm_detrend_compcor_moco24_bp.nii.gz')):
        #     os.chdir(wmcsf_dir)
        #     print '......calculating residual image'
        #     selector = {'wm': False, 'csf': False, 'motion': True, 'linear': True, 'quadratic': True,
        #                 'compcor': True, 'gm': False, 'global': False, 'pc1': False}
        #     calc_residuals(func_mni,
        #                    selector=selector,
        #                    wm_sig_file=os.path.join(wmcsf_dir, 'wm_signals.npy'),
        #                    csf_sig_file=os.path.join(wmcsf_dir, 'csf_signals.npy'),
        #                    gm_sig_file=os.path.join(wmcsf_dir, 'gm_signals.npy'),
        #                    motion_file=friston,
        #                    compcor_ncomponents=0)
        #     print '......bandpass filtering'
        #     os.system('fslmaths residual -bptf %s %s residual_bp' % (highpass_sigma, lowpass_sigma))
        #     os.system('cp residual_bp.nii.gz ../REST_MNI2mm_detrend_compcor_moco24_bp.nii.gz')

        ################################################################################################################
        ################################################################################################################

        # print '- Nuisance Signal regression :::: FUNC2mm_fwhm_ICA-AROMA_detrend_wmcsf_moco24 '
        #
        # if not os.path.isfile(os.path.join(aroma_dir, 'denoised_func_data_nonaggr.nii.gz')):
        #     os.chdir(aroma_dir)
        #
        #     print '......smoothing to FWHM=4mm'
        #     os.system('fslmaths %s -s %s REST_EDIT_UNI_BRAIN_MNI2mm_fwhm4mm.nii.gz' %(func_mni, sigma))
        #     os.system('fslmaths %s -Tmean -bin REST_EDIT_UNI_BRAIN_MNI2mm_mask'%func_mni)
        #
        #     print '......ica_aroma'
        #     os.system('python /scr/sambesi1/Software/ICA-AROMA/ICA_AROMA.py '
        #               '-in %s -out %s -mc %s -m %s -tr %s'
        #               %(os.path.join(aroma_dir, 'REST_EDIT_UNI_BRAIN_MNI2mm_fwhm4mm.nii.gz'),
        #                 aroma_dir, movpar, os.path.join(aroma_dir, 'REST_EDIT_UNI_BRAIN_MNI2mm_mask.nii.gz'),TR))
        #
        #
        #     print '......extracting tissue data'
        #     extract_tissue_data(data_file = os.path.join(aroma_dir, 'denoised_func_data_nonaggr.nii.gz'),
        #                          ventricles_mask_file = mni_HOLV_2mm,
        #                          wm_seg_file  = os.path.join(subdir, 'REGISTRATION/ANATOMICAL_WM_MNI2mm.nii.gz'),
        #                          csf_seg_file = os.path.join(subdir, 'REGISTRATION/ANATOMICAL_CSF_MNI2mm.nii.gz'),
        #                          gm_seg_file  = os.path.join(subdir, 'REGISTRATION/ANATOMICAL_GM_MNI2mm.nii.gz'))
        #
        #     print '......calculating residual image'
        #     selector = {'wm': True, 'csf': True, 'motion': True, 'linear': True, 'quadratic': True,
        #                 'compcor': False, 'gm': False, 'global': False, 'pc1': False}
        #     calc_residuals(os.path.join(aroma_dir, 'denoised_func_data_nonaggr.nii.gz'),
        #                    selector     = selector,
        #                    wm_sig_file  = os.path.join(aroma_dir, 'wm_signals.npy'),
        #                    csf_sig_file = os.path.join(aroma_dir, 'csf_signals.npy'),
        #                    gm_sig_file  = os.path.join(aroma_dir, 'gm_signals.npy'),
        #                    motion_file  = friston,
        #                    compcor_ncomponents=0)
        #
        #     print '......bandpass filtering'
        #     os.system('fslmaths residual -bptf %s %s residual_bp' %(highpass_sigma, lowpass_sigma))
        #     os.system('cp residual_bp.nii.gz ../REST_MNI2mm_fwhm_aroma_detrend_compcor_moco24_bp.nii.gz')


nuisance_signal_regression(tourettome_subjects, tourettome_workspace)
# nuisance_signal_regression(paris[50:], tourettome_workspace)
# nuisance_signal_regression(hannover_a, tourettome_workspace)