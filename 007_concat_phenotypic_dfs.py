__author__ = 'kanaan..11.01.2018...@Peel'

import os
import pandas as pd
import numpy as np
from variables.subject_list import *
from utilities.utils import *

# Concatenate dataframes that include (a) DICOM Header, (b) clinical data, (c) quality control metrics.

def concat_dataframes(population, workspace_dir, phenotypic_dir):

    print '######################################'
    print '1. Concatenating dcm,cln,qc dataframes'

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

    print '##############################################'
    print '2. Create design matrix dataframe for surfstat'

    xoutliers =  ['HB004', 'HB005', 'HB007', 'HB008', 'HB009', 'HB010', 'HB014', 'HB015', 'HB018', 'HB019', 'HB020',
             'HB025', 'HB031', 'HB032', 'HB033', 'HM001', 'HM002', 'HM003', 'HM004', 'HM005', 'HM006', 'HM007',
             'HM008', 'HM009', 'HM010', 'HM011', 'HM012', 'HM014', 'HM015', 'HM017', 'HM019', 'HM020', 'HM022',
             'HM023', 'HM024', 'HM025', 'HM026', 'HM027', 'HM028', 'HM029', 'HM030', 'HM031', 'HM032', 'HM033',
             'LZ001', 'LZ002', 'LZ003', 'LZ005', 'LZ040', 'LZ044', 'LZ050', 'LZ052', 'LZ053', 'LZ054', 'LZ057',
             'LZ058', 'LZ059', 'LZ076', 'PA015', 'PA020', 'PA023', 'PA024', 'PA025', 'PA029', 'PA030', 'PA036',
             'PA039', 'PA040', 'PA041', 'PA044', 'PA045', 'PA046', 'PA049', 'PA051', 'PA053', 'PA054', 'PA055',
             'PA059', 'PA060', 'PA061', 'PA088', 'PA094']

    design_columns = ['Group', 'Age', 'Sex', 'Site', 'qc_func_fd']
    df_design = df_pheno.drop([i for i in df_pheno.columns if i not in design_columns], axis=1)

    print 'dropping outliers=', tourettome_outliers
    df_design.drop(xoutliers, index=0)
    df_design.to_csv(os.path.join(phenotypic_dir, 'tourettome_phenotypic_design.csv'))

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
