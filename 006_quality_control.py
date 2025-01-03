__author__ = 'kanaan 06.01.2018'

import os
import nibabel as nb
import numpy as np
import pandas as pd
from nipype.algorithms.confounds import TSNR
from quality.motion_statistics import *
from quality.spatial_qc import *
from utilities.utils import *
from plotting.plot_volumes import *
from variables.subject_list import *
import mriqc.qc.anatomical as mriqca

import matplotlib;matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('white')
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm, inch, pica

# IMAGE QUALITY METRICS

# anatomical measures based on noise measurements
#### CJV  - coefficient of joint variation
#### CNR  - contrast-to-noise ratio
#### SNR  - signal-to-noise ratio
#### SNRd - Dietrichs SNR
#### QI2  - Mortamets quality index 2

# anatomical measures based on information theory
#### EFC  - Shannons entropy focus criterion
#### FBER - foreground-to-background ratio

# anatomical measures targeting specific artifacts
#### QI1  -  Mortamets quality index 1

# anatomical other measures
#### fwhm -  spatial distribution of the image intensity


def make_subject_qc(population, workspace):
    print '========================================================================================'
    print ''
    print '                    Tourettome - 006. QUALITY CONTROL                                   '
    print ''
    print '========================================================================================'

    count = 0
    for subject in population:

        count +=1

        print '%s.Running Quality Control for subject %s' %(count, subject)

        site_id = subject[0:2]
        subdir  = os.path.join(workspace, subject)
        qcdir   = mkdir_path(os.path.join(workspace, subject, 'QUALITY_CONTROL'))
        os.chdir(qcdir)

        df = pd.DataFrame(index=['%s' % subject])

        # EXTRACT ANATOMICAL AND FUNCTIONAL IMAGE QUALITY METRICS

        if not os.path.isfile(os.path.join(qcdir, 'quality_paramters.csv')):

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
            df.loc[subject, 'qc_anat_cjv']  = mriqca.cjv(anat_wm_mu, anat_gm_mu, anat_wm_sd, anat_gm_sd)
            df.loc[subject, 'qc_anat_cnr']  = mriqca.cnr(anat_wm_mu, anat_gm_mu, anat_bg_sd)
            df.loc[subject, 'qc_anat_snr']  = mriqca.snr(anat_fg_mu, anat_fg_sd, anat_fg_size)
            df.loc[subject, 'qc_anat_snrd'] = mriqca.snr_dietrich(anat_fg_mu, anat_bg_sd)
            df.loc[subject, 'qc_anat_efc']  = mriqca.efc(anat)
            df.loc[subject, 'qc_anat_fber'] = mriqca.fber(anat, anat_mask)
            # df.loc[subject]['qc_anat_fwhm'] = fwhm(os.path.join(subdir, 'RAW','ANATOMICAL.nii.gz' ),
            #                                        os.path.join(subdir, 'ANATOMICAL', 'ANATOMICAL_BRAIN_MASK.nii.gz'),out_vox=False)

            ############################################################################################
            # Functional measures

            # Load data
            func      =  np.mean(nb.load(os.path.join(subdir, 'FUNCTIONAL', 'REST_EDIT.nii.gz' )).get_data(), axis =3)
            func_mask =  nb.load(os.path.join(subdir, 'FUNCTIONAL', 'REST_BRAIN_MASK.nii.gz' )).get_data()
            movpar    =  os.path.join(subdir, 'FUNCTIONAL', 'moco/REST_EDIT_moco2.par')

            # Calculate spatial functional summary measures
            func_fg_mu, func_fg_sd, func_fg_size = summary_mask(func, func_mask)
            df.loc[subject, 'qc_func_snr']  = mriqca.snr(func_fg_mu, func_fg_sd, func_fg_size)
            df.loc[subject, 'qc_func_efc']  = mriqca.efc(func)
            df.loc[subject, 'qc_func_fber'] = mriqca.fber(func, func_mask)
            # df.loc[subject]['qc_func_fwhm'] = fwhm(func, func_mask, out_vox=False)

            # Calculate temporal functional summary measures
            FD1D          = np.loadtxt(calculate_FD_Power(movpar))
            frames_in     = [frame for frame, val in enumerate(FD1D) if val < 0.2]
            quat          = int(len(FD1D) / 4)
            fd_in_percent = (float(len(frames_in)) / float(len(FD1D))) * 100.

            df.loc[subject, 'qc_func_fd']     = str(np.round(np.mean(FD1D), 3))
            df.loc[subject, 'qc_func_fd_in']  = str(np.round(fd_in_percent, 2))
            df.loc[subject, 'qc_func_fd']     = str(np.round(np.mean(FD1D), 3))
            df.loc[subject, 'qc_func_fd_max'] = str(np.round(np.max(FD1D), 3))
            df.loc[subject, 'qc_func_fd_q4 '] = str(np.round(np.mean(np.sort(FD1D)[::-1][:quat]), 3))
            df.loc[subject, 'qc_func_fd_rms'] = str(np.round(np.sqrt(np.mean(FD1D)), 3))

            # Calculate DVARS
            func_proc = os.path.join(subdir, 'REGISTRATION', 'REST_EDIT_UNI_BRAIN_MNI2mm.nii.gz')
            func_gm = os.path.join(subdir, 'REGISTRATION', 'ANATOMICAL_GM_MNI2mm.nii.gz')
            df.loc[subject, 'qc_func_dvars']    = np.mean(np.load(calculate_DVARS(func_proc, func_gm)))

            # Calculate TSNR map
            if not os.path.isfile(os.path.join(qcdir, 'tsnr.nii.gz')):
                 tsnr = TSNR()
                 tsnr.inputs.in_file = os.path.join(subdir, 'FUNCTIONAL', 'REST_EDIT.nii.gz')
                 tsnr.run()
                 # os.system('flirt -in tsnr -ref ../ANATOMICAL/ANATOMICAL -applxfm -init ../REGISTRATION/reg_anat/rest2anat_2.mat -out tsnr2anat')

            if not os.path.isfile('TSNR_data.npy'):
                 tsnr_data = nb.load('./tsnr.nii.gz').get_data()
                 nan_mask = np.logical_not(np.isnan(tsnr_data))
                 mask = func_mask > 0
                 data = tsnr_data[np.logical_and(nan_mask, mask)]
                 np.save(os.path.join(os.getcwd(), 'TSNR_data.npy'), data)


            df.loc[subject, 'qc_func_tsnr'] = str(np.round(np.median(np.load('TSNR_data.npy')), 3))

            df.to_csv('quality_paramters.csv')

        ############################################################################################
        #  Make Image Quality Plots

        if not os.path.isfile(os.path.join(qcdir, 'plot_func_tsnr.png')):

            # 1. anat brain mask
            plot_quality(os.path.join(subdir, 'RAW', 'ANATOMICAL.nii.gz'),
                         os.path.join(subdir, 'ANATOMICAL', 'ANATOMICAL_BRAIN_MASK.nii.gz'),
                         subject[0:2], '%s-anat_brain_mask' % subject, 'r', alpha=0.9, title='plot_anat_brain_mask.png')

            # 2. anat gm seg
            plot_quality(os.path.join(subdir, 'RAW', 'ANATOMICAL.nii.gz'),
                         os.path.join(subdir, 'ANATOMICAL', 'ANATOMICAL_GM.nii.gz'),
                         subject[0:2], '%s-anat_gm_seg' % subject, 'r', alpha=0.9, title='plot_anat_gm_seg.png')

            # 3. anat2mni
            plot_quality(mni_head_1mm, os.path.join(subdir, 'REGISTRATION', 'ANATOMICAL_GM_MNI1mm.nii.gz'),
                         'MNI', '%s-anat_gm_seg' % subject, 'r', alpha=0.9, title='plot_anat2mni.png',
                         tissue2=os.path.join(subdir, 'REGISTRATION', 'ANATOMICAL_CSF_MNI1mm.nii.gz'))

            # 4. func2mni
            plot_quality(os.path.join(subdir, 'REGISTRATION', 'REST_EDIT_MOCO_BRAIN_MEAN_BBR_ANAT1mm.nii.gz'),
                         os.path.join(subdir, 'ANATOMICAL', 'ANATOMICAL_GM.nii.gz'),
                         subject[0:2], '%s-func2mni' % subject, 'r', alpha=0.9, title='plot_func2anat.png')

            # 5. func_tsnr
            plot_quality(os.path.join(subdir, 'QUALITY_CONTROL', 'tsnr.nii.gz'), None,
                         'TSNR', '%s-func_tsnr' % subject, 'r', alpha=0.9, title='plot_func_tsnr.png')

        # 6. plot FD, DVARS, CARPET

        resid = nb.load(os.path.join(subdir, 'DENOISE/residuals_compcor/residual_bp_z.nii.gz')).get_data().astype(np.float32)
        gm = resid[nb.load(os.path.join(subdir, 'DENOISE/tissue_signals/gm_mask.nii.gz')).get_data().astype('bool')]
        wm = resid[nb.load(os.path.join(subdir, 'DENOISE/tissue_signals/wm_mask.nii.gz')).get_data().astype('bool')]
        cm = resid[nb.load(os.path.join(subdir, 'DENOISE/tissue_signals/csf_mask.nii.gz')).get_data().astype('bool')]
        fd = np.loadtxt(os.path.join(subdir, 'QUALITY_CONTROL/FD.1D'))
        dv = np.load(os.path.join(subdir, 'QUALITY_CONTROL/DVARS.npy'))

        if not os.path.isfile(os.path.join(qcdir,'xplot_func_motion.png')):
            plot_temporal(gm, wm, cm, fd, dv, os.path.join(qcdir,'plot_func_motion.png'))

def make_group_qc(population, workspace, phenotypic_dir):

    print 'Creating Group QC dataframe'

    def get_dcm_header(site_id):
        df = pd.read_csv(os.path.join(phenotypic_dir, 'phenotypic_%s.csv' % site_id), index_col=0)
        #df = df[['Group', 'Site', 'Age', 'Sex']]
        return df

    df_dcm = pd.concat([get_dcm_header('hannover_a'),
                        get_dcm_header('hannover_b'),
                        get_dcm_header('leipzig'),
                        get_dcm_header('hamburg'),
                        get_dcm_header('paris')]
                       )

    df_qc = pd.concat([pd.read_csv(os.path.join(workspace,s ,'QUALITY_CONTROL/quality_paramters.csv'),index_col=0)
                       for s in population if os.path.isfile(os.path.join(workspace,s ,'QUALITY_CONTROL/quality_paramters.csv'))])
    df = pd.concat([df_dcm, df_qc], axis=1)
    df.to_csv(os.path.join(phenotypic_dir, 'phenotypic_tourettome.csv'))



    df_fd   = pd.DataFrame(df['qc_func_fd']).dropna()
    df_tsnr = pd.DataFrame(df['qc_func_tsnr']).dropna()

    # count = 0
    # for subject in df_fd.index:
    #     count +=1
    #     print '%s. Plotting FD/TSNR distribution for subject %s' %(count, subject)
    #
    #     qc_dir = os.path.join(workspace, subject, 'QUALITY_CONTROL')
    #     os.chdir(qc_dir)
    #
    #     fig = plt.figure()
    #     fig.set_size_inches(20, 2)
    #     sns.distplot(df_fd['qc_func_fd'], rug=True, hist=True, kde=True, color='b')
    #     plt.axvline(df_fd.loc[subject]['qc_func_fd'], color='r', linestyle='dashed', linewidth=3.5)
    #     plt.ylabel('Density', size=20, weight='bold')
    #     plt.xlabel('Framewise-Dispalcement (mm)', size=20, weight='bold')
    #     plt.yticks(fontsize=15, weight='bold')
    #     plt.xticks(fontsize=15, weight='bold')
    #     plt.savefig('plot_distribution_fd.png', bbox_inches='tight')
    #     plt.close()
    #
    #     fig = plt.figure()
    #     fig.set_size_inches(20, 2)
    #     sns.distplot(df_tsnr['qc_func_tsnr'], rug=True, hist=True, color='g')
    #     plt.axvline(df_tsnr.loc[subject]['qc_func_tsnr'], color='r', linestyle='dashed', linewidth=3.5)
    #     plt.ylabel('Density', size=20, weight='bold')
    #     plt.xlabel('TSNR', size=20, weight='bold')
    #     plt.yticks(fontsize=15, weight='bold')
    #     plt.xticks(fontsize=15, weight='bold')
    #     plt.savefig('plot_distribution_tsnr.png', bbox_inches='tight')
    #     plt.close()

    for subject in population:
        print '.......Creating QC_REPORT for subject:',subject
        qc_dir = os.path.join(workspace, subject,'QUALITY_CONTROL')
        os.chdir(qc_dir)
        report = canvas.Canvas('_report.pdf', pagesize=(8.27 * 500, 11.69 * 500))
        report.drawImage(os.path.join(qc_dir, 'plot_anat_gm_seg.png'), 150, 4550)
        report.drawImage(os.path.join(qc_dir, 'plot_anat2mni.png'), 150, 3600)
        report.drawImage(os.path.join(qc_dir, 'plot_func2anat.png'), 150, 2600)
        report.drawImage(os.path.join(qc_dir, 'plot_func_tsnr.png'), 150, 1900)
        report.drawImage(os.path.join(qc_dir, 'plot_func_motion.png'), 0, 100, width=1977 * 2.05, height=886 * 2)
        report.setFont("Helvetica", 180)
        report.drawString(1900, 5650, '%s' % subject)
        report.save()

        os.system('convert -density 50x50 -quality 50 -compress jpeg _report.pdf report.pdf')
        os.system('rm -rf _report.pdf')

make_subject_qc(tourettome_subjects, tourettome_workspace)
make_group_qc(tourettome_subjects, tourettome_workspace, tourettome_phenotypic)