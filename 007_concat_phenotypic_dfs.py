__author__ = 'kanaan..11.01.2018...@Peel'

import os
import pandas as pd
import numpy as np
from variables.subject_list import *
from variables.subject_list_original import LEIPZIG_A_subject_dict, PARIS_subject_dict, HANNOVER_B_subject_dictx , HANNOVER_A_subject_dict
from variables.clinical_standardization import *
from utilities.utils import *

# Concatenate dataframes that include (a) DICOM Header, (b) clinical data, (c) quality control metrics.

def concat_dataframes(population, workspace_dir, phenotypic_dir):

    print '######################################'
    print '1. Concatenating dcm,cln,qc dataframes'

    #############################################################################################################
    # Clinical Leipzig

    cln_orig_dir     = os.path.join(phenotypic_dir, 'df_cln/df_cln_original')

    # read data
    leipzig_patients = pd.read_csv((os.path.join(cln_orig_dir, 'orig_leipzig_clinical_patients.csv')),index_col=0)
    leipzig_controls = pd.read_csv((os.path.join(cln_orig_dir, 'orig_leipzig_clinical_controls.csv')),index_col=0)
    df_leipzig_dcm   = pd.read_csv(os.path.join(phenotypic_dir, 'df_dcm/dicomhdr_leipzig.csv'), index_col=0)

    # Add group identifier. just for sanity check
    leipzig_patients['group_id'] = 'patients'
    leipzig_controls['group_id'] = 'controls'

    # concat control and patient dataframes
    df_leipzig = pd.concat([leipzig_controls, leipzig_patients])

    # drop useless columns-
    df_leipzig = df_leipzig.drop([c for c in df_leipzig.columns if c not in leipzig_columns_dict.keys()], axis=1)
    df_leipzig = df_leipzig.rename(columns=leipzig_columns_dict)

    # rename index to anonamized subject_ids
    # df_leipzig['Name'] = df_leipzig.index
    df_leipzig = df_leipzig.rename(index=LEIPZIG_A_subject_dict).sort_index()

    # drop subjects with no resting data
    drop_leipzig = [i for i in df_leipzig.index if not i[0:2] == 'LZ']
    df_leipzig = df_leipzig.drop(drop_leipzig, axis=0)

    # concat dicom header and clinical dfs
    df_leipzig = pd.concat([df_leipzig, df_leipzig_dcm], axis=1)
    df_leipzig = df_leipzig.sort_index(axis=1)

    # add diangosis info

    for subject in df_leipzig.index:
        adhd = df_leipzig.loc[subject]['diagnosis_adhd']
        ocd = df_leipzig.loc[subject]['diagnosis_ocd']
        if ocd == 1 and adhd == 1:
            df_leipzig.loc[subject, 'diagnosis'] = 'GTS_OCD_ADHD'
        elif ocd == 1 and adhd == 0:
            df_leipzig.loc[subject, 'diagnosis'] = 'GTS_OCD'
        elif ocd == 0 and adhd == 1:
            df_leipzig.loc[subject, 'diagnosis'] = 'GTS_ADHD'
        elif ocd == 0 and adhd == 0:
            df_leipzig.loc[subject, 'diagnosis'] = 'GTS'
        else:
            df_leipzig.loc[subject, 'diagnosis'] = 'Healthy_Control'

    #############################################################################################################
    # Clinical Hamburg

    # load clinical and dicom header dfs
    df_hamburg = pd.read_csv((os.path.join(cln_orig_dir, 'orig_hamburg_clinical.csv')), index_col=0)
    df_hamburg_dcm = pd.read_csv(os.path.join(phenotypic_dir, 'df_dcm/dicomhdr_hamburg.csv'), index_col=0)

    # drop useless columns  and rename hamburg columns
    df_hamburg = df_hamburg.drop([c for c in df_hamburg.columns if c not in hamburg_columns_dict.keys()], axis=1)
    df_hamburg = df_hamburg.rename(columns=hamburg_columns_dict)

    # concat dicom header and clinical dfs
    df_hamburg = pd.concat([df_hamburg, df_hamburg_dcm], axis=1)
    df_hamburg = df_hamburg.sort_index(axis=1)

    # Add diangosis info
    for subject in df_hamburg.index:
        if df_hamburg.loc[subject]['group_id'] == 'patients':
            df_hamburg.loc[subject, 'diagnosis'] = 'GTS'
        else:
            df_hamburg.loc[subject, 'diagnosis'] = 'Healthy_control'

    df_hamburg['Sex'] = df_hamburg['Sex'].map({'M': 'male', 'F': 'female'})


    #############################################################################################################
    # Clinical Hannover_B

    # # load dataframes
    hannover_b_controls = pd.read_csv((os.path.join(cln_orig_dir, 'orig_hannover_b_clinical_controls.csv')), index_col=0)
    hannover_b_patients = pd.read_csv((os.path.join(cln_orig_dir, 'orig_hannover_b_clinical_patients.csv')), index_col=0)
    df_hannover_b_dcm = pd.read_csv(os.path.join(phenotypic_dir, 'df_dcm/dicomhdr_hannover_b.csv'), index_col=0)

    # Add group identifier. just for sanity check
    hannover_b_controls['group_id'] = 'controls'
    hannover_b_patients['group_id'] = 'patients'

    # concat dataframes, drop useless columns and rename columns to same formatting
    df_hannover_b = pd.concat([hannover_b_controls, hannover_b_patients])
    df_hannover_b = df_hannover_b.drop([c for c in df_hannover_b.columns if c not in hannover_b_columns_dict.keys()],axis=1)
    df_hannover_b = df_hannover_b.rename(columns=hannover_b_columns_dict)

    # Drop patients with two scans
    drop_hb_patients = [i for i in df_hannover_b.index if i[-1] == 'B']
    df_hannover_b = df_hannover_b.drop(drop_hb_patients)

    # rename index to anonamized subject_ids
    # df_hannover_b['Name'] = df_hannover_b.index
    df_hannover_b = df_hannover_b.rename(index=HANNOVER_B_subject_dictx).sort_index()

    # concat dicom header and clinical dfs
    df_hannover_b = pd.concat([df_hannover_b, df_hannover_b_dcm], axis=1)
    df_hannover_b = df_hannover_b.sort_index(axis=1)

    # drop subjects without MRI data
    drop_hb = [i for i in df_hannover_b.index if not i[0:2] == 'HB']
    df_hannover_b = df_hannover_b.drop(drop_hb, axis=0)

    #############################################################################################################
    # Hannover_A
    df_hannover_a_dcm = pd.read_csv(os.path.join(phenotypic_dir, 'df_dcm/dicomhdr_hannover_a.csv'), index_col=0)

    #############################################################################################################
    # Paris
    df_paris_dcm = pd.read_csv(os.path.join(phenotypic_dir, 'df_dcm/dicomhdr_paris.csv'), index_col=0)



    #############################################################################################################
    # Concat clinical+dcm
    df_cln_dcm = pd.concat([df_hamburg, df_leipzig, df_hannover_b, df_hannover_a_dcm, df_paris_dcm])

    # concat  df_cln_dcm with df_qc
    df_qc = pd.concat([pd.read_csv(os.path.join(workspace_dir, subject, 'QUALITY_CONTROL/quality_paramters.csv'),
                         index_col = 0) for subject in df_cln_dcm.index if os.path.isfile(
                       os.path.join(workspace_dir, subject, 'QUALITY_CONTROL/quality_paramters.csv'))])

    df_pheno = pd.concat([df_cln_dcm, df_qc], axis = 1)
    df_pheno.to_csv(os.path.join(phenotypic_dir, 'tourettome_phenotypic.csv'))

    print df_pheno

concat_dataframes(tourettome_subjects, tourettome_workspace, tourettome_phenotypic)
