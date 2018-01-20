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
from utilities.check_data import return_ct_data, return_sca_data, return_ecm_data
from plotting.cmaps import cmap_gradient


#based on fd_mu > 0.19
control_outliers = ['HM015', 'LZ061', 'HB028', 'LZ052' ]
patient_outliers = ['HA009', 'HB005', 'HM015', 'HM023', 'HM026', 'LZ004', 'LZ006', 'LZ007', 'LZ013', 'LZ017',
                    'LZ018', 'LZ020', 'LZ022', 'LZ025', 'LZ027', 'LZ028', 'LZ029', 'LZ031', 'LZ035', 'LZ038',
                    'PA009', 'PA012', 'PA025', 'PA045', 'PA052', 'PA055', 'PA058', 'PA077', 'PA080', 'PA094',
                    'LZ001']

# hamburg data has artifact..
# LZ001, LZ052 are missing data

hamburg_controls = ['HM001', 'HM004', 'HM006', 'HM012', 'HM014', 'HM017', 'HM019', 'HM022','HM025', 'HM027',
                    'HM028', 'HM029','HM030','HM032']
hamburg_patients = ['HM002', 'HM003', 'HM005', 'HM007', 'HM008', 'HM009', 'HM010', 'HM011', 'HM020', 'HM024',
                    'HM031', 'HM033']
hamburg          = hamburg_patients+hamburg_controls

# QC based on fd_max > 1 and fd_mu> 0.2
control_outliers = ['HM015', 'HM028', 'LZ057', 'LZ061', 'PA059', 'LZ052' ] + hamburg_controls
patient_outliers = ['HA009', 'HA016', 'HB005', 'HB011', 'HB015', 'HM015', 'HM023', 'HM026', 'HM028', 'LZ004',
                    'LZ006', 'LZ007', 'LZ013', 'LZ017', 'LZ018', 'LZ020', 'LZ021', 'LZ025', 'LZ027', 'LZ028',
                    'LZ029', 'LZ030', 'LZ031', 'LZ035', 'LZ038', 'PA001', 'PA006', 'PA009', 'PA011', 'PA012',
                    'PA013', 'PA019', 'PA025', 'PA039', 'PA045', 'PA052', 'PA055', 'PA058', 'PA061', 'PA066',
                    'PA077', 'PA078', 'PA080', 'PA081', 'PA094', 'PA095', 'LZ001'] + hamburg_patients


rsfc_seeds = ['STR3_MOTOR', 'STR3_LIMBIC', 'STR3_EXEC', 'PALL', 'THAL']
terms      = ['Age', 'Sex', 'Site', 'qc_func_fd', 'qc_anat_cjv']
formula  = 'y ~ Age + male + female + HANNOVER_A + HANNOVER_B + Leipzig + PARIS + CJV + FD'

def regress_nuisance_covariates(df_features, df_design, formula):
    # Regress features
    df_features = np.nan_to_num(df_features).T
    df_features_resid = []

    print '......... Tourettome dmatrix  shape=', df_design.shape
    print '......... Tourettome features shape=', df_features.shape

    for vertex_id in range(df_features.shape[1]):
        mat = df_design
        mat['y'] = df_features[:, vertex_id]
        model = smf.ols(formula=formula, data=pd.DataFrame(mat))
        df_features_resid.append(model.fit().resid)
    return df_features_resid


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


def plt_features_heatmap(df, fname, vmin, vmax, figsize =(35, 20),  yticklabels=False, dpi = 300):
    f = plt.figure(figsize=figsize)
    sns.heatmap(df, yticklabels=yticklabels, cmap=cmap_gradient, vmin=vmin, vmax=vmax)
    plt.xticks(size=6, rotation=90, weight='bold')
    f.savefig(fname, dpi=dpi, bbox_inches = 'tight')

def construct_features_dataframe(derivatives_dir, control_outliers, patients_outliers, rsfc_seeds):

    print '========================================================================================'
    print ''
    print '                    Tourettome - 009. Create Feature Dataframes                         '
    print ''
    print '========================================================================================'
    print ''

    #I/O
    features_dir = mkdir_path(os.path.join(derivatives_dir, 'feature_matrices'))

    ########################################################################################################
    print '###########################################################'
    print ' Inspecting sample size'

    df_pheno = pd.read_csv(os.path.join(tourettome_phenotypic, 'tourettome_phenotypic.csv'),
                           index_col=0).drop(control_outliers+patients_outliers,axis =0)
    population = df_pheno.index

    # Extract groups
    patients = sorted([i for i in population if df_pheno.loc[i]['Group'] == 'patients'])
    controls = sorted([i for i in population if df_pheno.loc[i]['Group'] == 'controls'])
    tourettome_subjects = sorted(controls + patients)

    # create group phenotypic dataframes
    df_pheno_controls = df_pheno.drop([i for i in df_pheno.index if i not in controls], axis=0)
    df_pheno_patients = df_pheno.drop([i for i in df_pheno.index if i not in patients], axis=0)
    df_pheno_controls = df_pheno_controls.drop([i for i in df_pheno_controls.columns if i not in terms], axis=1)
    df_pheno_patients = df_pheno_patients.drop([i for i in df_pheno_patients.columns if i not in terms], axis=1)

    df_pheno_controls.to_csv(os.path.join(tourettome_phenotypic, 'tourettome_phenotypic_controls.csv'))
    df_pheno_patients.to_csv(os.path.join(tourettome_phenotypic, 'tourettome_phenotypic_patients.csv'))

    # Included subjects
    print 'n_controls=', len(controls)
    print 'n_patients=', len(patients)
    print 'n_total =', len(tourettome_subjects)
    print ''

    # Outliers
    print 'n_control_outliers=', len(control_outliers)
    print 'n_patients_outliers=', len(patient_outliers)
    # print 'n_total_outliers =', len([i for i in control_outliers+patient_outliers if i not in hamburg])
    print 'n_total_outliers =', len(control_outliers+patient_outliers)
    print ''

    #######################################################################################################
    print '###########################################################'
    print '... Extracting SCA, CT & ECM data for QCd tourettome population'

    ###################
    # SCA
    if not os.path.isfile(os.path.join(features_dir, 'sca_tourettome_raw.csv')):
        print '...... Checking SCA data'
        sca_tourettome_raw = []
        for seed_name in rsfc_seeds:
            print '......... %s'%seed_name
            sca_tourettome_raw.append(return_sca_data(seed_name, tourettome_subjects, derivatives_dir))

        # Save raw dataframes
        sca_tourettome_raw = pd.concat(sca_tourettome_raw)
        sca_tourettome_raw.to_csv(os.path.join(features_dir, 'sca_tourettome_raw.csv'))
        plt_features_heatmap(sca_tourettome_raw, os.path.join(features_dir, 'sca_tourettome_raw.png'), vmin=-1,vmax=1)

    else:
        sca_tourettome_raw = pd.read_csv(os.path.join(features_dir, 'sca_tourettome_raw.csv'), index_col=0)

    ###################
    # CT
    if not os.path.isfile(os.path.join(features_dir, 'ct_tourettome_raw.csv')):
        print '...... Checking CT data'

        # only take subjects that have ct and are not outliers
        tourettome_subjects_ct = np.unique([i[0:5] for i in os.listdir(os.path.join(tourettome_derivatives, 'struct_cortical_thickness'))])
        tourettome_subjects_ct = [i for i in tourettome_subjects_ct if i not in control_outliers + patient_outliers]

        #check data and save
        ct_tourettome_raw= return_ct_data(tourettome_subjects_ct, tourettome_derivatives)
        ct_tourettome_raw.to_csv(os.path.join(features_dir, 'ct_tourettome_raw.csv'))
        plt_features_heatmap(ct_tourettome_raw, os.path.join(features_dir, 'ct_tourettome_raw.png'), vmin=-0, vmax=4)

    else:
        ct_tourettome_raw = pd.read_csv(os.path.join(features_dir, 'ct_tourettome_raw.csv'),index_col=0)

    # ###################
    # # ECM
    # if not os.path.isfile(os.path.join(features_dir, 'ecm_tourettome_raw.csv')):
    #     print '...... Checking ECM data'
    #     # check data and save
    #     ecm_tourettome_raw = return_ecm_data(tourettome_subjects, tourettome_derivatives)
    #     ecm_tourettome_raw.to_csv(os.path.join(features_dir, 'ecm_tourettome_raw.csv'))
    #     plt_features_heatmap(ecm_tourettome_raw, os.path.join(features_dir, 'ecm_tourettome_raw.png'), vmin=-1, vmax=1)

    ############################################################################################################
    print '###########################################################'
    print '... Building Design Matrix'

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
        #make_dmat_category('Site', 'HAMBURG')
        make_dmat_category('Site', 'Leipzig')
        make_dmat_category('Site', 'PARIS')
        design_matrix['CJV'] = df_pheno['qc_anat_cjv']
        design_matrix['FD'] = df_pheno['qc_func_fd']
        # design_matrix['DVARS'] = df_pheno['qc_func_dvars']
        # design_matrix['TSNR'] = df_pheno['qc_func_tsnr']

        # Save design matrix data
        design_matrix.to_csv(os.path.join(features_dir, 'design_matrix_tourettome.csv'))

        # Plot design matrix
        f = plt.figure(figsize=(12, 8))
        for i in ['Age', 'FD']:
            design_matrix[i] = preprocessing.scale(design_matrix[i])
        sns.heatmap(design_matrix, yticklabels=False, cmap=cmap_gradient, vmin=-2.5, vmax=2.5)
        plt.xticks(size=20, rotation=90, weight='bold')
        f.savefig(os.path.join(features_dir, 'design_matrix_tourettome.png'), dpi = 300, bbox_inches='tight')

    design_matrix = pd.read_csv(os.path.join(features_dir, 'design_matrix_tourettome.csv'), index_col = 0)

    ########################################################################################################
    print '###########################################################'
    print '... Denoising SCA features'

    if not os.path.isfile(os.path.join(features_dir, 'sca_patients_resid_z.csv')):

        #####################
        # Regress
        if not os.path.isfile(os.path.join(features_dir, 'sca_tourettome_resid.csv')):
            print '...... Regressing nuisace variables for SCA dataframes'
            sca_tourettome_resid = regress_nuisance_covariates(sca_tourettome_raw, design_matrix, formula)

            # save residual data
            sca_tourettome_resid = pd.concat(sca_tourettome_resid, axis=1).T  # transpose here to get back to RAW shape
            sca_tourettome_resid.to_csv(os.path.join(features_dir, 'sca_tourettome_resid.csv'))

            # plot sca residuals
            plt_features_heatmap(sca_tourettome_resid, os.path.join(features_dir, 'sca_tourettome_resid.png'),
                                 vmin=-2,vmax=2)

        #####################
        # Break down sca_tourettome_resid to patient and control dataframes
        if not os.path.isfile(os.path.join(features_dir, 'sca_patients_resid.csv')):
            sca_tourettome_resid = pd.read_csv(os.path.join(features_dir, 'sca_tourettome_resid.csv'), index_col =0)
            sca_patients_resid = sca_tourettome_resid.drop(controls, axis=1)
            sca_controls_resid = sca_tourettome_resid.drop(patients, axis=1)

            # save separately
            sca_patients_resid.to_csv(os.path.join(features_dir, 'sca_patients_resid.csv'))
            sca_controls_resid.to_csv(os.path.join(features_dir, 'sca_controls_resid.csv'))

            # plot separate sca residuals
            plt_features_heatmap(sca_controls_resid, os.path.join(features_dir, 'sca_controls_resid.png'),
                                 vmin=-1, vmax=1, figsize=(17.5, 10))
            plt_features_heatmap(sca_patients_resid, os.path.join(features_dir, 'sca_patients_resid.png'),
                                 vmin=-1, vmax=1, figsize=(17.5, 10))

        else:
            sca_controls_resid = pd.read_csv(os.path.join(features_dir, 'sca_controls_resid.csv'), index_col=0)
            sca_patients_resid = pd.read_csv(os.path.join(features_dir, 'sca_patients_resid.csv'), index_col=0)

        #####################
        # Z-Score
        if not os.path.isfile(os.path.join(features_dir, 'sca_patients_resid_z.csv')):
            print ' ... Z-scoring SCA dataframes'
            sca_controls_resid_z, sca_patients_resid_z = z_score_features(sca_controls_resid, sca_patients_resid)

            # save data
            sca_controls_resid_z.to_csv(os.path.join(features_dir, 'sca_controls_resid_z.csv'))
            sca_patients_resid_z.to_csv(os.path.join(features_dir, 'sca_patients_resid_z.csv'))
            plt_features_heatmap(sca_controls_resid_z, os.path.join(features_dir, 'sca_controls_resid_z.png'),
                                 vmin=-4, vmax=4, figsize=(17.5, 10))
            plt_features_heatmap(sca_patients_resid_z, os.path.join(features_dir, 'sca_patients_resid_z.png'),
                                 vmin=-4, vmax=4, figsize=(17.5, 10))

    else:
        print 'SCA features already denoised'

    ########################################################################################################
    print '###########################################################'
    print '... Denoising CT features'

    if not os.path.isfile(os.path.join(features_dir, 'ct_patients_resid_z.csv')):

        #####################
        # Drop CT subjects from design_matrix
        print '...... Dropping subjects with no freesurfer segmentation'
        print '...... Regressing nuisace variables for CT dataframes'

        # first drop subjects from design matrix that dont have CT----- due to freesurfer failure. get those subs back
        design_matrix = pd.read_csv(os.path.join(features_dir, 'design_matrix_tourettome.csv'), index_col=0)
        design_matrix = design_matrix.drop([i for i in design_matrix.index if i not in ct_tourettome_raw.columns],
                                           axis=0)

        #####################
        # Regress
        if not os.path.isfile(os.path.join(features_dir, 'ct_tourettome_resid.csv')):
            print '...... Regressing nuisace variables for CT dataframes'
            ct_tourettome_resid = regress_nuisance_covariates(ct_tourettome_raw, design_matrix, formula)

            # save residual data
            ct_tourettome_resid = pd.concat(ct_tourettome_resid, axis=1).T  # transpose here to get back to RAW shape
            ct_tourettome_resid.to_csv(os.path.join(features_dir, 'ct_tourettome_resid.csv'))

            # plot ct residuals
            plt_features_heatmap(ct_tourettome_resid, os.path.join(features_dir, 'ct_tourettome_resid.png'),
                                 vmin=-2, vmax=2)

        #####################
        # Break Down mats into patients and controls
        if not os.path.isfile(os.path.join(features_dir, 'ct_patients_resid.csv')):
            # Break down ct_tourettome_resid to patient and control dataframes
            ct_tourettome_resid = pd.read_csv(os.path.join(features_dir, 'ct_tourettome_resid.csv'), index_col=0)
            ct_patients_resid = ct_tourettome_resid.drop([i for i in controls if i in ct_tourettome_resid.columns], axis=1)
            ct_controls_resid = ct_tourettome_resid.drop([i for i in patients if i in ct_tourettome_resid.columns], axis=1)

            # save separately
            ct_patients_resid.to_csv(os.path.join(features_dir, 'ct_patients_resid.csv'))
            ct_controls_resid.to_csv(os.path.join(features_dir, 'ct_controls_resid.csv'))

            # plot separate sca residuals
            plt_features_heatmap(ct_controls_resid, os.path.join(features_dir, 'ct_controls_resid.png'),
                                 vmin=-1, vmax=1, figsize=(17.5, 10))
            plt_features_heatmap(ct_patients_resid, os.path.join(features_dir, 'ct_patients_resid.png'),
                                 vmin=-1, vmax=1, figsize=(17.5, 10))

        else:
            ct_controls_resid = pd.read_csv(os.path.join(features_dir, 'ct_controls_resid.csv'), index_col=0)
            ct_patients_resid = pd.read_csv(os.path.join(features_dir, 'ct_patients_resid.csv'), index_col=0)

        #####################
        # Z-Score
        if not os.path.isfile(os.path.join(features_dir, 'ct_patients_resid_z.csv')):
            print ' ... Z-scoring SCA dataframes'
            ct_controls_resid_z, ct_patients_resid_z = z_score_features(ct_controls_resid, ct_patients_resid)

            # plot separate sca residuals
            plt_features_heatmap(ct_controls_resid_z, os.path.join(features_dir, 'ct_controls_resid_z.png'),
                                 vmin=-4, vmax=4, figsize=(17.5, 10))
            plt_features_heatmap(ct_patients_resid_z, os.path.join(features_dir, 'ct_patients_resid_z.png'),
                                 vmin=-4, vmax=4, figsize=(17.5, 10))

        else:
            print 'CT features already denoised'


    # ########################################################################################################
    # print '###########################################################'
    # print '... Denoising ECM features'
    #
    # if not os.path.isfile(os.path.join(features_dir, 'ecm_patients_resid_z.csv')):
    #
    #     #####################
    #     # Regress
    #     if not os.path.isfile(os.path.join(features_dir, 'ecm_tourettome_resid.csv')):
    #         print '...... Regressing nuisace variables for ECM dataframes'
    #         # must read dmat again since we dropped missing subjects from ct
    #         design_matrix = pd.read_csv(os.path.join(features_dir, 'design_matrix_tourettome.csv'), index_col=0)
    #         ecm_tourettome_resid = regress_nuisance_covariates(ecm_tourettome_raw, design_matrix, formula)
    #
    #         # save residual data
    #         ecm_tourettome_resid = pd.concat(ecm_tourettome_resid, axis=1).T  # transpose here to get back to RAW shape
    #         ecm_tourettome_resid.to_csv(os.path.join(features_dir, 'ecm_tourettome_resid.csv'))
    #         plt_features_heatmap(ecm_tourettome_resid, os.path.join(features_dir, 'ecm_tourettome_resid.png'),vmin=-2,vmax=2)
    #
    #         # Break down sca_tourettome_resid to patient and control dataframes
    #         ecm_patients_resid = ecm_tourettome_resid.drop(controls, axis=1)
    #         ecm_controls_resid = ecm_tourettome_resid.drop(patients, axis=1)
    #
    #         # save separately
    #         ecm_patients_resid.to_csv(os.path.join(features_dir, 'ecm_patients_resid.csv'))
    #         ecm_controls_resid.to_csv(os.path.join(features_dir, 'ecm_controls_resid.csv'))
    #
    #         # plot separate sca residuals
    #         plt_features_heatmap(ecm_controls_resid, os.path.join(features_dir, 'ecm_controls_resid.png'),
    #                              vmin=-1, vmax=1, figsize=(17.5, 10))
    #         plt_features_heatmap(ecm_patients_resid, os.path.join(features_dir, 'ecm_patients_resid.png'),
    #                              vmin=-1, vmax=1, figsize=(17.5, 10))
    #
    #     else:
    #         ecm_controls_resid = pd.read_csv(os.path.join(features_dir, 'ecm_controls_resid.csv'), index_col=0)
    #         ecm_patients_resid = pd.read_csv(os.path.join(features_dir, 'ecm_patients_resid.csv'), index_col=0)
    #
    #     #####################
    #     # Z-Score
    #     if not os.path.isfile(os.path.join(features_dir, 'sca_patients_resid_z.csv')):
    #         print ' ... Z-scoring SCA dataframes'
    #         ecm_controls_resid_z, ecm_patients_resid_z = z_score_features(ecm_controls_resid, ecm_patients_resid)
    #
    #         # plot separate sca residuals
    #         plt_features_heatmap(ecm_controls_resid_z, os.path.join(features_dir, 'ecm_controls_resid_z.png'),
    #                              vmin=-4, vmax=4, figsize=(17.5, 10))
    #         plt_features_heatmap(ecm_patients_resid_z, os.path.join(features_dir, 'ecm_patients_resid_z.png'),
    #                              vmin=-4, vmax=4, figsize=(17.5, 10))
    #
    # else:
    #     print 'ECM features already denoised'

construct_features_dataframe(tourettome_derivatives, control_outliers, patient_outliers, rsfc_seeds)