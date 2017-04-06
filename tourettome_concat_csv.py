__author__ = 'kanaan..04.04.2017...@MNI'

import os
import pandas as pd
from variables.subject_list import *

def concat_csv(population, workspace):

    phenotypic_dir       = os.path.join(workspace, 'phenotypic')

    def get_dcm_header(site_id):
        df = pd.read_csv(os.path.join(phenotypic_dir, 'phenotypic_%s.csv'%site_id))
        df = df[['Group', 'Site', 'Age', 'Sex']]
        return df

    df_dcm = pd.concat([get_dcm_header('hannover_a'),
                        get_dcm_header('hannover_b'),
                        get_dcm_header('leipzig'),
                        get_dcm_header('paris') ])
    # Concat Basal Ganglia bin_count dataframes
    df_count = pd.concat([pd.read_csv(os.path.join(workspace, subject, 'ANATOMICAL','seg_first', 'bin_count.csv'))
                          for subject in population], ignore_index = 0)

    for roi in rois_bilateral:
        df_count['%s' %roi]  = df_count['L_%s'%roi] + df_count['R_%s'%roi]


    # Create Full dataframe
    df = pd.concat([df_dcm, df_count], axis = 1)


    df.to_csv(os.path.join(phenotypic_dir, 'phenotypic_tourettome.csv'))






