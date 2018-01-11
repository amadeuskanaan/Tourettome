__author__ = 'kanaan 10.01.2018'


import os
import numpy as np
import pandas as pd
import nibabel as nb
from variables import *
from utilities.utils import mkdir_path


def construct_features_dataframe(population, workspace_dir, derivatives_dir, freesufer_dir):

    print '========================================================================================'
    print ''
    print '                    Tourettome - 009. Heirarchical Clustering                           '
    print ''
    print '========================================================================================'

        # Create feature dataframe

        # structural - cortical thickness             - 20484 vertices
        # structural - subcortical volume             - 16    ROIS

        # functional - seed-correlation - STR3_MOTOR  - 20484 vertices
        # functional - seed-correlation - STR3_LIMBIC - 20484 vertices
        # functional - seed-correlation - STR3_EXEC   - 20484 vertices
        # functional - seed-correlation - HIPP        - 20484 vertices
        # functional - seed-correlation - AMYG        - 20484 vertices

        # other
        # functional - seed-correlation - aINSULA     - 20484 vertices
        # functional - seed-correlation - ACC         - 20484 vertices
        # functional - seed-correlation - PCC         - 20484 vertices
        # functional - seed-correlation - M1          - 20484 vertices


    for subject in population:
        ct_lh = nb.load(os.path.join(datadir, 'struct_cortical_thickness',
                                     '%s_ct2fsaverage5_fwhm20_lh.mgh' % subject)).get_data().ravel()
        ct_rh = nb.load(os.path.join(datadir, 'struct_cortical_thickness',
                                     '%s_ct2fsaverage5_fwhm20_rh.mgh' % subject)).get_data().ravel()

        if scale:
            ct_lh = preprocessing.scale(ct_lh)
            ct_rh = preprocessing.scale(ct_rh)
        else:
            pass
        df_ct_lh = pd.DataFrame(ct_lh, columns=[subject], index=['ct_lh_' + str(i) for i in range(ct_lh.shape[0])])
        df_ct_rh = pd.DataFrame(ct_rh, columns=[subject], index=['ct_rh_' + str(i) for i in range(ct_rh.shape[0])])

        df_subvol = pd.read_csv(os.path.join(datadir, 'struct_subcortical_volume', '%s_aseg_stats.txt' % subject),
                                index_col=0)
        df_subvol = df_subvol.drop([i for i in df_subvol.columns if i not in nuclei_subcortical], axis=1)
        df_subvol = pd.DataFrame(scale(df_subvol.T), index=df_subvol.columns, columns=[subject])

        df_features.append(pd.concat([df_ct_lh, df_ct_rh  # , df_subvol
                                      ], axis=0))

