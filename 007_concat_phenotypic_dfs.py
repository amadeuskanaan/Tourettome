__author__ = 'kanaan..11.01.2018...@Peel'

import os
import pandas as pd
import numpy as np
from variables.subject_list import *
from utilities.utils import *

# Concatenate dataframes that include (a) DICOM Header, (b) clinical data, (c) quality control metrics.

def concat_dataframes(population, workspace_dir, phenotypic_dir):

    print '####################################################################'
    print '1. Concatenating img_header, clinical and quality control dataframes'

    df_dcm =  pd.concat([pd.read_csv(os.path.join(phenotypic_dir, 'df_dcm/dicomhdr_leipzig.csv'),index_col =0),
                         pd.read_csv(os.path.join(phenotypic_dir, 'df_dcm/dicomhdr_paris.csv'),index_col =0),
                         pd.read_csv(os.path.join(phenotypic_dir, 'df_dcm/dicomhdr_hannover_a.csv'),index_col =0),
                         pd.read_csv(os.path.join(phenotypic_dir, 'df_dcm/dicomhdr_hannover_b.csv'),index_col =0),
                         pd.read_csv(os.path.join(phenotypic_dir, 'df_dcm/dicomhdr_hamburg.csv'),index_col =0),
                         ])

    df_cln = pd.concat([pd.read_csv(os.path.join(phenotypic_dir, 'df_cln/clinical_leipzig.csv'),index_col =0),
                        # pd.read_csv(os.path.join(phenotypic_dir, 'df_cln/clinical_paris.csv'), index_col=0)
                        # pd.read_csv(os.path.join(phenotypic_dir, 'df_cln/clinical_hannover_a.csv'), index_col=0)
                        # pd.read_csv(os.path.join(phenotypic_dir, 'df_cln/clinical_hannover_b.csv'), index_col=0)
                        # pd.read_csv(os.path.join(phenotypic_dir, 'df_cln/clinical_hamburg.csv'), index_col=0)
                        ])

    df_qc = pd.concat([pd.read_csv(os.path.join(workspace_dir, subject, 'QUALITY_CONTROL/quality_paramters.csv'),
                         index_col = 0) for subject in df_dcm.index if os.path.isfile(
                       os.path.join(workspace_dir, subject, 'QUALITY_CONTROL/quality_paramters.csv'))])

    df_pheno = pd.concat([df_dcm, df_qc, df_cln], axis=1).sort_index()
    df_pheno.to_csv(os.path.join(phenotypic_dir, 'tourettome_phenotypic.csv'))

    print '####################################################################'
    print '1. Create design matrix dataframe for surfstat'

    columns = ['Group', 'Age', 'Gender', 'Site', 'qc_func_fd']
    df_design = df_pheno.drop([i for i in df_pheno.columns if i not in columns], axis=1)

    tourettome_outliers = []
    df_design.drop(outiers,axis =0)
    df_pheno.to_csv(os.path.join(phenotypic_dir, 'tourettome_phenotypic_design.csv'))



concat_dataframes(tourettome_subjects, tourettome_workspace, tourettome_phenotypic)


# import os
# import pandas as pd
# from variables.subject_list import *
#
# def concat_csvs(population, workspace, phenotypic_dir):
#
#     def get_dcm_header(site_id):
#         df = pd.read_csv(os.path.join(phenotypic_dir, 'phenotypic_%s.csv'%site_id), index_col = 0)
#         df = df[['Group', 'Site', 'Age', 'Sex']]
#         return df
#
#     df_dcm = pd.concat([get_dcm_header('hannover_a'),
#                         get_dcm_header('hannover_b'),
#                         get_dcm_header('leipzig'),
#                         get_dcm_header('hamburg'),
#                         get_dcm_header('paris') ]
#                        )
#
#     df_qc = [pd.read_csv(os.path.join(workspace,subject, 'QUALITY_CONTROL/quality_paramters.csv'),
#                          index_col=0) for subject in population]
#
#     df_pheno = pd.concat([df_dcm, df_qc], axis=1).sort_index()
#
#
