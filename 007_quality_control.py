__author__ = 'kanaan 23.03.2017'

import os

import nibabel as nb
import numpy as np
import pandas as pd
from nipype.algorithms.misc import TSNR
from quality.motion_statistics import *
from quality.spatial_qc import *
from utilities.utils import *
from variables.subject_list import *


def quality_control(population, workspace):

    for subject in population:
        print '###############################################################################'
        print 'Calculating quality metrics for  %s' % subject
        print ''

        #input
        subdir       = os.path.join(workspace, subject)

        #output
        qcdir = mkdir_path(os.path.join(subdir, 'QUALITY'))
        os.chdir(qcdir)

        ################################################################################################################
        #### Spatial Quality metrics - MP2RAGE

        # Load data
        anat       = nb.load(os.path.join(subdir, 'RAW',        'ANATOMICAL.nii.gz' )).get_data()
        anat_mask  = nb.load(os.path.join(subdir, 'ANATOMICAL', 'ANATOMICAL_BRAIN_MASK.nii.gz' )).get_data()
        anat_gm    = nb.load(os.path.join(subdir, 'ANATOMICAL', 'seg_spm/c1ANATOMICAL.nii' )).get_data()
        anat_wm    = nb.load(os.path.join(subdir, 'ANATOMICAL', 'seg_spm/c2ANATOMICAL.nii' )).get_data()
        anat_csf   = nb.load(os.path.join(subdir, 'ANATOMICAL', 'seg_spm/c3ANATOMICAL.nii' )).get_data()
        anat_first = nb.load(os.path.join(subdir, 'ANATOMICAL', 'seg_first/FIRST.nii.gz' )).get_data()

        # Intermediate measures
        anat_fg_mu, anat_fg_sd, anat_fg_size    = summary_mask(anat, anat_mask)
        anat_gm_mu, anat_gm_sd, anat_gm_size    = summary_mask(anat, np.where(anat_gm > 0.5, 1, 0 ))
        anat_wm_mu, anat_wm_sd, anat_wm_size    = summary_mask(anat, np.where(anat_wm > 0.5, 1, 0 ))
        anat_csf_mu, anat_gm_sd, anat_csf_size  = summary_mask(anat, np.where(anat_csf > 0.5, 1, 0 ))
        anat_bg_data, anat_bg_mask              = get_background(anat, anat_mask)
        anat_bg_mu, anat_bg_sd, anat_bg_size    = summary_mask(anat, anat_bg_mask)

        # Calcualte spatial anatomical summary measures
        anat_CNR  = cnr(anat_gm_mu, anat_wm_mu, anat_bg_sd)
        anat_SNR  = snr(anat_fg_mu, anat_bg_sd)
        anat_EFC  = efc(anat)
        anat_FBER = fber(anat, anat_mask, anat_bg_mask)
        anat_QI1  = artifacts(anat, anat_mask, anat_bg_data)
        anat_FWHM = fwhm(os.path.join(subdir, 'RAW','ANATOMICAL.nii.gz' ),
                         os.path.join(subdir, 'ANATOMICAL', 'ANATOMICAL_BRAIN_MASK.nii.gz'),
                         out_vox=False)


        ###############################################################################################################
        # Temporal Quality metrics - REST




        # Calculate Framewise-Displacment
        movpar = os.path.join(subdir, 'FUNCTIONAL', 'moco/REST_EDIT_moco2.par')
        FD1D = np.loadtxt(calculate_FD_Power(movpar))
        frames_in = [frame for frame, val in enumerate(FD1D) if val < 0.2]

        # Calculate DVARS
        func_proc = os.path.join(subdir, 'REGISTRATION', 'REST_EDIT_UNI_BRAIN_MNI2mm.nii.gz')
        func_mask = os.path.join(subdir, 'REGISTRATION', 'ANATOMICAL_GM_MNI2mm.nii.gz')
        DVARS = calculate_DVARS(func_proc, func_gm)


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
             np.save(os.path.join(os.getcwd(), 'TSNR_data.npy'), data)  #######################################

        # Calculate DVARS
        # DVARS = calculate_DVARS(func_wmcsf, func_gm)

        ################################################################################################################
        ## Save quality paramters

        columns = [ 'SNR', 'CNR', 'FBER', 'EFC', 'FWHM', 'QI1', 'FD', 'FD_in', 'FD_max', 'FD_Q4', 'DVARS', 'TSNR']

        df = pd.DataFrame(index=['%s'%subject], columns = columns)
        df.loc[subject]['SNR']  = anat_SNR
        df.loc[subject]['CNR']  = anat_CNR
        df.loc[subject]['EFC']  = anat_EFC
        df.loc[subject]['FBER'] = anat_FBER
        df.loc[subject]['QI1']  = anat_QI1
        df.loc[subject]['FWHM'] = anat_FWHM[3]
        df.loc[subject]['FD'] = str(np.round(np.mean(FD1D), 3))
        fd_in_percent = (float(len(frames_in)) / float(len(FD1D))) * 100.
        df.loc[subject]['FD_in']  = str(np.round(fd_in_percent, 2))
        quat = int(len(FD1D) / 4)
        df.loc[subject]['FD_Q4'] = str(np.round(np.mean(np.sort(FD1D)[::-1][:quat]), 3))
        df.loc[subject]['FD_max'] = str(np.round(np.max(FD1D), 3))
        df.loc[subject]['FD_RMS'] = str(np.round(np.sqrt(np.mean(FD1D)), 3))
        #df.loc[subject]['DVARS'] = str(np.round(np.mean(np.load(DVARS)), 3))
        df.loc[subject]['TSNR'] = str(np.round(np.median(np.load('TSNR_data.npy')), 3))
        df.to_csv('quality_paramters.csv')

        print df

        ################################################################################################################
        ## plot image quality

quality_control(['PA040'], tourettome_workspace)








#
# import os
# from variables.subject_list import *
# from utilities.utils import *
# from plots.plot_volumes_qc import *
#
#
# def make_quality_reports(population, workspace):
#
#     for subject in population:
#
#         print '###############################################################################'
#         print 'Creating Quality Control Report for subject %s' % subject
#         print ''
#
#         subdir = os.path.join(workspace, subject)
#         qcdir  = mkdir_path(os.path.join(subdir, 'QUALITY'))
#         os.chdir(qcdir)
#
#         anat      = os.path.join(subdir, 'ANATOMICAL',   'ANATOMICAL_BRAIN.nii.gz' )
#         gm        = os.path.join(subdir, 'ANATOMICAL',   'ANATOMICAL_GM.nii.gz')
#         gm2mni    = os.path.join(subdir, 'REGISTRATION', 'ANATOMICAL_GM_MNI1mm.nii.gz')
#         func2anat = os.path.join(subdir, 'REGISTRATION', 'REST_EDIT_MOCO_BRAIN_MEAN_BBR_ANAT1mm.nii.gz')
#
#         # Plot native anatomical with GM
#         if not os.path.isfile(os.path.join(qcdir, 'plot_anat_native.png')):
#             plot_vol_quality(anat, gm, subject[0:2], '%s - Native Anatomical' %subject, 'plot_anat_native.png', cmap = 'r')
#
#         # Plot anat2mni reg quality using GM as a boundary
#         #plot_vol_quality(mni_brain_1mm, gm2mni, 'MNI', '%s - Anatomical to MNI xfm' %subject, 'plot_anat_mni.png', cmap = 'r' )
#
#         # Plot func2anat reg quality using GM as a boundary
#         #plot_vol_quality(func2anat, gm, subject[0:2], '%s - Func to Anat xfm' %subject, 'plot_func2anat-png', cmap = 'r' )
#
#
#
# make_quality_reports(tourettome_subjects, tourettome_workspace)
#
# ###########
# # Functional
# # 1- Raw Mean
# # 2- TSNR
# # 3- FD
# # 4- DVARS
# # 5- denoised imshow
#
# # GM/WM/CSF
# # PLOT FUNCTIONAL MEAN ax-cor-sagg at level of BG
#
#
#
# # make qap pipe