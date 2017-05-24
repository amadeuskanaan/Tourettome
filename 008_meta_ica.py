__author__ = 'kanaan 23.05.2017'
import os
import numpy as np
import pandas as pd
import json
import multiprocessing
from variables.subject_list import *
from utilities.utils import *
from quality.motion_statistics import calculate_FD_Power



def make_meta_ica(population, workspace):

    meta_ica_dir      = mkdir_path(os.path.join(workspace,   'META_ICA'))
    meta_ica_list_dir = mkdir_path(os.path.join(meta_ica_dir,'meta_subject_lists'))

    ####################################################################################################################
    # Prepare data for meta_ICA
    ####################################################################################################################

    for subject in population:
        print 'Preparaing %s data for meta ICA' %subject
        # Input/Output
        subject_dir = os.path.join(workspace, subject)
        ica_dir     = mkdir_path(os.path.join(subject_dir, 'ICA'))
        func_2mm    = os.path.join(subject_dir,'REGISTRATION', 'REST_EDIT_UNI_BRAIN_MNI2mm.nii.gz')

        if not os.path.isfile(os.path.join(ica_dir, 'REST_EDIT_UNI_BRAIN_MNI4mm_n174.nii.gz' )):
        #if not os.path.isfile(os.path.join(ica_dir, 'FD_n174.1D' )):
            os.chdir(ica_dir)

            # Resample data to 4mm
            os.system('flirt -in %s -ref %s -applyisoxfm 4 -nosearch -out REST_EDIT_UNI_BRAIN_MNI4mm'
                      %(func_2mm, mni_brain_2mm))

            # Cut data to shortest time-point length
            ### n_vols: PA=196; LZ=418; HA=271; HB=174
            os.system('fslroi REST_EDIT_UNI_BRAIN_MNI4mm XXX 0 174')
            os.system('fslmaths XXX -nan REST_EDIT_UNI_BRAIN_MNI4mm_n174')
            os.system('rm -rf XXX*')

            # Calculate FD
            FD = calculate_FD_Power(os.path.join(subject_dir, 'FUNCTIONAL', 'moco/REST_EDIT_moco2.par'))
            FD_n174 = np.loadtxt(FD)[:174]
            np.savetxt('FD_n174.1D', FD_n174)

    ####################################################################################################################
    # Identify subjects with FD above 2SD from the mean
    ####################################################################################################################

    if not os.path.isfile('%s/outliers.json' %meta_ica_dir):

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
        ### np.percentile(FD_median_dict.values(), 95)

        # Define subjects above upper bound threshold
        population_qc = [i for i in population if i not in outlier_above_1mm]
        FD_outliers    = [subject for subject in population_qc if FD_median_dict[subject] > FD_upper_bound]
        print FD_outliers

        #save outlier subjects in txt file
        outliers = FD_outliers + outlier_above_1mm

        with open('%s/outliers.json' %meta_ica_dir, 'w') as file:
            file.write(json.dumps(outliers))

    ####################################################################################################################
    # Create 30 random Lists of an equal number of controls/patients for each site
    ####################################################################################################################

    # Take 10 controls and 10 patients from each site at random..
    # ie. total sample = 20* 4 = 80 subjects times 30 lists
    if not os.path.isfile('%s/meta_lists.json'% meta_ica_list_dir):
        phenotypic = pd.read_csv(os.path.join(tourettome_phenotypic, 'phenotypic_tourettome.csv'),
                                 index_col = 0).drop(outliers)

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

            meta_lists['meta_list_%s' % i] = PA + HA + LZ #+ HB

        print meta_lists

        with open('%s/meta_lists.json'% meta_ica_list_dir, 'w') as file:
            file.write(json.dumps(meta_lists))


    ####################################################################################################################
    # Run melodic on the 30 randomized lists
    ####################################################################################################################

    meta_ica_dir      = mkdir_path(os.path.join(tourettome_workspace,   'META_ICA'))
    meta_ica_list_dir = mkdir_path(os.path.join(meta_ica_dir,'meta_subject_lists'))

    ### TR: PA=2.4; LZ=1.4; HA=2.0; HA=2.4; HB= 2.0. Average TR=2.05
    TR_mean = (2.4 + 2.4 + 2.0 + 1.4) / 4.
    TR_mean = (2.4 + 2.4 + 1.4) / 3.

    # create brain mask
    os.system('flirt -in %s -ref %s -applyisoxfm 4 -nosearch -out %s/MNI152_T1_4mm_brain_mask'
              % (mni_brain_2mm_mask, mni_brain_2mm_mask, meta_ica_dir))
    os.system('fslmaths %s/MNI152_T1_4mm_brain_mask -thr 0.5 -bin %s/MNI152_T1_4mm_brain_mask_bin'
              %(meta_ica_dir,meta_ica_dir))
    brain_mask_4mm = os.path.join(meta_ica_dir, 'MNI152_T1_4mm_brain_mask_bin.nii.gz')

    # load sub lists
    meta_lists = json.load(open('%s/meta_lists.json'% meta_ica_list_dir))

    #def run_melodic_multi_processing(i):
    for i in xrange(30):

        if not os.path.isfile(os.path.join(os.path.join(meta_ica_dir, 'ICA_%s'%i, 'melodic_IC.nii.gz'))):
            print 'Running Melodic Number %s' %i

            func_list = [os.path.join(tourettome_workspace, subject, 'ICA/REST_EDIT_UNI_BRAIN_MNI4mm_n174.nii.gz')
                         for subject in meta_lists['meta_list_%s' %i]
                         if os.path.isfile(os.path.join(tourettome_workspace, subject, 'ICA/REST_EDIT_UNI_BRAIN_MNI4mm_n174.nii.gz'))]

            #fun_list_file = open('%s/list_%s.txt' %(meta_ica_list_dir, i), 'w')
            #fun_list_file.write(func_list)

            input_file = os.path.join(meta_ica_list_dir, 'input_list_%s.txt' %(i))
            with open(input_file, 'w') as file:
                for func in func_list:
                    file.write(func + '\n')
            #print input_file

            melodic_run_dir = mkdir_path(os.path.join(meta_ica_dir, 'ICA_%s'%i))

            os.system(' '.join(['melodic',
                                '--in=' + input_file,#'%s/list_%s.txt' %(meta_ica_list_dir, i),
                                '--mask=' + brain_mask_4mm,
                                '-v',
                                '--outdir=' + melodic_run_dir,
                                '--report',
                                '--tr=' + str(TR_mean)])
                                # '--Ostats --nobet --mmthresh=0.5
                                # '-d 30',
                                )


    # to iterate 30 icas on multiple cores
    # if __name__ == "__main__":
    #     # Parallelize MELODIC runs on 26 cores
    #     number_processes = 26
    #     tasks_iterable   = range(30)
    #     pool             = multiprocessing.Pool(number_processes)
    #     pool.map_async(run_melodic_multi_processing, tasks_iterable)
    #     pool.close()
    #     pool.join()

    ####################################################################################################################
    # Run META ICA
    ####################################################################################################################

    melodic_ICs = [os.path.join(meta_ica_dir, 'ICA_%s'%i, 'melodic_IC.nii.gz') for i in xrange(30)]

    #Merge all melodic runs
    os.system('fslmerge -t %s/melodic_IC_all.nii.gz %s' %(meta_ica_dir, ' '.join(melodic_ICs)))

    # run meta ica
    ica_run_dir_all = mkdir_path(os.path.join(workspace, 'META_ICA/ICA_merged'))
    os.system(' '.join(['melodic',
                        '--in=' + os.path.join(meta_ica_dir, 'melodic_IC_all.nii.gz'),
                        '--mask=' + brain_mask_4mm,
                        '-v',
                        '--outdir=' + ica_run_dir_all,
                        '--Ostats --nobet --mmthresh=0.5 --report',
                        '--tr=' + str(TR_mean)]))

    ####################################################################################################################
    # Run Dual Regression to extract spatial maps from each subject
    ####################################################################################################################
    #
    # print 'Running dual Regression'
    #
    # dualreg_dir = mkdir_path(os.path.join(workspace, 'META_ICA', 'DUAL_REGRESSION'))
    # os.chdir(dualreg_dir)
    #
    # # Create a Design Matrix  ... same as Glm_gui
    # mat = open('design.mat', 'w')
    # mat.write('/NumWaves\t1\n')
    # mat.write('/NumPoints\t221\n')
    # mat.write('/PPheights\t\t1.000000e+00\n')
    # mat.write('/Matrix\n')
    # for i in xrange(221):
    #     mat.write('1.000000e+00\n')
    # mat.close()
    #
    # con = open('design.con','w')
    # con.write('/ContrastName1\tgroup mean\n')
    # con.write('/NumWaves\t1\n')
    # con.write('/NumContrasts\t1\n')
    # con.write('/PPheights\t\t1.000000e+00\n')
    # con.write('/RequiredEffect\t\t3.121\n')
    # con.write('\n')
    # con.write('/Matrix\n')
    # con.write('1.000000e+00')
    # con.close()
    #
    # pproc_list = [os.path.join(workspace, subject, 'ICA/REST_EDIT_UNI_BRAIN_MNI4mm_n174.nii.gz') for subject in leipzig + hannover_a + paris]
    # print len(pproc_list)
    #
    # meta_ica  = os.path.join(workspace, 'META_ICA', 'ICA_merged', 'melodic_IC.nii.gz')
    #
    # # dual_regression <group_IC_maps> <des_norm> <design.mat> <design.con> <n_perm> <output_directory> <input1> <input2> <input3> .........
    #
    # os.system(' '.join(['dual_regression ',
    #                     meta_ica,     # <group_IC_maps>
    #                     '1',          # <des_norm> 0 or 1 (1 is recommended). Whether to variance-normalise the timecourses used as the stage-2 regressors
    #                     'design.mat', # <design.mat> Design matrix for final cross-subject modelling with randomise
    #                     'design.con', # <design.con> Design contrasts for final cross-subject modelling with randomise
    #                     '500',        # <n_perm>
    #                     dualreg_dir,
    #                     ' '.join(pproc_list)]
    #                    ))

make_meta_ica(tourettome_subjects, tourettome_workspace)


def make_slices_dir(population, workspace):
    for subject in population:
        print subject
        slices_dir = mkdir_path(os.path.join(workspace, 'META_ICA/slices_dir'))
        os.chdir(slices_dir)
        func = os.path.join(tourettome_workspace, subject, 'ICA/REST_EDIT_UNI_BRAIN_MNI4mm_n174.nii.gz')
        #os.system('fslmaths %s -Tmean mean_%s' %(func, subject))
        os.system('fslmaths %s -Tstd std_%s' %(func, subject))

#make_slices_dir(tourettome_subjects, tourettome_workspace)

