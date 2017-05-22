__author__ = 'kanaan 23.05.2017'
import os
import numpy as np
import pandas as pd
import json
from variables.subject_list import *
from utilities.utils import *
from quality.motion_statistics import calculate_FD_Power



def prep_meta_ica(population, workspace):

    meta_ica_dir      = mkdir_path(os.path.join(tourettome_workspace, 'META_ICA'))
    meta_ica_list_dir = mkdir_path(os.path.join(meta_ica_dir,'meta_subject_lists'))

    ####################################################
    # Prepare data for meta_ICA
    for subject in population:
        print 'Preparaing %s data for meta ICA' %subject
        # Input/Output
        subject_dir = os.path.join(workspace, subject)
        ica_dir     = mkdir_path(os.path.join(subject_dir, 'ICA'))
        func_2mm    = os.path.join(subject_dir,'REGISTRATION', 'REST_EDIT_UNI_BRAIN_MNI2mm.nii.gz')

        # if not os.path.isfile(os.path.join(ica_dir, 'REST_EDIT_UNI_BRAIN_MNI4mm_n174.nii.gz' )):
        if not os.path.isfile(os.path.join(ica_dir, 'FD_n174.1D' )):
            os.chdir(ica_dir)

            # Resample data to 4mm
            #os.system('flirt -in %s -ref %s -applyisoxfm 4 -nosearch -out REST_EDIT_UNI_BRAIN_MNI4mm'%(func_2mm, mni_brain_2mm))

            # Cut data to shortest time-point length
            ### n_vols: PA=196; LZ=418; HA=271; HB=174
            ### TR: PA=2.4; LZ=1.4; HA=2.0; HA=2.4; HB= 2.0. Average TR=2.05
            #os.system('fslroi REST_EDIT_UNI_BRAIN_MNI4mm REST_EDIT_UNI_BRAIN_MNI4mm_n174 0 174')

            # Calculate FD
            FD = calculate_FD_Power(os.path.join(subject_dir, 'FUNCTIONAL', 'moco/REST_EDIT_moco2.par'))
            FD_n174 = np.loadtxt(FD)[:174]
            np.savetxt('FD_n174.1D', FD_n174)

    ####################################################
    # Identify subjects with FD above 2SD from the mean
    FD_median_dict = {}
    for subject in population:
        FD_median_dict[subject] = np.median(np.loadtxt(os.path.join(workspace, subject, 'ICA/FD_n174.1D')))
    print FD_median_dict

    # remove FD_mean above 1mm
    outlier_above_1mm = [subject for subject in population if FD_median_dict[subject] > 1]

    for subject in outlier_above_1mm:
        print 'Subject %s is an outlier with FD_mean above 1mm' %subject
        del FD_median_dict[subject]

    # define upper bound
    FD_upper_bound =  np.median(FD_median_dict.values()) + np.std(FD_median_dict.values())*2
    # np.percentile(FD_median_dict.values(), 95)#

    # Define subjects above upper bound threshold
    population_qc = [i for i in population if i not in outlier_above_1mm]
    FD_outliers    = [subject for subject in population_qc if FD_median_dict[subject] > FD_upper_bound]
    print FD_outliers

    #save outlier subjects in txt file
    outliers = FD_outliers + outlier_above_1mm

    with open('%s/outliers.json' %meta_ica_dir, 'w') as file:
        file.write(json.dumps(outliers))


    ####################################################
    # Take 10 controls and 10 patients from each site at random.. ie. total sample = 20* 4 = 80

    phenotypic = pd.read_csv(tourettome_phenotypic, index_col = 0).drop([outliers])

    patients = [subject for subject in phenotypic.index if phenotypic.loc[subject]['Group'] == 'patients']
    controls = [subject for subject in phenotypic.index if phenotypic.loc[subject]['Group'] == 'controls']
    meta_lists = {}


    for i in xrange(30):
        PA = list(
            np.random.choice([subject for subject in controls if subject[0:2] == 'PA'], 10, replace=False)) + list(
            np.random.choice([subject for subject in patients if subject[0:2] == 'PA'], 10, replace=False))

        HA = list(
            np.random.choice([subject for subject in controls if subject[0:2] == 'HA'], 10, replace=False)) + list(
            np.random.choice([subject for subject in patients if subject[0:2] == 'HA'], 10, replace=False))

        HB = list(
            np.random.choice([subject for subject in controls if subject[0:2] == 'HB'], 10, replace=False)) + list(
            np.random.choice([subject for subject in patients if subject[0:2] == 'HB'], 10, replace=False))

        LZ = list(
            np.random.choice([subject for subject in controls if subject[0:2] == 'LZ'], 10, replace=False)) + list(
            np.random.choice([subject for subject in patients if subject[0:2] == 'LZ'], 10, replace=False))

        meta_lists['meta_list_%s' % i] = PA + HA + HB + LZ

    print meta_lists


    with open('%s/meta_lists.json'% meta_ica_list_dir, 'w') as file:
        file.write(json.dumps(meta_lists))


prep_meta_ica(tourettome_subjects, tourettome_workspace)
