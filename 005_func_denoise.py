__author__ = 'kanaan 22.03.2017'

import os
import sys
import nibabel as nb
from CPAC.nuisance.nuisance import calc_residuals, extract_tissue_data
from utilities.utils import *
from variables.subject_list import *
from quality.motion_statistics import *

# assert len(sys.argv)== 2
# subject_index=int(sys.argv[1])

#requires FSL5, FREESURFER, CPAC

def nuisance_signal_regression(population, workspace_dir):

    for subject in population:
        # subject = population[subject_index]
        print '###############################################################################'
        print 'Denoising Functional Data for subject %s' % subject
        print ''

        # Input
        subdir   = os.path.join(workspace_dir, subject)
        func_mni = os.path.join(subdir, 'REGISTRATION/REST_EDIT_UNI_BRAIN_MNI3mm.nii.gz')
        TR       = nb.load(os.path.join(subdir, 'FUNCTIONAL/REST.nii.gz')).header['pixdim'][4]

        # Output
        nuisance_dir = mkdir_path(os.path.join(subdir, 'DENOISE'))
        signals_dir     = mkdir_path(os.path.join(nuisance_dir, 'tissue_signals'))

        # Smoothing kernel
        FWHM     = 6
        sigma    = FWHM / 2.35482004503

        # Band-pass frequencies
        ##sigma = 1 / (2 * TR * cutoff_in_hz)
        ## #https://www.jiscmail.ac.uk/cgi-bin/webadmin?A2=ind1205&L=FSL&P=R57592&1=FSL&9=A&I=-3&J=on&d=No+Match%3BMatch%3BMatches&z=4
        highpass_cutoff = 0.01 #hz
        lowpass_cutoff  = 0.1  #hz
        highpass_sigma  = 1./(2.*TR*highpass_cutoff)
        lowpass_sigma   = 1./(2.*TR*lowpass_cutoff)

        print 'TR=%ss'%TR
        print 'Highpass filter=', highpass_sigma
        print 'Lowpass filter=', lowpass_sigma
        print 'FWHM=', FWHM

        # Calculate Friston-24 paramters
        os.chdir(nuisance_dir)
        movpar  = os.path.join(subdir, 'FUNCTIONAL/moco/REST_EDIT_moco2.par')
        friston = os.path.join(subdir, 'DENOISE/FRISTON_24.1D')
        calc_friston_twenty_four(movpar)

        # id bad frames
        FD1D      = np.loadtxt(calculate_FD_Power(movpar))
        fd_frames_in = [frame for frame, val in enumerate(FD1D) if val < 0.2]
        print 'LEN_FD1D=', len(FD1D)
        print 'LEN_FD_frames_in=',  len(np.array(fd_frames_in)
        print 'Percentage of Good frames =' (len(np.array(fd_frames_in)) / len(FD1D) )* 100
        fd_frames_ex = set_frames_ex(in_file = FD1D, threshold=0.2, frames_before=1, frames_after=1)


        # extract tissue data
        if not os.path.isfile( os.path.join(signals_dir, 'wm_signals.npy')):
            print '......extracting tissue data'
            os.chdir(signals_dir)
            extract_tissue_data(data_file=func_mni, ventricles_mask_file=mni_HOLV_3mm,
                                wm_seg_file=os.path.join(subdir, 'REGISTRATION/REST_WM_MNI3mm.nii.gz'),
                                csf_seg_file=os.path.join(subdir, 'REGISTRATION/REST_CSF_MNI3mm.nii.gz'),
                                gm_seg_file=os.path.join(subdir, 'REGISTRATION/REST_GM_MNI3mm.nii.gz'))

        ################################################################################################################
        ######## Denoise MNI FUNC

        # 1- Detrend (Linear-Quadratic), Motion-24, WM/CSF mean signal
        # 2- Detrend (Linear-Quadratic), Motion-24, Compcor
        # 3- ICA-AROMA, Detrend (Linear-Quadratic), Motion-24, WM/CSF mean signal

        ################################################################################################################

        wmsig  = os.path.join(signals_dir, 'wm_signals.npy')
        csfsig = os.path.join(signals_dir, 'csf_signals.npy')
        gmsig  = os.path.join(signals_dir, 'gm_signals.npy')

        def denoise(denoise_type, data, selector, wmsig  = wmsig, csfsig = csfsig, gmsig  = gmsig, frames_ex=None):

            run_dir = mkdir_path(os.path.join(nuisance_dir, 'residuals_%s'%denoise_type))

            os.chdir(run_dir)
            if not os.path.isfile(os.path.join(run_dir, 'residual_bp_z_fwhm6.nii.gz')):

                if not os.path.isfile(os.path.join(run_dir, 'residual_bp.nii.gz')):
                    print '......calculating residual image'
                    calc_residuals(data,
                                   selector     =  selector,
                                   wm_sig_file  = wmsig,
                                   csf_sig_file =  csfsig,
                                   gm_sig_file  =  gmsig,
                                   motion_file  =  friston,
                                   compcor_ncomponents=0,
                                   frames_ex    = frames_ex)

                    print '......bandpass filtering'
                    os.system('fslmaths residual -bptf %s %s residual_bp' % (highpass_sigma, lowpass_sigma))

                print '...... standradizing data'
                expr = ['log((a+1)/(a-1))/2']
                os.system('3dcalc -a residual_bp.nii.gz -expr %s -prefix residual_bp_z.nii.gz' %expr)

                print '...... smooth data'
                os.system('fslmaths residual_bp_z -s %s residual_bp_z_fwhm6.nii.gz' % (sigma))

            if not os.path.isfile(os.path.join(run_dir, 'residual_bp_z_rh.mgh')):
                print '...... project to surface' #### take non-smoothed data and smooth on surface
                for hemi in ['lh', 'rh']:
                    os.system('mri_vol2surf '
                              '--mov residual_bp_z.nii.gz '
                              '--reg %s '
                              '--trgsubject fsaverage5 '
                              '--projfrac-avg 0.2 0.8 0.1 '
                              '--hemi %s '
                              '--interp nearest '
                              #'--fwhm 6 ' 
                              '--cortex '
                              '--o residual_bp_z_%s.mgh'
                              % (fs_mni_reg, hemi, hemi))

        ################################################################################################################

        # 1- Detrend (Linear-Quadratic + Motion-24 +  Compcor n5

        print '- Nuisance Signal regression :::: FUNC2mm_detrend_compcor_moco24_bp_std_fwhm '
        selector_cc = {'wm': False, 'csf': False, 'motion': True, 'linear': True, 'quadratic': True,
                        'compcor': True,  'gm' : False, 'global': False, 'pc1'  : False}
        denoise(denoise_type='compcor', data=func_mni, selector=selector_cc)

        #2- Detrend (Linear-Quadratic), Motion-24, Compcor, GSR
        print '- Nuisance Signal regression :::: FUNC2mm_detrend_compcor_moco24_global_bp_std_fwhm '
        selector_gsr = {'wm': False, 'csf': False, 'motion': True, 'linear': True, 'quadratic': True,
                       'compcor': True, 'gm': False, 'global': True, 'pc1': False}
        denoise(denoise_type='gsr', data=func_mni, selector=selector_gsr)


        #3- Detrend (Linear-Quadratic), Motion-24, Compcor, Censoring
        selector_censor = {'wm': False, 'csf': False, 'motion': True, 'linear': True, 'quadratic': True,
                           'compcor': True, 'gm': False, 'global': False, 'pc1': False}
        denoise(denoise_type='censoring', data=func_mni, selector=selector_censor, frames_ex=fd_frames_ex)

# nuisance_signal_regression(tourettome_subjects, tourettome_workspace)
nuisance_signal_regression(paris, tourettome_workspace)


