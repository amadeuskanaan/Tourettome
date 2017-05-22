__author__ = 'kanaan 23.05.2017'
import os
import numpy as np
from variables.subject_list import *
from utilities.utils import *
from quality.motion_statistics import calculate_FD_Power





def prep_meta_ica(population, workspace):


    # Prepare data for meta_ICA
    for subject in population:
        print 'Preparaing %s data for meta ICA' %subject
        # Input/Output
        subject_dir = os.path.join(workspace, subject)
        ica_dir     = mkdir_path(os.path.join(subject_dir, 'ICA'))
        func_2mm    = os.path.join(subject_dir,'REGISTRATION', 'REST_EDIT_UNI_BRAIN_MNI2mm.nii.gz')

        if not os.path.isfile(os.path.join(ica_dir, 'REST_EDIT_UNI_BRAIN_MNI4mm_n174.nii.gz' )):
            os.chdir(ica_dir)

            # Resample data to 4mm
            #os.system('flirt -in %s -ref %s -applyisoxfm 4 -nosearch -out REST_EDIT_UNI_BRAIN_MNI4mm'%(func_2mm, mni_brain_2mm))

            # Cut data to shortest time-point length
            ### n_vols: PA=196; LZ=418; HA=271; HB=174
            ### TR: PA=2.4; LZ=1.4; HA=2.0; HA=2.4; HB= 2.0. Average TR=2.05
            #os.system('fslroi REST_EDIT_UNI_BRAIN_MNI4mm REST_EDIT_UNI_BRAIN_MNI4mm_n174 0 174')

            # Calculate FD
            FD = calculate_FD_Power(os.path.join(subject_dir, 'FUNCTIONAL', 'moco/REST_EDIT_moco2.par'))


    # Identify subjects with FD above 2SD from the mean
    FD_median_dict = {}
    for subject in population:
        FD_median_dict[subject] = np.median(np.loadtxt(os.path.join(workspace, subject, 'ICA/FD.1D')))

    print FD_median_dict

    outlier_above_1mm = [subject for subject in population if FD_median_dict[subject] > 1]

    for subject in outlier_above_1mm:
        print 'outlier above 1mm', subject
        del FD_median_dict[subject]

    FD_upper_bound =  np.median(FD_median_dict.values()) + np.std(FD_median_dict.values())*2
    # np.percentile(FD_median_dict.values(), 95)#

    FD_outliers    = [subject for subject in population if FD_median_dict[subject] > FD_upper_bound and FD_median_dict > 1]
    print FD_outliers


prep_meta_ica(tourettome_subjects, tourettome_workspace)






