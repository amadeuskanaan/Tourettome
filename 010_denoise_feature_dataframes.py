__author__ = 'kanaan 10.01.2018'


import os
import numpy as np
import pandas as pd
import nibabel as nb
from patsy import dmatrix
import statsmodels.formula.api as smf

from variables import *
from utilities.utils import mkdir_path, return_sca_data


def regress_covariates(df_features, df_pheno):

    # Build design Matrix "C(a, contrast)"
    formula = " 0 + Sex + Site + Age + qc_func_fd + qc_anat_cjv"
    design_matrix = dmatrix(formula, df_pheno, return_type="dataframe")
    design_matrix.sort_index(axis=1, inplace=True)
    design_matrix.columns = ['age', 'female', 'male', 'hannover_b', 'leipzig', 'paris', 'cjv', 'fd']

    df_features = np.nan_to_num(df_features).T
    df_features_resid = []

    # Fit linear model
    for vertex_id in range(df_features.shape[1]):
        mat = design_matrix
        mat['y'] = df_features[:, vertex_id]
        formula = 'y ~ age + female + male + hannover_b + leipzig + paris + cjv + fd'
        model = smf.ols(formula=formula, data=pd.DataFrame(mat))
        df_features_resid.append(model.fit().resid)

    df_features_resid = pd.concat(df_features_resid, axis=1)
    return df_features_resid

rsfc_seeds = ['STR3_MOTOR', 'STR3_LIMBIC', 'STR3_EXEC',
              #'PALL', 'THAL'
             ]

def construct_features_dataframe(population_controls, population_patients,
                                 workspace_dir, derivatives_dir, freesufer_dir):

    print '========================================================================================'
    print ''
    print '                    Tourettome - 009. Create Feature Dataframes                         '
    print ''
    print '========================================================================================'
    print ''
    print '..... n_controls=', len(controls)
    print '..... n_patients=', len(patients)
    print '..... n_total =', len(controls) + len(patients)
    print ''
    print ' 1. Extracting functional features'

    print 'A-  Extracting Seed-based correlation data for seeds =',seeds

    dict_controls_sca = {}
    dict_patients_sca = {}

    for seed_name in seeds:
        dict_controls_sca[seed_name] = return_sca_data(seed_name, controls, derivatives_dir)
        dict_controls_sca[seed_name] = return_sca_data(seed_name, patients, derivatives_dir)

    print dict_controls_sca.keys()
    print dict_patients_sca.keys()

    #df_controls_features = pd.concat([df_controls_sca[seed]['sca'] for seed in df_controls_sca.keys()])
    #df_patients_features = pd.concat([df_patients_sca[seed]['sca'] for seed in df_patients_sca.keys()])


construct_features_dataframe(qc_controls, qc_patients, tourettome_workspace,
                             tourettome_derivatives, tourettome_freesurfer )






    # print '..... Controls dataframe shape =',df_controls_features.shape
    # print '..... Patients dataframe shape =',df_patients_features.shape

    # print ''
    # print 'B- Regressing out nuisance variables= age, gender, site, image quality'
    #
    # # Construct clean phenotypic dataframe
    # terms = ['Age', 'Sex', 'Site', 'qc_func_fd', 'qc_anat_cjv']
    # df_pheno = pd.read_csv(os.path.join(derivatives_dir, 'phenotypic/tourettome_phenotypic.csv'), index_col = 0)

    # df_pheno_controls = df_pheno.drop([i for i in df_pheno.index if i not in controls], axis=0)
    # df_pheno_controls = df_pheno_controls.drop([i for i in df_pheno_controls.columns if i not in terms], axis=1)
    #
    # df_pheno_patients = df_pheno.drop([i for i in df_pheno.index if i not in patients], axis=0)
    # df_pheno_patients = df_pheno_patients.drop([i for i in df_pheno_patients.columns if i not in terms], axis=1)

    # df_controls_features_resid = regress_covariates(df_controls_features, df_pheno_controls)
    # df_patients_features_resid = regress_covariates(df_patients_features, df_pheno_patients)

    # print 'C- z-scoring patient data based on control distribution'
    # n_vertices = df_controls_features_resid.shape[1]
    # vertex_mu = [np.mean(df_controls_features_resid.T.loc[vertex]) for vertex in range(n_vertices)]
    # vertex_sd = [np.std(df_controls_features_resid.T.loc[vertex]) for vertex in range(n_vertices)]
    #
    # df_controls_features_resid_z = pd.concat([(df_controls_features_resid.T.loc[vertex] - vertex_mu[vertex]) /
    #                                 vertex_sd[vertex] for vertex in range(n_vertices)], axis=1)
    #
    # df_patients_features_resid_z = pd.concat( [(df_patients_features_resid.T.loc[vertex] - vertex_mu[vertex]) /
    #                                 vertex_sd[vertex] for vertex in range(n_vertices)], axis=1)



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

