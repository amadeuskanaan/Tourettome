__author__ = 'kanaan 22.03.2017'

import os
import sys
import nibabel as nb
from CPAC.nuisance.nuisance import calc_residuals, extract_tissue_data
from utilities.utils import *
from variables.subject_list import *
from quality.motion_statistics import *

assert len(sys.argv)== 2
subject_index=int(sys.argv[1])


#requires FSL5, FREESURFER, CPAC

def nuisance_signal_regression(population, workspace_dir):

    # for subject in population:
        subject = population[subject_index]
        print '###############################################################################'
        print 'Denoising Functional Data for subject %s' % subject
        print ''

        # Input
        subdir   = os.path.join(workspace_dir, subject)
        func_mni = os.path.join(subdir, 'REGISTRATION/REST_EDIT_UNI_BRAIN_MNI2mm.nii.gz')
        TR       = nb.load(os.path.join(subdir, 'FUNCTIONAL/REST.nii.gz')).header['pixdim'][4]

        # Output
        nuisance_dir = mkdir_path(os.path.join(subdir, 'DENOISE'))
        wmcsf_dir    = mkdir_path(os.path.join(nuisance_dir, 'residuals_wmcsf'))
        aroma_dir    = mkdir_path(os.path.join(nuisance_dir, 'residuals_ica_aroma'))
        compcor_dir  = mkdir_path(os.path.join(nuisance_dir, 'residuals_compcor'))

        # Smoothing kernel
        FWHM     = '6'
        sigma    = FWHM / 2.35482004503

        # Band-pass frequencies  #https://www.jiscmail.ac.uk/cgi-bin/webadmin?A2=ind1205&L=FSL&P=R57592&1=FSL&9=A&I=-3&J=on&d=No+Match%3BMatch%3BMatches&z=4
        ##sigma = 1 / (2 * TR * cutoff_in_hz)
        highpass_cutoff = 0.01 #hz
        lowpass_cutoff  = 0.1  #hz
        highpass_sigma  = 1./(2*TR*highpass_cutoff)
        lowpass_sigma   = 1./(2*TR*lowpass_cutoff)

        print 'TR=%ss'%TR
        print 'Highpass filter=', highpass_sigma
        print 'Lowpass filter=', lowpass_sigma
        print 'FWHM=', FWHM

        # Calculate Friston-24 paramters
        os.chdir(nuisance_dir)
        movpar  = os.path.join(subdir, 'FUNCTIONAL/moco/REST_EDIT_moco2.par')
        friston = os.path.join(subdir, 'DENOISE/FRISTON_24.1D')
        calc_friston_twenty_four(movpar)


        # extract tissue data
        if not os.path.isfile( os.path.join(wmcsf_dir, 'wm_signals.npy')):
            print '......extracting tissue data'
            os.chdir(wmcsf_dir)
            extract_tissue_data(data_file=func_mni,
                                ventricles_mask_file=mni_HOLV_2mm,
                                wm_seg_file=os.path.join(subdir, 'REGISTRATION/ANATOMICAL_WM_MNI2mm.nii.gz'),
                                csf_seg_file=os.path.join(subdir, 'REGISTRATION/ANATOMICAL_CSF_MNI2mm.nii.gz'),
                                gm_seg_file=os.path.join(subdir, 'REGISTRATION/ANATOMICAL_GM_MNI2mm.nii.gz'))

        ################################################################################################################
        ######## Denoise MNI FUNC

        # 1- Detrend (Linear-Quadratic), Motion-24, WM/CSF mean signal
        # 2- Detrend (Linear-Quadratic), Motion-24, Compcor
        # 3- ICA-AROMA, Detrend (Linear-Quadratic), Motion-24, WM/CSF mean signal

        ################################################################################################################

        def denoise(run_dir, data, selector):

            print '......calculating residual image'
            os.chdir(run_dir)
            if not os.path.isfile(os.path.join(run_dir, 'residual_bp_z_fwhm%s.nii.gz'%FWHM)):
                calc_residuals(data,
                               selector     =  selector,
                               wm_sig_file  =  os.path.join(wmcsf_dir, 'wm_signals.npy'),
                               csf_sig_file =  os.path.join(wmcsf_dir, 'csf_signals.npy'),
                               gm_sig_file  =  os.path.join(wmcsf_dir, 'gm_signals.npy'),
                               motion_file  =  friston,
                               compcor_ncomponents=0)

                print '......bandpass filtering'
                os.system('fslmaths residual -bptf %s %s residual_bp' % (highpass_sigma, lowpass_sigma))

                print '...... standradizing data'
                expr = ['log((a+1)/(a-1))/2']
                os.system('3dcalc -a residual_bp.nii.gz -expr %s -prefix residual_bp_z.nii.gz' %expr)

                print '...... smooth data'
                os.system('fslmaths residual_bp_z -s %s residual_bp_z_fwhm%s.nii.gz' % (sigma,FWHM))

            print '...... project to surface' #### take non-smoothed data and smooth on surface
            for hemi in ['lh', 'rh']:
                os.system('mri_vol2surf '
                          '--mov residual_bp_z.nii.gz '
                          '--reg %s '
                          '--trgsubject fsaverage5 '
                          '--projfrac-avg 0.2 0.8 0.1 '
                          '--hemi %s '
                          '--interp nearest '
                          '--surf-fwhm 6 '
                          '--cortex '
                          '--o residual_bp_z_%s.mgh'
                          % (fs_mni_reg, hemi, hemi))


        ################################################################################################################

        # 1- Detrend (Linear-Quadratic), Motion-24, WM/CSF mean signal

        print '- Nuisance Signal regression :::: FUNC2mm_fwhm_detrend_wmcsf_moco24 '

        selector_std = {'wm'     : True, 'csf': True,  'motion': True,  'linear': True, 'quadratic': True,
                        'compcor': False, 'gm': False, 'global': False, 'pc1'   : False}
        denoise(run_dir=wmcsf_dir,data=func_mni, selector=selector_std)


        # 2- Detrend (Linear-Quadratic), Motion-24, Compcor

        print '- Nuisance Signal regression :::: FUNC2mm_fwhm_detrend_compcor_moco24 '

        selector_cc = {'wm'     : False, 'csf': False, 'motion': True, 'linear': True, 'quadratic': True,
                        'compcor': True,  'gm' : False, 'global': False, 'pc1'  : False}
        denoise(run_dir=compcor_dir, data=func_mni, selector=selector_cc)

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
        # #                 aroma_dir, movpar, os.path.join(aroma_dir, 'REST_EDIT_UNI_BRAIN_MNI2mm_mask.nii.gz'),TR))
        # #
        # #
        # #     print '......extracting tissue data'
        # #     extract_tissue_data(data_file = os.path.join(aroma_dir, 'denoised_func_data_nonaggr.nii.gz'),
        # #                          ventricles_mask_file = mni_HOLV_2mm,
        # #                          wm_seg_file  = os.path.join(subdir, 'REGISTRATION/ANATOMICAL_WM_MNI2mm.nii.gz'),
        # #                          csf_seg_file = os.path.join(subdir, 'REGISTRATION/ANATOMICAL_CSF_MNI2mm.nii.gz'),
        # #                          gm_seg_file  = os.path.join(subdir, 'REGISTRATION/ANATOMICAL_GM_MNI2mm.nii.gz'))
        # #
        # #     print '......calculating residual image'
        # #     selector = {'wm': True, 'csf': True, 'motion': True, 'linear': True, 'quadratic': True,
        # #                 'compcor': False, 'gm': False, 'global': False, 'pc1': False}
        # #     calc_residuals(os.path.join(aroma_dir, 'denoised_func_data_nonaggr.nii.gz'),
        # #                    selector     = selector,
        # #                    wm_sig_file  = os.path.join(aroma_dir, 'wm_signals.npy'),
        # #                    csf_sig_file = os.path.join(aroma_dir, 'csf_signals.npy'),
        # #                    gm_sig_file  = os.path.join(aroma_dir, 'gm_signals.npy'),
        # #                    motion_file  = friston,
        # #                    compcor_ncomponents=0)
        # #
        # #     print '......bandpass filtering'
        # #     os.system('fslmaths residual -bptf %s %s residual_bp' %(highpass_sigma, lowpass_sigma))
        # #     os.system('cp residual_bp.nii.gz ../REST_MNI2mm_fwhm_aroma_detrend_compcor_moco24_bp.nii.gz')


nuisance_signal_regression(['LZ004', 'LZ030', 'LZ053'], tourettome_workspace)
# nuisance_signal_regression(tourettome_subjects, tourettome_workspace)
