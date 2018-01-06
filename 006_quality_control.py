__author__ = 'kanaan 06.01.2018'

import os
import nibabel as nb
import numpy as np
import pandas as pd
from nipype.algorithms.misc import TSNR
from quality.motion_statistics import *
from quality.spatial_qc import *
from utilities.utils import *
from variables.subject_list import *
import mriqc.qc.anatomical as mriqca

# IMAGE QUALITY METRICS

# anatomical measures based on noise measurements
#### CJV  - coefficient of joint variation
#### CNR  - contrast-to-noise ratio
#### SNR  - signal-to-noise ratio
#### SNRd - Dietrich’s SNR
#### QI2  - Mortamet’s quality index 2

# anatomical measures based on information theory
#### EFC  - Shannons entropy focus criterion
#### FBER - foreground-to-background ratio

# anatomical measures targeting specific artifacts
#### QI1  -  Mortamet’s quality index 1

# anatomical other measures
#### fwhm -  spatial distribution of the image intensity


def make_quality_control(population, workspace):
    print '========================================================================================'
    print ''
    print '                    Tourettome - 006. QUALITY CONTROL                                   '
    print ''
    print '========================================================================================'

    count = 0
    for subject in population:

        count +=1
        site_id = subject[0:2]
        subdir  = os.path.join(workspace, subject)
        qcdir   = mkdir_path(os.path.join(workspace, subject, 'QUALITY_CONTROL'))
        os.chdir(qcdir)

        columns = ['qc_anat_cjv', 'qc_ant_cnr', 'qc_anat_snr', 'qc_anat_snrd', 'qc_anat_efc', 'qc_anat_fber', 'qc_anat_fwhm',
                   'qc_func_snr', 'qc_func_efc', 'qc_func_fber', 'qc_func_fwhm', 'qc_func_fd', 'qc_func_fd_in',
                   'qc_func_fd_max', 'qc_func_dvars', 'qc_func_tsnr']

        df = pd.DataFrame(index=['%s' % subject], columns=columns)


        ############################################################################################
        #  Anatomical measures

        # Load data
        anat       = nb.load(os.path.join(subdir, 'RAW',        'ANATOMICAL.nii.gz' )).get_data()
        anat_mask  = nb.load(os.path.join(subdir, 'ANATOMICAL', 'ANATOMICAL_BRAIN_MASK.nii.gz' )).get_data()
        anat_gm    = nb.load(os.path.join(subdir, 'ANATOMICAL', 'seg_spm/c1ANATOMICAL.nii' )).get_data()
        anat_wm    = nb.load(os.path.join(subdir, 'ANATOMICAL', 'seg_spm/c2ANATOMICAL.nii' )).get_data()
        anat_csf   = nb.load(os.path.join(subdir, 'ANATOMICAL', 'seg_spm/c3ANATOMICAL.nii' )).get_data()

        # Intermediate measures
        anat_fg_mu, anat_fg_sd, anat_fg_size    = summary_mask(anat, anat_mask)
        anat_gm_mu, anat_gm_sd, anat_gm_size    = summary_mask(anat, np.where(anat_gm > 0.5, 1, 0 ))
        anat_wm_mu, anat_wm_sd, anat_wm_size    = summary_mask(anat, np.where(anat_wm > 0.5, 1, 0 ))
        anat_csf_mu, anat_gm_sd, anat_csf_size  = summary_mask(anat, np.where(anat_csf > 0.5, 1, 0 ))
        anat_bg_data, anat_bg_mask              = get_background(anat, anat_mask)
        anat_bg_mu, anat_bg_sd, anat_bg_size    = summary_mask(anat, anat_bg_mask)

        # Calculate spatial anatomical summary measures
        df.loc[subject]['qc_anat_cjv']  = mriqca.cjv(anat_wm_mu, anat_gm_mu, anat_wm_sd, anat_gm_sd)
        df.loc[subject]['qc_anat_cnr']  = mriqca.cnr(anat_wm_mu, anat_gm_mu, anat_bg_sd)
        df.loc[subject]['qc_anat_snr']  = mriqca.snr(anat_fg_mu, anat_fg_sd, anat_fg_size)
        df.loc[subject]['qc_anat_snrd'] = mriqca.snr_dietrich(anat_fg_mu, anat_bg_sd)
        df.loc[subject]['qc_anat_efc']  = mriqca.efc(anat)
        df.loc[subject]['qc_anat_fber'] = mriqca.fber(anat, anat_mask)
        df.loc[subject]['qc_anat_fwhm'] = fwhm(os.path.join(subdir, 'RAW','ANATOMICAL.nii.gz' ),
                                               os.path.join(subdir, 'ANATOMICAL', 'ANATOMICAL_BRAIN_MASK.nii.gz'),out_vox=False)

        ############################################################################################
        # Functional measures


        # Load data
        func      =  os.path.join(subdir, 'FUNCTIONAL', 'REST_EDIT.nii.gz' )
        func_mask =  os.path.join(subdir, 'FUNCTIONAL', 'REST_BRAIN_MASK.nii.gz' )
        movpar    =  os.path.join(subdir, 'FUNCTIONAL', 'moco/REST_EDIT_moco2.par')

        # Calculate spatial functional summary measures
        func_fg_mu, func_fg_sd, func_fg_size = summary_mask(nb.load(func).get_data(),nb.load(func_mask).get_data())
        df.loc[subject]['qc_func_snr']  = mriqca.snr(func_fg_mu, func_fg_sd, func_fg_size)
        df.loc[subject]['qc_func_efc']  = mriqca.efc(func)
        df.loc[subject]['qc_func_fber'] = mriqca.fber(func, func_mask)
        df.loc[subject]['qc_func_fwhm'] = fwhm(func, func_mask, out_vox=False)

        # Calculate temporal functional summary measures
        FD1D          = np.loadtxt(calculate_FD_Power(movpar))
        frames_in     = [frame for frame, val in enumerate(FD1D) if val < 0.2]
        quat          = int(len(FD1D) / 4)
        fd_in_percent = (float(len(frames_in)) / float(len(FD1D))) * 100.

        df.loc[subject]['qc_func_fd']     = str(np.round(np.mean(FD1D), 3))
        df.loc[subject]['qc_func_fd_in']  = str(np.round(fd_in_percent, 2))
        df.loc[subject]['qc_func_fd']     = str(np.round(np.mean(FD1D), 3))
        df.loc[subject]['qc_func_fd_max'] = str(np.round(np.max(FD1D), 3))
        df.loc[subject]['FD_Q4'] = str(np.round(np.mean(np.sort(FD1D)[::-1][:quat]), 3))
        df.loc[subject]['FD_RMS'] = str(np.round(np.sqrt(np.mean(FD1D)), 3))

        # Calculate DVARS
        func_proc = os.path.join(subdir, 'REGISTRATION', 'REST_EDIT_UNI_BRAIN_MNI2mm.nii.gz')
        func_mask = os.path.join(subdir, 'REGISTRATION', 'ANATOMICAL_GM_MNI2mm.nii.gz')
        df.loc[subject]['qc_func_dvars']    = calculate_DVARS(func_proc, func_gm)

        # Calculate TSNR map
        if not os.path.isfile(os.path.join(qcdir, 'tsnr.nii.gz')):
             tsnr = TSNR()
             tsnr.inputs.in_file = func_edit
             tsnr.run()

        if not os.path.isfile('TSNR_data.npy'):
             tsnr_data = nb.load('./tsnr.nii.gz').get_data()
             nan_mask = np.logical_not(np.isnan(tsnr_data))
             mask = nb.load(func_mask).get_data() > 0
             data = tsnr_data[np.logical_and(nan_mask, mask)]
             np.save(os.path.join(os.getcwd(), 'TSNR_data.npy'), data)

        df.loc[subject]['TSNR'] = str(np.round(np.median(np.load('TSNR_data.npy')), 3))
        df.to_csv('quality_paramters.csv')


make_quality_control(['PA060'], tourettome_workspace)