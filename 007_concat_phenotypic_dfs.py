__author__ = 'kanaan..11.01.2018...@Peel'

import os
import pandas as pd
import numpy as np
from variables.subject_list import *
from utilities.utils import *

# Concatenate dataframes that include (a) DICOM Header, (b) clinical data, (c) quality control metrics.

def concat_dataframes(population, workspace, phenotypic_dir)

    df_dcm =  pd.concat([pd.read_csv(os.path.join(phenotypic_dir, 'phenotypic_leipzig.csv'),index_col =0),
                         #pd.read_csv(os.path.join(phenotypic_dir, 'phenotypic_paris.csv'),index_col =0),
                         #pd.read_csv(os.path.join(phenotypic_dir, 'phenotypic_hannover_a.csv'),index_col =0),
                         #pd.read_csv(os.path.join(phenotypic_dir, 'phenotypic_hannover_b.csv'),index_col =0),
                         #pd.read_csv(os.path.join(phenotypic_dir, 'phenotypic_hamburg.csv'),index_col =0),
                         ])

    df_cln = pd.concat[[pd.read_csv(os.path.join(phenotypic_dir, 'CLINICAL/clinical_leipzig.csv'),index_col =0),


                        ])











import os
import pandas as pd
from variables.subject_list import *

def concat_csvs(population, workspace, phenotypic_dir):

    def get_dcm_header(site_id):
        df = pd.read_csv(os.path.join(phenotypic_dir, 'phenotypic_%s.csv'%site_id), index_col = 0)
        df = df[['Group', 'Site', 'Age', 'Sex']]
        return df

    df_dcm = pd.concat([get_dcm_header('hannover_a'),
                        get_dcm_header('hannover_b'),
                        get_dcm_header('leipzig'),
                        get_dcm_header('hamburg'),
                        get_dcm_header('paris') ]
                       )

    df_qc = [pd.read_csv(os.path.join(workspace,subject, 'QUALITY_CONTROL/quality_paramters.csv'),
                         index_col=0) for subject in population]

    df_pheno = pd.concat([df_dcm, df_qc], axis=1).sort_index()


concat_csvs(tourettome_subjects, tourettome_workspace, tourettome_phenotypic)