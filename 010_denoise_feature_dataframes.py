__author__ = 'kanaan 10.01.2018'


import os
import numpy as np
import pandas as pd
import nibabel as nb
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('white')

from variables.subject_list import *
from utilities.utils import mkdir_path, return_sca_data, return_ct_data, regress_covariates
from plotting.plot_mats import plot_heatmap
from plotting.cmaps import cmap_gradient

control_outliers = ['HM015', 'LZ061', 'HB028',
                    'LZ052' # no data
                    ]
patient_outliers = ['HA009', 'HB005', 'HM015', 'HM023', 'HM026', 'LZ004', 'LZ006', 'LZ007', 'LZ013', 'LZ017',
                    'LZ018', 'LZ020', 'LZ022', 'LZ025', 'LZ027', 'LZ028', 'LZ029', 'LZ031', 'LZ035', 'LZ038',
                    'PA009', 'PA012', 'PA025', 'PA045', 'PA052', 'PA055', 'PA058', 'PA077', 'PA080', 'PA094',
                    'LZ001',
                    ]

hamburg = ['HM001', 'HM002', 'HM003', 'HM004', 'HM005', 'HM006', 'HM007', 'HM008', 'HM009', 'HM010',
           'HM011', 'HM012', 'HM014', 'HM015', 'HM017', 'HM019', 'HM020', 'HM022', 'HM023', 'HM024',
           'HM025', 'HM026', 'HM027', 'HM028', 'HM029', 'HM030', 'HM031', 'HM032', 'HM033']

seeds = ['STR3_MOTOR', 'STR3_LIMBIC', 'STR3_EXEC', 'PALL', 'THAL'
         ]
terms = ['Age', 'Sex', 'Site', 'qc_func_fd', 'qc_anat_cjv']


def construct_features_dataframe(control_outliers, patient_outliers, workspace_dir, derivatives_dir, freesufer_dir):

    print '========================================================================================'
    print ''
    print '                    Tourettome - 009. Create Feature Dataframes                         '
    print ''
    print '========================================================================================'
    print ''

    #I/O
    features_dir = mkdir_path(os.path.join(derivatives_dir, 'feature_matrices'))

    print '#####################################################'
    print ' Inspecting sample size'

    df_pheno = pd.read_csv(os.path.join(tourettome_phenotypic, 'tourettome_phenotypic.csv'), index_col=0)
    population = df_pheno.index
    # Extract groups
    patients = sorted([i for i in population if df_pheno.loc[i]['Group'] == 'patients' if
                       i not in patient_outliers and i not in hamburg])
    controls = sorted([i for i in population if df_pheno.loc[i]['Group'] == 'controls' or
                       df_pheno.loc[i]['Group'] == 'probands' if i not in control_outliers and i not in hamburg])

    # create group phenotypic dataframes
    df_pheno_controls = df_pheno.drop([i for i in df_pheno.index if i not in controls], axis=0)
    df_pheno_controls = df_pheno_controls.drop([i for i in df_pheno_controls.columns if i not in terms], axis=1)

    df_pheno_patients = df_pheno.drop([i for i in df_pheno.index if i not in patients], axis=0)
    df_pheno_patients = df_pheno_patients.drop([i for i in df_pheno_patients.columns if i not in terms], axis=1)

    # Included subjects
    print 'n_controls=', len(controls)
    print 'n_patients=', len(patients)
    print 'n_total =', len(controls) + len(patients)
    print ''

    # Outliers
    print 'n_control_outliers=', len(control_outliers)
    print 'n_patients_outliers=', len(patient_outliers)
    print 'n_total_outliers =', len(control_outliers) + len(patient_outliers)
    print ''

    print '################################################################################################'
    print ' Denoising  SCA features'

    print '... Extracting data'
    if not os.path.isfile(os.path.join(features_dir, 'sca_patients_raw.csv')):
        sca_controls_raw = []
        sca_patients_raw = []

        for seed_name in seeds:
            print '......  checking control data for ', seed_name
            sca_controls_raw.append(return_sca_data(seed_name, controls, derivatives_dir))
            print '......  checking patient data for ', seed_name
            sca_patients_raw.append(return_sca_data(seed_name, patients, derivatives_dir))

        print '...... raw dataframes contain these seeds -->', seeds
        sca_controls_raw = pd.concat(sca_controls_raw)
        sca_patients_raw = pd.concat(sca_patients_raw)
        sca_all_raw = pd.concat([sca_controls_raw, sca_patients_raw])

        # Save raw dataframes
        sca_controls_raw.to_csv(os.path.join(features_dir, 'sca_controls_raw.csv'))
        sca_patients_raw.to_csv(os.path.join(features_dir, 'sca_patients_raw.csv'))
        sca_tourettome_raw.to_csv(os.path.join(features_dir, 'sca_tourettome_raw.csv'))

        plot_heatmap(sca_controls_raw, '%s/sca_controls_raw'%features_dir, cmap =cmap_gradient)
        plot_heatmap(sca_patients_raw, '%s/sca_patients_raw'%features_dir, cmap =cmap_gradient)
        plot_heatmap(sca_tourettome_raw, '%s/sca_tourettome_raw'%features_dir, cmap =cmap_gradient)
    else:
        sca_tourettome_raw = pd.read_csv(os.path.join(features_dir, 'sca_tourettome_raw.csv'), index_col=0)

#     ############################################################################################################
#     print '... Regression nuisance variables'
#
# #####################
# #####################
# #####################
# ####TO DO ---- regress as a concatenated dataframe
#     if not os.path.isfile(os.path.join(features_dir, 'sca_patients_resid.csv')):
#         sca_controls_resid = regress_covariates(sca_controls_raw, df_pheno, controls, 'controls', features_dir, cmap_gradient)
#         sca_patients_resid = regress_covariates(sca_patients_raw, df_pheno, patients, 'patients', features_dir, cmap_gradient)
#     else:
#         sca_controls_resid = pd.read_csv(os.path.join(features_dir, 'sca_controls_resid.csv'), index_col=0).T
#         sca_patients_resid = pd.read_csv(os.path.join(features_dir, 'sca_patients_resid.csv'), index_col=0).T
#
#     print sca_controls_resid.shape
#     print sca_patients_resid.shape

#     ############################################################################################################
#     print ' ... z-scoring dataframes to control distribution'
#     # "At each surface point, we normalized feature data in each individual with ASD against the
#     # corresponding distribution in control using vertex-wise zscoring (Bernhardt, AnnNeurology, 2015)"
#
#     if not os.path.isfile(os.path.join(features_dir, 'sca_patients_resid_z.csv')):
#
#         # Calculate control mu/sd across each vertex and z-score patients
#         n_vertices = sca_controls_resid.shape[1]
#         vertex_mu = [np.mean(sca_controls_resid.T.loc[vertex]) for vertex in range(n_vertices)]
#         vertex_sd = [np.std(sca_controls_resid.T.loc[vertex]) for vertex in range(n_vertices)]
#         sca_patients_resid_z = pd.concat([(sca_patients_resid.T.loc[vertex] - vertex_mu[vertex]) /
#                                  vertex_sd[vertex] for vertex in range(n_vertices)],axis=1).T
#
# ########
# ########
# ########## Z-score control dataframe in a loop.
#         # for each subject, remove this subject, calculate. vertex mu_sd and zscore.
#         sca_controls_resid_z = pd.concat([(sca_controls_resid.T.loc[vertex] - vertex_mu[vertex]) /
#                                  vertex_sd[vertex] for vertex in range(n_vertices)],axis=1).T
#
#         # Save data frames
#         sca_controls_resid_z.to_csv('%s/sca_controls_resid_z.csv'%features_dir)
#         sca_patients_resid_z.to_csv('%s/sca_patients_resid_z.csv'%features_dir)
#         plot_heatmap(sca_controls_resid_z, '%s/sca_controls_resid_z' % features_dir, vmin =-3, vmax=3, cmap = cmap_gradient)
#         plot_heatmap(sca_patients_resid_z, '%s/sca_patients_resid_z' % features_dir, vmin =-3, vmax=3, cmap = cmap_gradient)
#
#


    # print '#####################################################'
    # print ' 2. Denoising cortical-thickness features'

    # ct_controls = return_ct_data(controls, derivatives_dir)
    # ct_patients = return_ct_data(patients, derivatives_dir)



construct_features_dataframe(control_outliers, patient_outliers, tourettome_workspace,
                             tourettome_derivatives, tourettome_freesurfer )


