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

    subsx = ['HA001', 'HA002', 'HA003', 'HA004', 'HA005', 'HA006', 'HA007', 'HA008', 'HA009', 'HA010', 'HA011', 'HA012',
             'HA013', 'HA014', 'HA015', 'HA016', 'HA017', 'HA018', 'HA019', 'HA020', 'HA021', 'HA022', 'HA023', 'HA024',
             'HA025', 'HA026', 'HA027', 'HA028', 'HA029', 'HA030', 'HA031', 'HA032', 'HA033', 'HA034', 'HA035', 'HA036',
             'HA037', 'HA038', 'HA039', 'HA040', 'HA041', 'HA042', 'HA043', 'HA044', 'HA045', 'HA046', 'HA047', 'HA048',
             'HA049', 'HA050', 'HA051', 'HA052', 'HA053', 'HA054', 'HB001', 'HB002', 'HB003', 'HB006', 'HB011', 'HB012',
             'HB013', 'HB016', 'HB017', 'HB021', 'HB022', 'HB023', 'HB024', 'HB026', 'HB027', 'HB028', 'HB029', 'HB030',
             # 'HM001', 'HM002', 'HM003', 'HM004', 'HM005', 'HM006', 'HM007', 'HM008', 'HM009', 'HM010', 'HM011', 'HM012',
             # 'HM014', 'HM019', 'HM020', 'HM022', 'HM023', 'HM025', 'HM026', 'HM027', 'HM028', 'HM030', 'HM031',
             'LZ004',
             'LZ006', 'LZ007', 'LZ008', 'LZ009', 'LZ010', 'LZ011', 'LZ012', 'LZ013', 'LZ014', 'LZ015', 'LZ016', 'LZ017',
             'LZ018', 'LZ019', 'LZ020', 'LZ021', 'LZ022', 'LZ023', 'LZ024', 'LZ025', 'LZ026', 'LZ027', 'LZ028', 'LZ029',
             'LZ030', 'LZ031', 'LZ032', 'LZ033', 'LZ034', 'LZ035', 'LZ036', 'LZ037', 'LZ038', 'LZ039', 'LZ041', 'LZ042',
             'LZ043', 'LZ045', 'LZ046', 'LZ047', 'LZ048', 'LZ049', 'LZ051', 'LZ055', 'LZ056', 'LZ060', 'LZ061', 'LZ062',
             'LZ063', 'LZ064', 'LZ065', 'LZ066', 'LZ067', 'LZ068', 'LZ069', 'LZ070', 'LZ071', 'LZ072', 'LZ073', 'LZ074',
             'LZ075', 'PA001', 'PA002', 'PA003', 'PA004', 'PA005', 'PA006', 'PA007', 'PA008', 'PA009', 'PA010', 'PA011',
             'PA012', 'PA013', 'PA014', 'PA016', 'PA017', 'PA018', 'PA019', 'PA021', 'PA022', 'PA026', 'PA027', 'PA028',
             'PA031', 'PA032', 'PA033', 'PA035', 'PA037', 'PA038', 'PA042', 'PA043', 'PA047', 'PA048', 'PA050', 'PA052',
             'PA056', 'PA058', 'PA062', 'PA063', 'PA064', 'PA066', 'PA067', 'PA068', 'PA069', 'PA070', 'PA071', 'PA072',
             'PA073', 'PA074', 'PA075', 'PA076', 'PA077', 'PA078', 'PA079', 'PA080', 'PA081', 'PA082', 'PA083', 'PA084',
             'PA085', 'PA087', 'PA089', 'PA090', 'PA091', 'PA092', 'PA093', 'PA095', 'PA096']

    design_columns = ['Group', 'Age', 'Sex', 'Site', 'qc_func_fd']
    df_design = df_pheno.drop([i for i in df_pheno.columns if i not in design_columns], axis=1)

    tourettome_outliers = [i for i in df_pheno.index if i not in subsx]

    print 'dropping outliers=', tourettome_outliers
    df_design.drop(tourettome_outliers)
    df_design.to_csv(os.path.join(phenotypic_dir, 'tourettome_phenotypic_designx.csv'))


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
