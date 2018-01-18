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
sns.set_style('white')

from variables.subject_list import *
from utilities.utils import mkdir_path
from utilities.check_data import return_ct_data, return_sca_data
from plotting.cmaps import cmap_gradient


control_outliers = ['HM015', 'LZ061', 'HB028', 'LZ052' ]
patient_outliers = ['HA009', 'HB005', 'HM015', 'HM023', 'HM026', 'LZ004', 'LZ006', 'LZ007', 'LZ013', 'LZ017',
                    'LZ018', 'LZ020', 'LZ022', 'LZ025', 'LZ027', 'LZ028', 'LZ029', 'LZ031', 'LZ035', 'LZ038',
                    'PA009', 'PA012', 'PA025', 'PA045', 'PA052', 'PA055', 'PA058', 'PA077', 'PA080', 'PA094',
                    'LZ001',]

seeds = ['STR3_MOTOR'#, 'STR3_LIMBIC', 'STR3_EXEC', 'PALL', 'THAL'
        ]
terms = ['Age', 'Sex', 'Site', 'qc_func_fd', 'qc_anat_cjv']


def construct_features_dataframe(derivatives_dir):

    print '========================================================================================'
    print ''
    print '                    Tourettome - 009. Create Feature Dataframes                         '
    print ''
    print '========================================================================================'
    print ''

    #I/O
    features_dir = mkdir_path(os.path.join(derivatives_dir, 'feature_matrices'))

    ############################################################################################################
    print '#####################################################'
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

    ############################################################################################################
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


construct_features_dataframe(tourettome_derivatives)