__author__ = 'kanaan 10.01.2018... re-written 18.10.2018'

import os, sys
import numpy as np
import pandas as pd
import nibabel as nb
import matplotlib
import subprocess
import seaborn as sns
from sklearn import preprocessing
matplotlib.use('agg')
import matplotlib.pyplot as plt
sns.set_style('white')

from variables.subject_list import *
from utilities.utils import mkdir_path
from utilities.check_data import return_ct_data, return_sca_data, return_ecm_data
sys.path.append('/Users/kanaan/SCR/Github/Tourettome/plotting/')
from plotting.cmaps import cmap_gradient

control_outliers = ['HM015', 'LZ061', 'LZ052', 'LZ057', 'LZ058',
                    'HB019',
                    'HM001', 'HM004', 'HM006', 'HM012', 'HM014', 'HM017', 'HM019', 'HM022', 'HM025', 'HM027',
                    'HM028', 'HM029', 'HM030', 'HM032'
                    ]

patient_outliers = ['HA009', 'HB005', 'HM015', 'HM023', 'HM026', 'LZ004', 'LZ006', 'LZ007', 'LZ013', 'LZ017',
                    'LZ018', 'LZ020', 'LZ025', 'LZ027', 'LZ028', 'LZ029', 'LZ030', 'LZ031', 'LZ035', 'LZ038',
                    'PA001', 'PA006', 'PA009', 'PA012', 'PA013', 'PA019', 'PA025', 'PA039', 'PA045', 'PA052',
                    'PA055', 'PA058', 'PA077', 'PA078', 'PA080', 'PA081', 'PA094', 'LZ001',
                    'PA055', 'HB014', 'HB015',
                    'HM002', 'HM003', 'HM005', 'HM007', 'HM008', 'HM009', 'HM010', 'HM011', 'HM020', 'HM024',
                    'HM031', 'HM033'
                    ]

terms = ['Age', 'Sex', 'Group', 'Site', 'qc_func_fd']


def z_score_features(df_controls, df_patients):

    ################################
    # Z-score controls
    print '...... Control feature  shape=', df_controls.shape
    print '...... Z-scoring Controls'
    # For each subject z-score based on the distrubution of all other subjects
    df_controls_mu = []
    df_controls_sd = []

    for subject in df_controls.columns:
        df_controls_mu.append(pd.DataFrame(df_controls.drop([subject], axis=1).mean(axis=1), columns=[subject]))
        df_controls_sd.append(pd.DataFrame(df_controls.drop([subject], axis=1).std(axis=1), columns=[subject]))

    df_controls_mu = pd.concat(df_controls_mu, axis=1)
    df_controls_sd = pd.concat(df_controls_sd, axis=1)
    df_controls_z = (df_controls.copy(deep=True) - df_controls_mu) / df_controls_sd

    ################################
    # Z-score patients
    print '...... Patient feature  shape=',df_patients.shape
    print '...... Z-scoring Patients'    # "At each surface point, we normalized feature data in each individual with ASD against the
    # corresponding distribution in control using vertex-wise zscoring (Bernhardt, AnnNeurology, 2015)"
    n_patients = len(df_patients.columns)
    df_controls_vert_mu = pd.DataFrame(pd.np.tile(df_controls.mean(axis=1), (n_patients, 1)),
                                       index=df_patients.columns).T
    df_controls_vert_sd = pd.DataFrame(pd.np.tile(df_controls.std(axis=1), (n_patients, 1)),
                                       index=df_patients.columns).T
    df_patients_z = (df_patients.copy(deep=1) - df_controls_vert_mu) / df_controls_vert_sd

    return df_controls_z, df_patients_z


def denoise_features(tourettome_dir, feature_name, outliers):

    # SAVE CT pheno dataframe for surfstat
    df_pheno     = pd.read_csv(os.path.join(tourettome_dir,  'phenotypic', 'tourettome_phenotypic.csv'),index_col=0)
    df_pheno= df_pheno.drop(outliers)

    df_pheno_qc = df_pheno.drop([i for i in df_pheno.columns if i not in terms],axis = 1)
    df_pheno_qc.index.names = ['subject']
    df_pheno_qc.to_csv(os.path.join(tourettome_dir,'phenotypic/tourettome_phenotypic_qc.csv'))

    patients = [i for i in df_pheno_qc.index if df_pheno_qc.loc[i]['Group'] == 'patients']
    controls = [i for i in df_pheno_qc.index if df_pheno_qc.loc[i]['Group'] == 'controls']

    # Regress covariates
    #[features, residuals]=regress_covariates_sca(tourettome_dir, feature_name, freesurfer_dir, phenotypic)
    os.chdir('/scr/malta1/Github/Tourettome/surfstats')
    regress = ['matlab', '-nodesktop', '-nosplash', '-noFigureWindows',
               '-r "regress_covariates_sca(\'%s\', \'%s\', \'%s\') ; quit;"'
               %(tourettome_dir, feature_name, df_pheno_qc )]
    subprocess.call(regress)

    # ####################################################################################################################
    # # Zscore
    # features_dir = os.path.join(tourettome_derivatives, 'feature_matrices')
    # df_sca_resid  = pd.read_csv(os.path.join(features_dir, 'tourettome_sca_resid.csv'), header= None)
    #
    # sca_resid_patients = df_resid.drop(controls, )
    
    #     #####################
    #     # Break down sca_tourettome_resid to patient and control dataframes
    #     if not os.path.isfile(os.path.join(features_dir, 'sca_patients_resid.csv')):
    #         sca_tourettome_resid = pd.read_csv(os.path.join(features_dir, 'sca_tourettome_resid.csv'), index_col =0)
    #         sca_patients_resid = sca_tourettome_resid.drop(controls, axis=1)
    #         sca_controls_resid = sca_tourettome_resid.drop(patients, axis=1)
    #
    #         # save separately
    #         sca_patients_resid.to_csv(os.path.join(features_dir, 'sca_patients_resid.csv'))
    #         sca_controls_resid.to_csv(os.path.join(features_dir, 'sca_controls_resid.csv'))
    #
    #         # plot separate sca residuals
    #         plt_features_heatmap(sca_controls_resid, os.path.join(features_dir, 'sca_controls_resid.png'),
    #                              vmin=-1, vmax=1, figsize=(17.5, 10))
    #         plt_features_heatmap(sca_patients_resid, os.path.join(features_dir, 'sca_patients_resid.png'),
    #                              vmin=-1, vmax=1, figsize=(17.5, 10))
    #
    #     else:
    #         sca_controls_resid = pd.read_csv(os.path.join(features_dir, 'sca_controls_resid.csv'), index_col=0)
    #         sca_patients_resid = pd.read_csv(os.path.join(features_dir, 'sca_patients_resid.csv'), index_col=0)
    #
    #     #####################
    #     # Z-Score
    #     if not os.path.isfile(os.path.join(features_dir, 'sca_patients_resid_z.csv')):
    #         print ' ... Z-scoring SCA dataframes'
    #         sca_controls_resid_z, sca_patients_resid_z = z_score_features(sca_controls_resid, sca_patients_resid)
    #
    #         # save data
    #         sca_controls_resid_z.to_csv(os.path.join(features_dir, 'sca_controls_resid_z.csv'))
    #         sca_patients_resid_z.to_csv(os.path.join(features_dir, 'sca_patients_resid_z.csv'))
    #         plt_features_heatmap(sca_controls_resid_z, os.path.join(features_dir, 'sca_controls_resid_z.png'),
    #                              vmin=-4, vmax=4, figsize=(17.5, 10))
    #         plt_features_heatmap(sca_patients_resid_z, os.path.join(features_dir, 'sca_patients_resid_z.png'),
    #                              vmin=-4, vmax=4, figsize=(17.5, 10))
    #
    # else:
    #     print 'SCA features already denoised'


denoise_features(tourettome_base, 'func_seed_correlation', patient_outliers+control_outliers)