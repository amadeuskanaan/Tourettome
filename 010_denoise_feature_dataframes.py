__author__ = 'kanaan 10.01.2018'


import os
import numpy as np
import pandas as pd
import nibabel as nb
from patsy import dmatrix
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('white')

from variables.subject_list import *
from utilities.utils import mkdir_path, return_sca_data
from plotting.cmaps import *

control_outliers = ['HM015', 'LZ061', 'HB028']
patient_outliers = ['HA009', 'HB005', 'HM015', 'HM023', 'HM026', 'LZ004', 'LZ006', 'LZ007', 'LZ013', 'LZ017',
                    'LZ018', 'LZ020', 'LZ022', 'LZ025', 'LZ027', 'LZ028', 'LZ029', 'LZ031', 'LZ035', 'LZ038',
                    'PA009', 'PA012', 'PA025', 'PA045', 'PA052', 'PA055', 'PA058', 'PA077', 'PA080', 'PA094',
                   ]

hamburg = ['HM001', 'HM002', 'HM003', 'HM004', 'HM005', 'HM006', 'HM007', 'HM008', 'HM009', 'HM010',
           'HM011', 'HM012', 'HM014', 'HM015', 'HM017', 'HM019', 'HM020', 'HM022', 'HM023', 'HM024',
           'HM025', 'HM026', 'HM027', 'HM028', 'HM029', 'HM030', 'HM031', 'HM032', 'HM033']


seeds = ['STR3_MOTOR', 'STR3_LIMBIC', 'STR3_EXEC']
terms = ['Age', 'Sex', 'Site', 'qc_func_fd', 'qc_anat_cjv']


def plot_heatmap(df, fname, figsize=(12, 10), cmap='jet', vmin=-0.7, vmax=0.7):
    fig = plt.figure(figsize=figsize)
    sns.heatmap(df, xticklabels=False, yticklabels=False, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.savefig('%s.png'%fname, bbox_inches='tight')


def ______________regress_covariates(df_features, df_pheno, population, popname, features_dir, cmap = cmap_gradient):

    # Build design Matrix
    design_matrix = dmatrix(" 0 + Sex + Site + Age + qc_func_fd + qc_anat_cjv", df_pheno, return_type="dataframe")
    design_matrix = design_matrix.drop([i for i in design_matrix.index if i not in population])
    design_matrix.sort_index(axis=1, inplace=True)
    design_matrix.columns = ['age', 'female', 'male', 'hannover_a', 'hannover_b', 'leipzig', 'paris', 'cjv', 'fd']

    # save design matrix
    dmat = design_matrix
    dmat['age'] = dmat['age']/100
    f= plt.figure(figsize=(12, 8))
    sns.heatmap(dmat, yticklabels=False, cmap=cmap, vmin=0, vmax=2)
    plt.xticks(size=20, rotation=90, weight='bold')
    plt.savefig('%s/design_matrix_%s.png'%(features_dir, popname), bbox_inches='tight')
    design_matrix.to_csv('%s/design_matrix_%s.txt'%(features_dir, popname))

    df_features = np.nan_to_num(df_features).T
    print df_features.shape
    df_features_resid = []

    # Fit linear model
    print '..... calculating residuals for %s',popname
    for vertex_id in range(df_features.shape[1]):
        mat = design_matrix
        mat['y'] = df_features[:, vertex_id]
        formula = 'y ~ age + female + male +  hannover_a + hannover_b + leipzig + paris + cjv + fd'
        model = smf.ols(formula=formula, data=pd.DataFrame(mat))
        df_features_resid.append(model.fit().resid)

    # save residual data
    df_features_resid = pd.concat(df_features_resid, axis=1)
    df_features_resid.to_csv('%s/sca_%s_resid.csv'%(features_dir, popname))

    f = plt.figure(figsize=(12, 10))
    sns.heatmap(df_features_resid.T, xticklabels=False, yticklabels=False, cmap=cmap, vmin=-.7, vmax=0.7)
    plt.savefig('%s/design_matrix_%s.png'%(features_dir, popname), bbox_inches='tight')

    return df_features_resid


def regress_covariates(df_features, df_pheno, population, popname, features_dir, cmap=cmap_gradient):
    # Build design Matrix
    design_matrix = dmatrix(" 0 + Sex + Site + Age + qc_func_fd + qc_anat_cjv", df_pheno, return_type="dataframe")
    design_matrix = design_matrix.drop([i for i in design_matrix.index if i not in population])
    design_matrix.sort_index(axis=1, inplace=True)
    design_matrix.columns = ['age', 'female', 'male', 'hannover_a', 'hannover_b', 'leipzig', 'paris', 'cjv', 'fd']

    #sav design matrix data
    dmat = design_matrix
    dmat['age'] = dmat['age']/100
    f= plt.figure(figsize=(12, 8))
    sns.heatmap(dmat, yticklabels=False, cmap=cmap, vmin=0, vmax=2)
    plt.xticks(size=20, rotation=90, weight='bold')
    plt.savefig('%s/design_matrix_%s.png'%(features_dir, popname), bbox_inches='tight')
    design_matrix.to_csv('%s/design_matrix_%s.txt'%(features_dir, popname))

    df_features = np.nan_to_num(df_features).T
    print df_features.shape
    df_features_resid = []

    for vertex_id in range(df_features.shape[1]):
        mat = design_matrix
        mat['y'] = df_features[:, vertex_id]
        print mat
        break
        # formula = 'y ~ age + female + male + hannover_b + leipzig + paris + cjv + fd'
        # model = smf.ols(formula=formula, data=pd.DataFrame(mat))
        # df_features_resid.append(model.fit().resid)

    # # save residual data
    # df_features_resid = pd.concat(df_features_resid, axis=1)
    # df_features_resid.to_csv('%s/sca_%s_resid.csv' % (features_dir, popname))
    # f = plt.figure(figsize=(12, 10))
    # sns.heatmap(pd.concat(x, axis=1).T, xticklabels=False, yticklabels=False, cmap='jet', vmin=-.7, vmax=0.7)
    # plt.savefig('%s/design_matrix_%s.png'%(features_dir, popname), bbox_inches='tight')

    return df_features_resid



def construct_features_dataframe(control_outliers, patient_outliers, workspace_dir, derivatives_dir, freesufer_dir):

    print '========================================================================================'
    print ''
    print '                    Tourettome - 009. Create Feature Dataframes                         '
    print ''
    print '========================================================================================'
    print ''

    #I/O
    features_dir = mkdir_path(os.path.join(derivatives_dir, 'feature_matrices'))

    ################################################################################################
    # Samples after QC

    df_pheno = pd.read_csv(os.path.join(tourettome_phenotypic, 'tourettome_phenotypic.csv'), index_col=0)
    population = df_pheno.index
    # Extract groups
    patients = sorted([i for i in population if df_pheno.loc[i]['Group'] == 'patients' if
                       i not in patient_outliers and i not in hamburg])
    controls = sorted([i for i in population if df_pheno.loc[i]['Group'] in ['controls', 'probands']
                       if i not in control_outliers and i not in hamburg])

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

    ################################################################################################
    print ' 1. Extracting functional features'

    sca_controls_raw = os.path.join(features_dir, 'sca_controls_raw.npy')
    sca_patients_raw = os.path.join(features_dir, 'sca_patients_raw.npy')

    if not os.path.isfile(sca_patients_raw):
        dict_controls_sca = {}
        dict_patients_sca = {}

        for seed_name in seeds:
            print '-- Extracting CONTROL SBCA for', seed_name
            dict_controls_sca[seed_name] = return_sca_data(seed_name, controls, derivatives_dir)
            print '-- Extracting PATIENT SBCA for', seed_name
            dict_patients_sca[seed_name] = return_sca_data(seed_name, patients, derivatives_dir)

        print 'Raw dataframes contain these seeds -->',  dict_controls_sca.keys()
        np.save(sca_controls_raw,  dict_controls_sca)
        np.save(sca_patients_raw,  dict_patients_sca)


    ################################################################################################
    print ' 2. Nuisance variable regression - Age, Gender, Site, Image-Quality'
    print ''
    # Extract Raw Data
    sca_controls_raw = pd.concat([np.load(sca_controls_raw)[()][seed] for seed in seeds], axis =0)
    sca_patients_raw = pd.concat([np.load(sca_patients_raw)[()][seed] for seed in seeds], axis =0)

    plot_heatmap(sca_controls_raw, '%s/sca_controls_raw'%features_dir, cmap =cmap_gradient)
    plot_heatmap(sca_patients_raw, '%s/sca_patients_raw'%features_dir, cmap =cmap_gradient)

    print 'Control Dataframe shape=', sca_controls_raw.shape
    print 'Patient Dataframe shape=', sca_patients_raw.shape

    # Regression
    sca_controls_resid = regress_covariates(sca_controls_raw, df_pheno, controls, 'controls', features_dir)


construct_features_dataframe(control_outliers, patient_outliers, tourettome_workspace,
                             tourettome_derivatives, tourettome_freesurfer )



    # ct_lh = nb.load(os.path.join(datadir, 'struct_cortical_thickness',
        #                              '%s_ct2fsaverage5_fwhm20_lh.mgh' % subject)).get_data().ravel()
        # ct_rh = nb.load(os.path.join(datadir, 'struct_cortical_thickness',
        #                              '%s_ct2fsaverage5_fwhm20_rh.mgh' % subject)).get_data().ravel()
        #
        # if scale:
        #     ct_lh = preprocessing.scale(ct_lh)
        #     ct_rh = preprocessing.scale(ct_rh)
        # else:
        #     pass
        # df_ct_lh = pd.DataFrame(ct_lh, columns=[subject], index=['ct_lh_' + str(i) for i in range(ct_lh.shape[0])])
        # df_ct_rh = pd.DataFrame(ct_rh, columns=[subject], index=['ct_rh_' + str(i) for i in range(ct_rh.shape[0])])
        #
        # df_subvol = pd.read_csv(os.path.join(datadir, 'struct_subcortical_volume', '%s_aseg_stats.txt' % subject),
        #                         index_col=0)
        # df_subvol = df_subvol.drop([i for i in df_subvol.columns if i not in nuclei_subcortical], axis=1)
        # df_subvol = pd.DataFrame(scale(df_subvol.T), index=df_subvol.columns, columns=[subject])
        #
        # df_features.append(pd.concat([df_ct_lh, df_ct_rh  # , df_subvol
        #                               ], axis=0))

