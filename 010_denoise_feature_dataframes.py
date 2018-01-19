__author__ = 'kanaan 10.01.2018... re-written 18.10.2018'

import os
import numpy as np
import pandas as pd
import nibabel as nb
import matplotlib
import statsmodels.formula.api as smf
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
sns.set_style('white')

from variables.subject_list import *
from utilities.utils import mkdir_path
from utilities.check_data import return_ct_data, return_sca_data
from plotting.cmaps import cmap_gradient


#based on fd_mu > 0.19
control_outliers = ['HM015', 'LZ061', 'HB028', 'LZ052' ]
patient_outliers = ['HA009', 'HB005', 'HM015', 'HM023', 'HM026', 'LZ004', 'LZ006', 'LZ007', 'LZ013', 'LZ017',
                    'LZ018', 'LZ020', 'LZ022', 'LZ025', 'LZ027', 'LZ028', 'LZ029', 'LZ031', 'LZ035', 'LZ038',
                    'PA009', 'PA012', 'PA025', 'PA045', 'PA052', 'PA055', 'PA058', 'PA077', 'PA080', 'PA094',
                    'LZ001',]

#based on fd_max > 1 and fd_mu> 0.2
control_outliers = ['HM015', 'HM028', 'LZ057', 'LZ061', 'PA059', 'LZ052' ]
patient_outliers = ['HA009', 'HA016', 'HB005', 'HB011', 'HB015', 'HM015', 'HM023', 'HM026', 'HM028', 'LZ004',
                    'LZ006', 'LZ007', 'LZ013', 'LZ017', 'LZ018', 'LZ020', 'LZ021', 'LZ025', 'LZ027', 'LZ028',
                    'LZ029', 'LZ030', 'LZ031', 'LZ035', 'LZ038', 'PA001', 'PA006', 'PA009', 'PA011', 'PA012',
                    'PA013', 'PA019', 'PA025', 'PA039', 'PA045', 'PA052', 'PA055', 'PA058', 'PA061', 'PA066',
                    'PA077', 'PA078', 'PA080', 'PA081', 'PA094', 'PA095', 'LZ001',]

# LZ001, LZ052 are missing data

seeds = ['STR3_MOTOR', 'STR3_LIMBIC', 'STR3_EXEC', 'PALL', 'THAL'
        ]
terms = ['Age', 'Sex', 'Site', 'qc_func_fd', 'qc_anat_cjv']


def regress_nuisance_covariates(df_features, df_design):
    # Regress features
    df_features = np.nan_to_num(df_features).T
    df_features_resid = []

    print '...... Tourettome dmatrix  shape=', df_design.shape
    print '...... Tourettome features shape=', df_features.shape

    formula = 'y ~ Age + male + female + HANNOVER_A + HANNOVER_B + HAMBURG + Leipzig + PARIS + CJV + FD + DVARS + TSNR'
    for vertex_id in range(df_features.shape[1]):
        mat = df_design
        mat['y'] = df_features[:, vertex_id]
        model = smf.ols(formula=formula, data=pd.DataFrame(mat))
        df_features_resid.append(model.fit().resid)
    return df_features_resid


def construct_features_dataframe(derivatives_dir):

    print '========================================================================================'
    print ''
    print '                    Tourettome - 009. Create Feature Dataframes                         '
    print ''
    print '========================================================================================'
    print ''

    #I/O
    features_dir = mkdir_path(os.path.join(derivatives_dir, 'feature_matrices'))

    ########################################################################################################
    print '################################################################################################'
    print ' Inspecting sample size'

    df_pheno = pd.read_csv(os.path.join(tourettome_phenotypic, 'tourettome_phenotypic.csv'), index_col=0)
    population = df_pheno.index

    # Extract groups
    patients = sorted([i for i in population if df_pheno.loc[i]['Group'] == 'patients' if
                       i not in patient_outliers])
    controls = sorted([i for i in population if df_pheno.loc[i]['Group'] == 'controls' or
                       df_pheno.loc[i]['Group'] == 'probands' if i not in control_outliers])
    tourettome_subjects = sorted(controls + patients)

    # create group phenotypic dataframes
    df_pheno_controls = df_pheno.drop([i for i in df_pheno.index if i not in controls], axis=0)
    df_pheno_controls = df_pheno_controls.drop([i for i in df_pheno_controls.columns if i not in terms], axis=1)

    df_pheno_patients = df_pheno.drop([i for i in df_pheno.index if i not in patients], axis=0)
    df_pheno_patients = df_pheno_patients.drop([i for i in df_pheno_patients.columns if i not in terms], axis=1)

    # Included subjects
    print 'n_controls=', len(controls)
    print 'n_patients=', len(patients)
    print 'n_total =', len(tourettome_subjects)
    print ''

    # Outliers
    print 'n_control_outliers=', len(control_outliers)
    print 'n_patients_outliers=', len(patient_outliers)
    print 'n_total_outliers =', len(control_outliers) + len(patient_outliers)
    print ''

    #######################################################################################################
    print '################################################################################################'
    print '... Extracting SCA data'

    if not os.path.isfile(os.path.join(features_dir, 'sca_tourettome_raw.csv')):
        sca_tourettome_raw = []
        for seed_name in seeds:
            print 'checking sca data for tourettome population (After QC)'
            sca_tourettome_raw.append(return_sca_data(seed_name, tourettome_subjects, derivatives_dir))

        # Save raw dataframes
        sca_tourettome_raw = pd.concat(sca_tourettome_raw)
        sca_tourettome_raw.to_csv(os.path.join(features_dir, 'sca_tourettome_raw.csv'))

        # Save raw dataframe plot
        f = plt.figure(figsize=(35, 20))
        sns.heatmap(sca_tourettome_raw, yticklabels=False, cmap=cmap_gradient, vmin=-1, vmax=1)
        plt.xticks(size=6, rotation=90, weight='bold')
        f.savefig(os.path.join(features_dir, 'sca_tourettome_raw.png'), dpi=300)

    else:
        sca_tourettome_raw = pd.read_csv(os.path.join(features_dir, 'sca_tourettome_raw.csv'), index_col=0)

    ############################################################################################################
    print '################################################################################################'
    print '... Build Design Matrix'

    if not os.path.isfile(os.path.join(features_dir, 'design_matrix_tourettome.csv')):
        # Create design matrix
        design_matrix = pd.DataFrame(index=sca_tourettome_raw.columns)
        design_matrix['Age'] = df_pheno['Age']

        def make_dmat_category(old_col, new_col):
            for subject in design_matrix.index:
                if df_pheno.loc[subject][old_col] == new_col:
                    design_matrix.loc[subject, new_col] = 1
                else:
                    design_matrix.loc[subject, new_col] = 0

        make_dmat_category('Sex', 'male')
        make_dmat_category('Sex', 'female')
        make_dmat_category('Site', 'HANNOVER_A')
        make_dmat_category('Site', 'HANNOVER_B')
        make_dmat_category('Site', 'HAMBURG')
        make_dmat_category('Site', 'Leipzig')
        make_dmat_category('Site', 'PARIS')
        design_matrix['CJV'] = df_pheno['qc_anat_cjv']
        design_matrix['FD'] = df_pheno['qc_func_fd']
        design_matrix['DVARS'] = df_pheno['qc_func_dvars']
        design_matrix['TSNR'] = df_pheno['qc_func_tsnr']
        # design_matrix['SNR'] = df_pheno['qc_func_snr']
        # design_matrix['FBER'] = df_pheno['qc_func_fber']


        # Save design matrix data
        design_matrix.to_csv(os.path.join(features_dir, 'design_matrix_tourettome.csv'))

        # Plot design matrix
        f = plt.figure(figsize=(12, 8))
        for i in ['Age', 'FD', 'DVARS', 'TSNR']:
            design_matrix[i] = preprocessing.scale(design_matrix[i])
        sns.heatmap(design_matrix, yticklabels=False, cmap=cmap_gradient, vmin=-2.5, vmax=2.5)
        plt.xticks(size=20, rotation=90, weight='bold')
        f.savefig(os.path.join(features_dir, 'design_matrix_tourettome.png'), dpi = 300, bbox_inches='tight')

    design_matrix = pd.read_csv(os.path.join(features_dir, 'design_matrix_tourettome.csv'), index_col = 0)

    ########################################################################################################
    print '################################################################################################'
    print '... SCA nuisance variable regression'

    if not os.path.isfile(os.path.join(features_dir, 'sca_patients_resid_z.csv')):

        if not os.path.isfile(os.path.join(features_dir, 'sca_tourettome_resid.csv')):
            sca_tourettome_resid = regress_nuisance_covariates(sca_tourettome_raw, design_matrix)

            # save residual data
            sca_tourettome_resid = pd.concat(sca_tourettome_resid, axis=1).T  # transpose here to get back to RAW shape
            sca_tourettome_resid.to_csv(os.path.join(features_dir, 'sca_tourettome_resid.csv'))

            # plot sca residuals
            f = plt.figure(figsize=(35, 20))
            sns.heatmap(sca_tourettome_resid, yticklabels=False, cmap=cmap_gradient, vmin=-1, vmax=1)
            plt.xticks(size=6, rotation=90, weight='bold')
            f.savefig(os.path.join(features_dir, 'sca_tourettome_resid.png'), dpi=300)

        else:
            sca_tourettome_resid = pd.read_csv(os.path.join(features_dir, 'sca_tourettome_resid.csv'), index_col=0)


        ########################################################################################################
        print '################################################################################################'
        print ' ... Z-scoring SCA dataframes'
        # "At each surface point, we normalized feature data in each individual with ASD against the
        # corresponding distribution in control using vertex-wise zscoring (Bernhardt, AnnNeurology, 2015)"

        print '...... Breaking down Tourettome_resid into patients/controls dfs and plotting'
        # break down sca_tourettome_resid to patient and control dataframes
        sca_patients_resid = sca_tourettome_resid.drop(controls, axis=1)
        sca_controls_resid = sca_tourettome_resid.drop(patients, axis=1)

        if not os.path.isfile(os.path.join(features_dir,'sca_patients_resid.csv')):
            # save separately
            sca_patients_resid.to_csv(os.path.join(features_dir,'sca_patients_resid.csv'))
            sca_controls_resid.to_csv(os.path.join(features_dir,'sca_controls_resid.csv'))

            # plot separate sca residuals
            f = plt.figure(figsize=(17.5, 10))
            sns.heatmap(sca_controls_resid, yticklabels=False, cmap=cmap_gradient, vmin=-1, vmax=1)
            plt.xticks(size=6, rotation=90, weight='bold')
            f.savefig(os.path.join(features_dir, 'sca_controls_resid.png'), dpi=300)

            f = plt.figure(figsize=(17.5, 10))
            sns.heatmap(sca_patients_resid, yticklabels=False, cmap=cmap_gradient, vmin=-1, vmax=1)
            plt.xticks(size=6, rotation=90, weight='bold')
            f.savefig(os.path.join(features_dir, 'sca_patients_resid.png'), dpi=300)

        print '...... Z-scoring patients'
        # get vertex means/sds across control subjects
        n_vertices = sca_patients_resid.shape[0]
        vertices_mu = [np.mean(sca_controls_resid.loc[vertex]) for vertex in range(n_vertices)]
        vertices_sd = [np.std(sca_controls_resid.loc[vertex]) for vertex in range(n_vertices)]

        if not os.path.isfile(os.path.join(features_dir, 'sca_patients_resid_z.csv')):
            # z-score patients
            sca_patients_resid_z = pd.concat([(sca_patients_resid.loc[vertex] - vertices_mu[vertex]) / vertices_sd[vertex]
                                            for vertex in range(n_vertices)], axis=1).T
            sca_patients_resid_z.to_csv(os.path.join(features_dir, 'sca_patients_resid_z.csv'))

            # plot sca residuals
            f = plt.figure(figsize=(35, 20))
            sns.heatmap(sca_patients_resid_z, yticklabels=False, cmap=cmap_gradient, vmin=-3, vmax=3)
            plt.xticks(size=6, rotation=90, weight='bold')
            f.savefig(os.path.join(features_dir, 'sca_patients_resid_z.png'), dpi=300)

        print '...... Z-scoring controls'
        if not os.path.isfile(os.path.join(features_dir, 'sca_controls_resid_z.csv')):
            # z-score patients
            sca_controls_resid_z = pd.concat([(sca_controls_resid.loc[vertex] - vertices_mu[vertex]) / vertices_sd[vertex]
                                              for vertex in range(n_vertices)], axis=1).T
            sca_controls_resid_z.to_csv(os.path.join(features_dir, 'sca_controls_resid_z.csv'))

            # plot sca residuals
            f = plt.figure(figsize=(35, 20))
            sns.heatmap(sca_controls_resid_z, yticklabels=False, cmap=cmap_gradient, vmin=-3, vmax=3)
            plt.xticks(size=6, rotation=90, weight='bold')
            f.savefig(os.path.join(features_dir, 'sca_controls_resid_z.png'), dpi=300)


    else:
        print 'SCA already denoised'

    #######################################################################################################
    print '################################################################################################'
    print '... Extracting Cortical-thickness data'

    if not os.path.isfile(os.path.join(features_dir, 'ct_tourettome_raw.csv')):
        print '......checking CT data for tourettome population (After QC)'

        # only take subjects that have ct and are not outliers
        tourettome_subjects_ct = np.unique([i[0:5] for i in os.listdir(os.path.join(tourettome_derivatives, 'struct_cortical_thickness'))])
        tourettome_subjects_ct = [i for i in tourettome_subjects_ct if i not in control_outliers + patient_outliers]

        #check data and save
        ct_tourettome_raw= return_ct_data(tourettome_subjects_ct, tourettome_derivatives)
        ct_tourettome_raw.to_csv(os.path.join(features_dir, 'ct_tourettome_raw.csv'))

        # plot ct_raw
        f = plt.figure(figsize=(35, 20))
        sns.heatmap(ct_tourettome_raw, yticklabels=False, cmap=cmap_gradient, vmin=1, vmax=3.5)
        plt.xticks(size=6, rotation=90)
        f.savefig(os.path.join(features_dir, 'ct_tourettome_raw.png'), bbox_inches = 'tight')

    else:
        ct_tourettome_raw = pd.read_csv(os.path.join(features_dir, 'ct_tourettome_raw.csv'),index_col=0)

    print ct_tourettome_raw.shape

    ########################################################################################################
    print '################################################################################################'
    print '... Cortical-thickness nuisance variable regression'

    if not os.path.isfile(os.path.join(features_dir, 'ct_tourettome_resid.csv')):

        # first drop subjects from design matrix that dont have CT----- due to freesurfer failure. get those subs back
        design_matrix = pd.read_csv(os.path.join(features_dir, 'design_matrix_tourettome.csv'), index_col=0)
        design_matrix = design_matrix.drop([i for i in design_matrix.index if i not in ct_tourettome_raw.columns],
                                           axis = 0 )

        ct_tourettome_resid = regress_nuisance_covariates(ct_tourettome_raw, design_matrix)

        # save residual data
        ct_tourettome_resid = pd.concat(ct_tourettome_resid, axis=1).T  # transpose here to get back to RAW shape
        ct_tourettome_resid.to_csv(os.path.join(features_dir, 'ct_tourettome_resid.csv'))

        # plot sca residuals
        f = plt.figure(figsize=(35, 20))
        sns.heatmap(ct_tourettome_resid, yticklabels=False, cmap=cmap_gradient, vmin=-1, vmax=1)
        plt.xticks(size=6, rotation=90, weight='bold')
        f.savefig(os.path.join(features_dir, 'ct_tourettome_resid.png'), dpi=300)

    else:
        ct_tourettome_resid = pd.read_csv(os.path.join(features_dir, 'ct_tourettome_resid.csv'), index_col=0)


    ########################################################################################################
    print '################################################################################################'
    print ' ... Z-scoring CT dataframes'

    print '...... Breaking down Tourettome_resid into patients/controls dfs and plotting'
    # break down CT to patient and control dataframes
    ct_patients_resid = ct_tourettome_resid.drop([i for i in controls if i in ct_tourettome_resid.columns], axis=1)
    ct_controls_resid = ct_tourettome_resid.drop([i for i in patients if i in ct_tourettome_resid.columns], axis=1)

    if not os.path.isfile(os.path.join(features_dir, 'ct_patients_resid.csv')):
        # save separately
        ct_patients_resid.to_csv(os.path.join(features_dir, 'ct_patients_resid.csv'))
        ct_controls_resid.to_csv(os.path.join(features_dir, 'ct_controls_resid.csv'))

        # plot separate sca residuals
        f = plt.figure(figsize=(17.5, 10))
        sns.heatmap(ct_controls_resid, yticklabels=False, cmap=cmap_gradient, vmin=-1, vmax=1)
        plt.xticks(size=6, rotation=90, weight='bold')
        f.savefig(os.path.join(features_dir, 'ct_controls_resid.png'), dpi=300)

        f = plt.figure(figsize=(17.5, 10))
        sns.heatmap(ct_patients_resid, yticklabels=False, cmap=cmap_gradient, vmin=-1, vmax=1)
        plt.xticks(size=6, rotation=90, weight='bold')
        f.savefig(os.path.join(features_dir, 'ct_patients_resid.png'), dpi=300)

    print '...... Z-scoring patients'
    # get vertex means/sds across control subjects
    n_vertices = ct_patients_resid.shape[0]
    vertices_mu = [np.mean(ct_controls_resid.loc[vertex]) for vertex in range(n_vertices)]
    vertices_sd = [np.std(ct_controls_resid.loc[vertex]) for vertex in range(n_vertices)]

    if not os.path.isfile(os.path.join(features_dir, 'ct_patients_resid_z.csv')):
        # z-score patients
        ct_patients_resid_z = pd.concat([(ct_patients_resid.loc[vertex] - vertices_mu[vertex]) / vertices_sd[vertex]
                                          for vertex in range(n_vertices)], axis=1).T
        ct_patients_resid_z.to_csv(os.path.join(features_dir, 'ct_patients_resid_z.csv'))

        # plot sca residuals
        f = plt.figure(figsize=(35, 20))
        sns.heatmap(ct_patients_resid_z, yticklabels=False, cmap=cmap_gradient, vmin=-3, vmax=3)
        plt.xticks(size=6, rotation=90, weight='bold')
        f.savefig(os.path.join(features_dir, 'ct_patients_resid_z.png'), dpi=300)

    print '...... Z-scoring controls'
    if not os.path.isfile(os.path.join(features_dir, 'ct_controls_resid_z.csv')):
        # z-score patients
        ct_controls_resid_z = pd.concat([(ct_controls_resid.loc[vertex] - vertices_mu[vertex]) / vertices_sd[vertex]
                                          for vertex in range(n_vertices)], axis=1).T
        ct_controls_resid_z.to_csv(os.path.join(features_dir, 'ct_controls_resid_z.csv'))

        # plot sca residuals
        f = plt.figure(figsize=(35, 20))
        sns.heatmap(ct_controls_resid_z, yticklabels=False, cmap=cmap_gradient, vmin=-3, vmax=3)
        plt.xticks(size=6, rotation=90, weight='bold')
        f.savefig(os.path.join(features_dir, 'ct_controls_resid_z.png'), dpi=300)



construct_features_dataframe(tourettome_derivatives)