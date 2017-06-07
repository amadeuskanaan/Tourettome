__author__ = 'kanaan 23.05.2017'
import os
import numpy as np
import pandas as pd
import json
import multiprocessing
from variables.subject_list import *
from utilities.utils import *
from quality.motion_statistics import calculate_FD_Power
import nibabel as nb


def meta_decompsition_pproc(population, workspace):

    workspace_dir = mkdir_path(os.path.join(workspace, 'META_DECOMPOSITION'))
    lists_dir     = mkdir_path(os.path.join(workspace_dir, 'subject_lists'))

    ####################################################################################################################
    # Prepare data for meta_ICA
    ####################################################################################################################

    for subject in population:
        print 'Preparaing %s data for meta ICA' % subject

        # Input/Output
        subject_dir = os.path.join(workspace, subject)
        ica_dir = mkdir_path(os.path.join(subject_dir, 'ICA'))
        func_2mm = os.path.join(subject_dir, 'REGISTRATION', 'REST_EDIT_UNI_BRAIN_MNI2mm.nii.gz')
        # fun_2mm -> slice time correction, drop 4 TRs, RPI, BET, Intensity Normalization

        if not os.path.isfile(os.path.join(ica_dir, 'REST_EDIT_UNI_BRAIN_MNI4mm_n196_fwhm_hp.nii.gz')):
            os.chdir(ica_dir)

            # Cut data to shortest time-point length
            ### n_vols: PA=196; LZ=418; HA=271; HB=174-.... Dataset HB will not be used
            os.system('fslroi %s REST_EDIT_UNI_BRAIN_MNI2mm_n196_nan 0 196' % func_2mm)
            os.system('fslmaths REST_EDIT_UNI_BRAIN_MNI2mm_n196_nan -nan REST_EDIT_UNI_BRAIN_MNI2mm_n196')

            # Calculate FD for new length
            FD = calculate_FD_Power(os.path.join(subject_dir, 'FUNCTIONAL', 'moco/REST_EDIT_moco2.par'))
            FD_n = np.loadtxt(FD)[:196]
            np.savetxt('FD_n196.1D', FD_n)

            # Smoothing FWHM 6mm
            FWHM = 6.
            sigma = FWHM / 2.35482004503
            os.system('fslmaths REST_EDIT_UNI_BRAIN_MNI2mm_n196 -s %s REST_EDIT_UNI_BRAIN_MNI2mm_n196_fwhm' % (sigma))

            # High pass Temporal Filtering (100s)
            if subject[0:2] == 'LZ':
                TR = 1.4
            elif subject[0:2] == 'PA':
                TR = 2.4
            elif subject[0:2] == 'HA':
                TR = 2.4

            highpass_cutoff = 0.01  # hz
            highpass_sigma = 1. / (2. * TR * highpass_cutoff)
            os.system(
                'fslmaths REST_EDIT_UNI_BRAIN_MNI2mm_n196_fwhm -bptf %s -1.0 REST_EDIT_UNI_BRAIN_MNI2mm_n196_fwhm_hp'
                % highpass_sigma)

            # Resample data to 4mm
            os.system('flirt -in REST_EDIT_UNI_BRAIN_MNI2mm_n196_fwhm_hp -ref %s -applyisoxfm 4 -nosearch '
                      '-out REST_EDIT_UNI_BRAIN_MNI4mm_n196_fwhm_hp' % (mni_brain_2mm))

            # Clean folder
            os.system('rm -rf *2mm*')

    ####################################################################################################################
    # Detect outliers
    ####################################################################################################################

    if not os.path.isfile('%s/outliers.json' % workspace_dir):

        print 'Detecting Motion Outliers'

        FD_median_dict = {}
        FD_max_dict = {}
        for subject in population:
            FD_median_dict[subject] = np.median(np.loadtxt(os.path.join(workspace, subject, 'ICA/FD_n196.1D')))
            FD_max_dict[subject] = np.max(np.loadtxt(os.path.join(workspace, subject, 'ICA/FD_n196.1D')))

        #print 'FD_median', FD_median_dict
        #print 'FD_max', FD_max_dict

        # Remove subjects with FD_mean above 1mm and FD_max above 3mm
        fd_mean_outliers = [subject for subject in population if FD_median_dict[subject] > 1.]
        fd_max_outliers = [subject for subject in population if FD_max_dict[subject] > 4.]

        for subject in fd_mean_outliers:
            print 'Subject %s is an outlier with FD_mean above 1mm' % subject
            del FD_median_dict[subject]

        for subject in fd_max_outliers:
            print 'Subject %s is an outlier with FD_max above 4mm' % subject
            del FD_max_dict[subject]

        # define upper bound
        FD_upper_bound = np.median(FD_median_dict.values()) + np.std(FD_median_dict.values()) * 2
        ### np.percentile(FD_median_dict.values(), 95)

        # Define subjects above upper bound threshold
        population_qc = [i for i in population
                         if i not in fd_mean_outliers or i not in fd_max_outliers]
        fd_std_outliers = [subject for subject in population_qc if FD_median_dict[subject] > FD_upper_bound]
        print 'Outlier subject with FD_mean > 2 * FS_std:', fd_std_outliers

        # save outlier subjects in txt file
        outliers = fd_std_outliers + fd_mean_outliers +  fd_max_outliers

        print 'All outliers:', outliers

        with open('%s/outliers.json' % lists_dir, 'w') as file:
            file.write(json.dumps(outliers))

    ####################################################################################################################
    # Create 30 random Lists of an equal number of controls/patients for each site
    ####################################################################################################################

    # Take 10 controls and 10 patients from each site at random..
    # ie. total sample = 20* 4 = 80 subjects times 30 lists
    if not os.path.isfile('%s/meta_lists.json' % lists_dir):
        phenotypic = pd.read_csv(os.path.join(tourettome_phenotypic, 'phenotypic_tourettome.csv'),
                                 index_col=0).drop(outliers, axis=0)
        phenotypic = phenotypic.drop(['LZ001', 'LZ052', 'LZ055', 'HA053'], axis=0)
        phenotypic.to_csv('%s/pheno.csv' % lists_dir)

        patients = [subject for subject in phenotypic.index if phenotypic.loc[subject]['Group'] == 'patients']
        controls = [subject for subject in phenotypic.index if phenotypic.loc[subject]['Group'] == 'controls']
        meta_lists = {}

        for i in xrange(30):
            PA = list(
                np.random.choice([subject for subject in controls if subject[0:2] == 'PA'], 20, replace=False)) + list(
                np.random.choice([subject for subject in patients if subject[0:2] == 'PA'], 20, replace=False))

            HA = list(
                np.random.choice([subject for subject in controls if subject[0:2] == 'HA'], 20, replace=False)) + list(
                np.random.choice([subject for subject in patients if subject[0:2] == 'HA'], 10, replace=False))

            # HB = list(
            #     np.random.choice([subject for subject in controls if subject[0:2] == 'HB'], 10, replace=False)) + list(
            #     np.random.choice([subject for subject in patients if subject[0:2] == 'HB'], 10, replace=False))

            LZ = list(
                np.random.choice([subject for subject in controls if subject[0:2] == 'LZ'], 20, replace=False)) + list(
                np.random.choice([subject for subject in patients if subject[0:2] == 'LZ'], 20, replace=False))

            meta_lists['meta_list_%s' % i] = PA + HA + LZ  # + HB

        print 'META_LISTS', meta_lists

        with open('%s/meta_lists.json' % lists_dir, 'w') as file:
            file.write(json.dumps(meta_lists))

    ####################################################################################################################
    # Create brain mask
    ####################################################################################################################

    os.chdir(workspace_dir)
    os.system('flirt -in %s -ref %s -applyisoxfm 4 -nosearch -out MNI_4mm'
              % (mni_brain_2mm, mni_brain_2mm))

    os.system('flirt -in %s -ref %s -applyisoxfm 4 -nosearch -out MNI_4mm_mask_'
              % (mni_brain_2mm_mask, mni_brain_2mm_mask))

    os.system('fslmaths MNI_4mm_mask_ -thr 0.5 -bin MNI_4mm_mask')
    os.system('rm -rf  MNI_4mm_mask_.nii.gz')


def meta_dict_learning(workspace):

    from nilearn.decomposition import DictLearning

    workspace_dir      = mkdir_path(os.path.join(workspace, 'META_DECOMPOSITION'))
    lists_dir          = mkdir_path(os.path.join(workspace_dir, 'subject_lists'))
    dict_learning_dir  = mkdir_path(os.path.join(workspace_dir, 'dict_learning'))

    TR     = (2.4 + 2.4 + 1.4) / 3.
    mask   = os.path.join(workspace_dir, 'MNI_4mm_mask.nii.gz')

    # load sub lists
    meta_lists = json.load(open('%s/meta_lists.json' % lists_dir))

    # run dict_learning 30 times

    def run_meta_dict_learning(n_components):
        for i in xrange(30):

            dl_dir = mkdir_path(os.path.join(dict_learning_dir, 'ndim_%s'%n_components,'DL_%s'%i))

            if not os.path.isfile(os.path.join(dl_dir, 'dl_components.nii.gz')):
                print 'Running Dictionary Learning Decomposition Number %s' % i

                func_list = [os.path.join(tourettome_workspace, subject, 'ICA/REST_EDIT_UNI_BRAIN_MNI4mm_n196_fwhm_hp.nii.gz')
                             for subject in meta_lists['meta_list_%s' % i]]

                print func_list
                dict_learning = DictLearning(n_components=n_components,mask = mask,
                                             memory="nilearn_cache", memory_level=2, n_jobs=2,
                                             smoothing_fwhm=0, verbose=1, random_state=0, n_epochs=1)

                dict_learning.fit(func_list)
                masker = dict_learning.masker_
                components_img = masker.inverse_transform(dict_learning.components_)
                components_img.to_filename('%s/dl_components.nii.gz'%dl_dir)

        # run meta dictionary learning
        dict_learning = DictLearning(n_components=n_components, mask=mask,
                                     memory="nilearn_cache", memory_level=2, n_jobs=2,
                                     smoothing_fwhm=0, verbose=1, random_state=0, n_epochs=1)

        dict_learning_all = [os.path.join(dict_learning_dir,'ndim_%s'%n_components,
                                          'DL_%s'%i, 'dl_components.nii.gz') for i in xrange(30)]
        dict_learning.fit(dict_learning_all)
        masker = dict_learning.masker_
        components_img = masker.inverse_transform(dict_learning.components_)
        components_img.to_filename('%s/ndim_%s/dict_learning_IC.nii.gz'
                                   %(dict_learning_dir, n_components))

    run_meta_dict_learning(20)
    run_meta_dict_learning(30)
    run_meta_dict_learning(40)

def meta_ica_melodic(population, workspace):
    meta_ica_dir = mkdir_path(os.path.join(tourettome_workspace, 'META_ICA'))
    meta_ica_list_dir = mkdir_path(os.path.join(meta_ica_dir, 'meta_subject_lists'))
    melodic_dir  = mkdir_path(os.path.join(tourettome_workspace, 'META_ICA/melodic'))
    ####################################################################################################################
    # Run melodic on the 30 randomized lists
    ####################################################################################################################

    ### TR: PA=2.4; LZ=1.4; HA=2.0; HA=2.4; HB= 2.0. Average TR=2.05
    # TR_mean = (2.4 + 2.4 +    2.0 + 1.4) / 4.
    TR_mean = (2.4 + 2.4 + 1.4) / 3.

    # create brain mask
    os.system('flirt -in %s -ref %s -applyisoxfm 4 -nosearch -out %s/MNI152_T1_4mm_brain_mask'
              % (mni_brain_2mm_mask, mni_brain_2mm_mask, meta_ica_dir))
    os.system('fslmaths %s/MNI152_T1_4mm_brain_mask -thr 0.5 -bin %s/MNI152_T1_4mm_brain_mask_bin'
              % (meta_ica_dir, meta_ica_dir))
    brain_mask_4mm = os.path.join(meta_ica_dir, 'MNI152_T1_4mm_brain_mask_bin.nii.gz')

    # load sub lists
    meta_lists = json.load(open('%s/meta_lists.json' % meta_ica_list_dir))

    # def run_melodic_multi_processing(i):
    for i in xrange(30):

        if not os.path.isfile(os.path.join(os.path.join(meta_ica_dir, 'ICA_%s' % i, 'melodic_IC.nii.gz'))):
            print 'Running Melodic Number %s' % i

            func_list = [os.path.join(tourettome_workspace, subject, 'ICA/REST_EDIT_UNI_BRAIN_MNI4mm_n196_fwhm_hp.nii.gz')
                         for subject in meta_lists['meta_list_%s' % i]]

            # fun_list_file = open('%s/list_%s.txt' %(meta_ica_list_dir, i), 'w')
            # fun_list_file.write(func_list)

            input_file = os.path.join(meta_ica_list_dir, 'input_list_%s.txt' % (i))
            with open(input_file, 'w') as file:
                for func in func_list:
                    file.write(func + '\n')
            # print input_file

            melodic_run_dir = mkdir_path(os.path.join(melodic_dir, 'ICA_%s' % i))

            os.system(' '.join(['melodic',
                                '--in=' + input_file,  # '%s/list_%s.txt' %(meta_ica_list_dir, i),
                                '--mask=' + brain_mask_4mm,
                                '-v',
                                '--outdir=' + melodic_run_dir,
                                '--report',
                                '--tr=' + str(TR_mean),
                                '-d 30'
                                ]))

    ####################################################################################################################
    # Run META ICA
    ####################################################################################################################

    print 'Running META_ICA'

    if not os.path.isfile(os.path.join(melodic_dir, 'ICA_merged', 'melodic_IC.nii.gz')):
        # melodic_ICs = [os.path.join(meta_ica_dir, 'ICA_%s'%i, 'melodic_IC.nii.gz') for i in xrange(30)]
        melodic_ICs = [os.path.join(melodic_dir, 'ICA_%s' % i, 'melodic_IC.nii.gz') for i in xrange(30)]

        # Merge all melodic runs
        os.system('fslmerge -t %s/melodic_IC_all.nii.gz %s' % (melodic_dir, ' '.join(melodic_ICs)))

        # run meta ica
        ica_run_dir_all = mkdir_path(os.path.join(melodic_dir, 'ICA_merged'))
        os.system(' '.join(['melodic',
                            '--in=' + os.path.join(melodic_dir, 'melodic_IC_all.nii.gz'),
                            '--mask=' + brain_mask_4mm,
                            '-v',
                            '--outdir=' + ica_run_dir_all,
                            '--Ostats --nobet --mmthresh=0.5 --report',
                            '--tr=1',  # + str(TR_mean)
                            '-d 30'
                            ]))


def meta_dual_regression(workspace, population, decomposition, ndims):

    workspace_dir = os.path.join(workspace, 'META_DECOMPOSITION')
    lists_dir = os.path.join(workspace_dir, 'subject_lists')

    decomposition_dir = os.path.join(workspace_dir, decomposition, 'ndim_%s'%ndims)
    components_file = os.path.join(decomposition_dir, '%s_IC.nii.gz'%decomposition)

    dualreg_dir = mkdir_path(os.path.join(decomposition_dir, 'dual_regression'))
    os.chdir(dualreg_dir)

    # ###################################################################################################################
    # # Run Dual Regression to extract spatial maps from each subject
    # ###################################################################################################################

    if not os.path.isfile(os.path.join(dualreg_dir, 'dr_stage1_subject00000_bp.nii.gz')):

        print 'Running dual Regression for decomposition:', decomposition

        # Create a Design Matrix  ... same as Glm_gui

        outliers = json.load(open('%s/outliers.json'%lists_dir))
        population = [subject for subject in population if subject not in outliers]

        pproc_list = []
        pproc_dict = {}
        for i, subject in enumerate(population):
            pproc_list.append(os.path.join(workspace, subject, 'ICA/REST_EDIT_UNI_BRAIN_MNI4mm_n196_fwhm_hp.nii.gz'))
            pproc_dict[i] = subject

        # print pproc_list
        print pproc_dict
        print 'Pop size =', len(population), len(pproc_dict), len(pproc_list)

        mat = open('design.mat', 'w')
        mat.write('/NumWaves\t1\n')
        mat.write('/NumPoints\t%s\n' % len(population))
        mat.write('/PPheights\t\t1.000000e+00\n')
        mat.write('/Matrix\n')
        for i in xrange(len(population)):
            mat.write('1.000000e+00\n')
        mat.close()

        con = open('design.con', 'w')
        con.write('/ContrastName1\tgroup mean\n')
        con.write('/NumWaves\t1\n')
        con.write('/NumContrasts\t1\n')
        con.write('/PPheights\t\t1.000000e+00\n')
        con.write('/RequiredEffect\t\t3.121\n')
        con.write('\n')
        con.write('/Matrix\n')
        con.write('1.000000e+00')
        con.close()

        with open('%s/dualreg_subject_list.json' % dualreg_dir, 'w') as file:
            file.write(json.dumps(pproc_dict))

        # Run dual regression
        if not os.path.isfile(os.path.join(dualreg_dir, 'dr_stage1_subject00000.txt')):
            os.system(' '.join(['dual_regression ',
                                components_file,     # <group_IC_maps>
                                '1',          # <des_norm> 0 or 1 (1 is recommended). Whether to variance-normalise the timecourses used as the stage-2 regressors
                                'design.mat', # <design.mat> Design matrix for final cross-subject modelling with randomise
                                'design.con', # <design.con> Design contrasts for final cross-subject modelling with randomise
                                '500',        # <n_perm>
                                dualreg_dir,
                                ' '.join(pproc_list)]
                                ))

        # Bandpass timeseries
        if not os.path.isfile(os.path.join(dualreg_dir, 'dr_stage1_subject00200_bp.nii.gz')):
            for id in pproc_dict.keys():
                print id, ' ', pproc_dict[id]
                affine = nb.load(os.path.join(workspace, pproc_dict[id],
                                              'ICA/REST_EDIT_UNI_BRAIN_MNI4mm_n196_fwhm_hp.nii.gz')).get_affine()
                dr_sub = np.loadtxt(os.path.join(dualreg_dir, 'dr_stage1_subject%05d.txt' % id))
                dr_sub_reshaped = dr_sub.reshape(1, 1, dr_sub.shape[1], dr_sub.shape[0])
                img = nb.Nifti1Image(dr_sub_reshaped, affine)
                img.to_filename(os.path.join(dualreg_dir, 'dr_stage1_subject%05d.nii.gz' % id))

                if subject[0:2] == 'LZ':
                    TR = 1.4
                elif subject[0:2] == 'PA':
                    TR = 2.4
                elif subject[0:2] == 'HA':
                    TR = 2.4

                highpass_cutoff = 0.01  # hz
                lowpass_cutoff = 0.1  # hz
                highpass_sigma = 1. / (2. * TR * highpass_cutoff)
                lowpass_sigma = 1. / (2. * TR * lowpass_cutoff)

                os.system('fslmaths dr_stage1_subject%05d.nii.gz -bptf %s %s dr_stage1_subject%05d_bp.nii.gz'
                          % (id, highpass_sigma, lowpass_sigma, id))


population = tourettome_subjects
workspace = tourettome_workspace

# meta_decompsition_pproc(population, workspace)
# meta_dict_learning(workspace)
# meta_dual_regression(workspace, population, decomposition='dict_learning', ndims=20)
# meta_dual_regression(workspace, population, decomposition='dict_learning', ndims=30)
meta_dual_regression(workspace, population, decomposition='dict_learning', ndims=40)


