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
    df_count = pd.concat([pd.read_csv(os.path.join(workspace, subject, 'ANATOMICAL','seg_first', 'bin_count.csv'), index_col = 0)
                          for subject in population], ignore_index = False)

    for roi in rois_bilateral:
        df_count['%s' %roi]  = df_count['L_%s'%roi] + df_count['R_%s'%roi]




    # Create Full dataframe
    df = pd.concat([df_dcm, df_count])


    #df_count.to_csv(os.path.join(phenotypic_dir, 'tmp_count.csv'))
    #df_dcm.to_csv(os.path.join(phenotypic_dir, 'tmp_dcm.csv'))


concat_csv(tourettome_subjects, tourettome_workspace, tourettome_phenotypic)




