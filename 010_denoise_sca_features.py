__author__ = 'kanaan 10.01.2018... re-written 18.10.2018'

import os, sys
import numpy as np
import pandas as pd
import nibabel as nb
import matplotlib
import subprocess
import seaborn as sns
from sklearn import preprocessing
matplotlib.use('agg')
import matplotlib.pyplot as plt
sns.set_style('white')

from variables.subject_list import *
from utilities.utils import mkdir_path
from utilities.check_data import return_ct_data, return_sca_data, return_ecm_data
sys.path.append('/Users/kanaan/SCR/Github/Tourettome/plotting/')
from plotting.cmaps import cmap_gradient

control_outliers = ['HM015', 'LZ061', 'LZ052', 'LZ057', 'LZ058',
                    'HB019', 'HB028',
                    'HM001', 'HM004', 'HM006', 'HM012', 'HM014', 'HM017', 'HM019', 'HM022', 'HM025', 'HM027',
                    'HM028', 'HM029', 'HM030', 'HM032'
                    ]

patient_outliers = ['HA009', 'HB005', 'HM015', 'HM023', 'HM026', 'LZ004', 'LZ006', 'LZ007', 'LZ013', 'LZ017',
                    'LZ018', 'LZ020', 'LZ025', 'LZ027', 'LZ028', 'LZ029', 'LZ030', 'LZ031', 'LZ035', 'LZ038',
                    'PA001', 'PA006', 'PA009', 'PA012', 'PA013', 'PA019', 'PA025', 'PA039', 'PA045', 'PA052',
                    'PA055', 'PA058', 'PA077', 'PA078', 'PA080', 'PA081', 'PA094', 'LZ001',
                    'PA055', 'HB014', 'HB015',
                    'HM002', 'HM003', 'HM005', 'HM007', 'HM008', 'HM009', 'HM010', 'HM011', 'HM020', 'HM024',
                    'HM031', 'HM033'
                    ]

terms = ['Age', 'Sex', 'Group', 'Site', 'qc_func_fd']

def denoise_features(tourettome_dir, feature_name, freesurfer_dir, outliers):

    # SAVE CT pheno dataframe for surfstat
    df_pheno     = pd.read_csv(os.path.join(tourettome_dir,  'phenotypic', 'tourettome_phenotypic.csv'),index_col=0)
    df_pheno= df_pheno.drop(outliers)

    df_pheno = df_pheno.drop([i for i in df_pheno.columns if i not in terms],axis = 1)
    df_pheno.index.names = ['subject']
    df_pheno.to_csv(os.path.join(tourettome_dir,'phenotypic/tourettome_phenotypic_qc.csv'))
    df_pheno = os.path.join(tourettome_dir,  'phenotypic', 'tourettome_phenotypic_qc.csv')

    #df_patients = df_pheno.drop([i for i in df_pheno.index if df_pheno.loc[i]['Group'] == 'controls'])
    #df_controls = df_pheno.drop([i for i in df_pheno.index if df_pheno.loc[i]['Group'] == 'patients'])

    # Regress covarites

    #[features, residuals]=regress_covariates_sca(tourettome_dir, feature_name, freesurfer_dir, phenotypic)

    # os.chdir('/scr/malta1/Github/Tourettome/algorithms/surfstats')
    regress = ['matlab', '-nodesktop', '-nosplash', '-noFigureWindows',
               '-r "regress_covariates_sca(\'%s\', \'%s\', \'%s\', \'%s\') ; quit;"'
               %(tourettome_dir, feature_name, freesurfer_dir, df_pheno )]
    subprocess.call(regress)


fsdir = '/data/pt_nmr093_gts/freesurfer'
denoise_features(tourettome_base, fsdir, 'func_seed_correlation', patient_outliers+control_outliers)