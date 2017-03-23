__author__ = 'kanaan 22.03.2017'

import os
from variables.subject_list import *
from utilities.utils import *
import nibabel as nb

import nipype
from nipype.utils import config
from nipype.interfaces import fsl
from CPAC.nuisance.nuisance import calc_residuals, extract_tissue_data



def nuisance_signal_regression(population, workspace_dir):

    for subject in population:
        print '###############################################################################'
        print 'Denoising Functional Data for subject %s' % subject
        print ''


        #input
        subdir   = os.path.join(workspace_dir, subject)
        func_mni = os.path.join(subdir, 'REGISTRATION/REST_EDIT_BRAIN_UNIMOCO_MNI2mm.nii.gz')
        TR       = nb.load(os.path.join(subdir, 'FUNCTIONAL/REST.nii.gz')).header['pixdim'][4]
        FWHM     = 4.
        sigma    = FWHM / 2.35482004503

        lowpass_sigma  = 1./(2*TR*0.1)
        highpass_sigma = 1./(2*TR*0.01)

        #output
        nuisance_dir = mkdir_path(os.path.join(subdir, 'DENOISE'))
        aroma_dir    = mkdir_path(os.path.join(nuisance_dir, 'ica_aroma'))

        # calculate friston paramters
        os.chdir(nuisance_dir)
        movpar  = os.path.join(subdir, 'FUNCTIONAL/moco/REST_EDIT_moco2.1D' )
        friston = os.path.join(subdir, 'FUNC_DENOISE/FRISTON_24.1D')
        if not os.path.isfile(friston):
            calc_friston_twenty_four(movpar)


        # Denoise MNI FUNC
        print '- Nuisance Signal regression on MNI FUNC :::: fwhm_ICAAROMA_detrend_wmcsf_moco6 '

        if not os.path.isfile(os.path.join(aroma_dir, 'denoised_func_data_nonaggr.nii.gz')):
            os.chdir(aroma_dir)

            print '......smoothing to FWHM=4mm'
            os.system('fslmaths %s -s %s REST_EDIT_BRAIN_UNIMOCO_MNI2mm_fwhm4mm.nii.gz' %(func_mni, sigma))
            os.system('fslmaths %s -Tmean -bin REST_EDIT_BRAIN_UNIMOCO_MNI2mm_mask'%func_mni)

            print '......ica_aroma'
            os.system('python /scr/sambesi1/Software/ICA-AROMA/ICA_AROMA.py '
                      '-in %s '
                      '-out %s '
                      '-mc %s '
                      '-m %s '
                      '-tr %s'
                      %(os.path.join(aroma_dir, 'REST_EDIT_BRAIN_UNIMOCO_MNI2mm_fwhm4mm.nii.gz'),
                        aroma_dir,
                        movpar,
                        os.path.join(aroma_dir, 'REST_EDIT_BRAIN_UNIMOCO_MNI2mm_mask.nii.gz'),
                        TR))


            # print '......extracting tissue data'
            #
            # extract_tissue_data(data_file = os.path.join(aroma_dir, 'denoised_func_data_nonaggr.nii.gz'),
            #                     ventricles_mask_file = mni_HOLV_2mm,
            #                     wm_seg_file  = os.path.join(subdir, 'REGISTRATION/ANATOMICAL_WM_MNI2mm.nii.gz'),
            #                     csf_seg_file = os.path.join(subdir, 'REGISTRATION/ANATOMICAL_CSF_MNI2mm.nii.gz'),
            #                     gm_seg_file  = os.path.join(subdir, 'REGISTRATION/ANATOMICAL_GM_MNI2mm.nii.gz'))
            #
            # print '......calculating residual image'
            # selector = {'wm': True, 'csf': True, 'motion': True, 'linear': True, 'quadratic': True,
            #             'compcor': False, 'gm': False, 'global': False, 'pc1': False}
            #
            # calc_residuals(os.path.join(aroma_dir, 'denoised_func_data_nonaggr.nii.gz'),
            #                selector     = selector,
            #                wm_sig_file  = os.path.join(aroma_dir, 'wm_signals.npy'),
            #                csf_sig_file = os.path.join(aroma_dir, 'csf_signals.npy'),
            #                gm_sig_file  = os.path.join(aroma_dir, 'gm_signals.npy'),
            #                motion_file  = movpar,
            #                compcor_ncomponents=0)

        print '......bandpass filtering'

        print lowpass_sigma
        print highpass_sigma


        os.system('fslmaths residual -bptf %s %s residual_bp' %(highpass_sigma, lowpass_sigma))

        # bp = fsl.TemporalFilter()
        # bp.inputs.in_file = os.path.join(aroma_dir, 'residual.nii.gz')#
        # bp.inputs.highpass_sigma =  highpass_sigma
        # bp.inputs.lowpass_sigma =  lowpass_sigma
        # bp.inputs.out_file  = os.path.join(aroma_dir, 'residual_bp.nii.gz')#
        # print bp.cmdline


nuisance_signal_regression(['HB012'], tourettome_workspace)