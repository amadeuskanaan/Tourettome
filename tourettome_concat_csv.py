__author__ = 'kanaan..04.04.2017...@MNI'

import os
import pandas as pd
from variables.subject_list import *

def concat_csv(population, workspace, phenotypic_dir):

    def get_dcm_header(site_id):
        df = pd.read_csv(os.path.join(phenotypic_dir, 'phenotypic_%s.csv'%site_id), index_col = 0)
        df = df[['Group', 'Site', 'Age', 'Sex']]
        return df

    df_dcm = pd.concat([get_dcm_header('hannover_a'),
                        get_dcm_header('hannover_b'),
                        get_dcm_header('leipzig'),
                        get_dcm_header('paris') ])

    # Concat Basal Ganglia bin_count dataframes
    df_count     = pd.concat([pd.read_csv(os.path.join(workspace, subject, 'ANATOMICAL','seg_first', 'bin_count.csv'), index_col = 0)
                          for subject in population], ignore_index = False)
    df_count_jac = pd.concat([pd.read_csv(os.path.join(workspace, subject, 'ANATOMICAL','seg_first', 'bin_count_jac.csv'), index_col = 0)
                          for subject in population], ignore_index = False)


    for roi in rois_bilateral:
        df_count['%s' %roi]  = df_count['L_%s'%roi] + df_count['R_%s'%roi]

    for roi in rois_bilateral:
        df_count_jac['%s' %roi]  = df_count['L_%s'%roi] + df_count['R_%s'%roi]


    df_count['L_STR'] = df_count['L_Caud'] + df_count['L_Puta'] + df_count['L_Accu']
    df_count['R_STR'] = df_count['R_Caud'] + df_count['R_Puta'] + df_count['R_Accu']
    df_count['STR'] = df_count['L_STR'] + df_count['R_STR']
    df_count['L_BG']  = df_count['L_STR'] + df_count['L_Pall']
    df_count['R_BG']  = df_count['R_STR'] + df_count['R_Pall']
    df_count['BG']  = df_count['R_BG'] + df_count['R_BG']


    # Create Full dataframe
    df = pd.concat([df_dcm, df_count], axis = 1)
    df.to_csv(os.path.join(phenotypic_dir, 'phenotypic_tourettome.csv'))

    df_jac = pd.concat([df_dcm, df_count_jac], axis = 1)
    df_jac.to_csv(os.path.join(phenotypic_dir, 'phenotypic_tourettome_jac.csv'))


#concat_csv(tourettome_subjects, tourettome_workspace, tourettome_phenotypic)


qsm_results_dir = '/scr/sambesi3/workspace/project_iron/results_OCT_26'

def concat_qsm_csv(phenotypic_dir):

    qsm_c = pd.read_csv(os.path.join(qsm_results_dir, 'QSM_median_controls_a.csv'), index_col=0)
    qsm_p = pd.read_csv(os.path.join(qsm_results_dir, 'QSM_median_patients_a.csv'), index_col=0)
    df= pd.concat([qsm_c,qsm_p])

    tour = pd.read_csv('./phenotypic_leipzig.csv', index_col=0, usecols=[0, 1, 2, 3, 4, 5], skiprows=0)
    tour['ID'] = tour.index
    tour = tour.set_index('Name')
    tour.index.name = None

    cols1 = ['Name', 'Group', 'Site', 'Age', 'Sex']
    cols2 = ['R_Caud', 'L_Caud', 'R_Puta', 'L_Puta', 'R_Pall', 'L_Pall',
             'R_Amyg', 'L_Amyg', 'R_Hipp', 'L_Hipp', 'R_Accu', 'L_Accu', 'R_Thal', 'L_Thal',
             'Caud', 'Puta', 'Pall', 'Amyg', 'Hipp', 'Accu', 'Thal',
             'L_RN', 'R_RN', 'L_STN', 'R_STN', 'L_SN', 'R_SN', 'L_DN', 'R_DN',
             'SN', 'STN', 'RN', 'GPe', 'GPi', 'DN', 'MRS_STR']

    df['Name'] = df.index
    df = df.set_index('ID')
    df.index.name = None
    order = cols1 + cols2
    df = df[order]

    df.to_csv(os.path.join(phenotypic_dir, 'phenotypic_leipzig_qsm.csv'))


concat_qsm_csv(tourettome_phenotypic)