import os
import numpy as np
from variables.subject_list import *




def prep_meta_ica(population, workspace):

    for subject in population:

        # Input/Output
        subject_dir = os.path.join(workspace, subject)
        ica_dir     = os.path.join(subject_dir, 'ICA')
        func_2mm    = os.path.join(subject_dir,'REGISTRATION', 'REST_EDIT_UNI_BRAIN_MNI2mm.nii.gz')

        os.chdir(ica_dir)

        # Resample data to 4mm
        os.system('flirt -in %s -ref %s -applisoxfm 4 -nosearch -out REST_EDIT_UNI_BRAIN_MNI4mm'%(func_2mm, mni_brain_2mm))

        # Cut data to shortest time-point length
        ### n_vols: PA=196; LZ=418; HB=271; HA=271
        ### TR: PA=2.4; LZ=1.4; HA=2.0; HA=2.4; HB= 2.0. Average TR=2.05
        os.system('fslroi REST_EDIT_UNI_BRAIN_MNI4mm REST_EDIT_UNI_BRAIN_MNI4mm_n174 0 174')

        # resample Data to 4mm

prep_meta_ica(['LZ030'], tourettome_workspace)


#
# def cut_data(func)
#
# # Given computational resource limitations (e.g., 32 GB of physical memory), as well as a number of centers with a
# # small number of time points due to repetition times >2.0 s, each TC-GICA run was applied to a dataset consisting
# # of 18 partic- ipants/center from the 17 centers that collected a minimum of 165 functional volumes per scan. This
# # approach also ensured that a single center’s data would not drive the ICA components de- tected. Consistent with
# # recent work on low-dimensional ICA (8), the number of components was fixed at 20. Given the potential for such
# # factors as initial random values and subject sampling to affect ICA results, 25 TC-GICA analyses were performed,
# # each using a unique resampling from each of the 17 centers. A meta-ICA analysis was then carried out across the 25
# # runs to extract the 20 spatially independent components consistently identified across the 25 runs. An alternative
# # hierarchical clustering approach based on ICASSO (9) is described below. The two approaches yielded similar results.
# # Dual regression (10, 11) was then carried out using the 20 resulting components as templates, to produce individual
# # participant maps for each of the 20 components.
#
# # 1- Cut all data to smallest number of frames
# # 2- Keep only subjects with FD within 2SD
# # 3- Create 25 population lists ...
# ###### max length = length of smallest population
# ###### each population list should be half controls and half patients
# ###### use unique resample each time.
# ######
# # 4- Run melodic with n=20 components on each population list
# # 5- Run melodic on the 25 ICAs.
#
#
# #was carried out 25 times on randomized subsets of 112 participants (7 in the TD group plus 7 in the ASD group for each of the 8 sites). The
#
# def make_meta_ica(population, workspace):
#
#     for subject in population:
#
#         subject_dir = os.path.join()
#
#
#
# # Step 0a------ take first 200 timepoints only
# # step 0b only take subjects with FD within 2SD from the mean
# #  Take 10 controls and 10 patients from each site at random.. ie. total sample = 20* 4 = 80
# #  Create 30 subject lists of 80 subjects (falh GTS half HC) with resampling ... crucial that there is an overlap
# # Run melodic 30 times
# # fslmerge melodic_IC.nii.gz (this will equal d=30 * 30)
# # run big ICA on 900 time_point melodic_ICA_nii_merge.nii.gz withput dimensions
#
# # dual regression .. get timecourse for each spatial map for each subject
# # choose interesting RSNs
#
# #### Reprodicibility across sub_population ===== meta_ica ravel n_component pearson correlation with each n_component of sub_sample ICA
# #### To get reprodicbility value.. take maximum pearson correlation for each meta_ica_component and each sub_sample_ica_component
# #### reprodibility value equals median.. === x-axis
#
# ### to get y axis == "propotion of sptial map in gray matter"... multiply each meta_ica_component with GM_MASK....
#
#
# ##################### Now we have 20 components
# # ie timecourse for each component for each subject
# # create correlation matrix for each subject
# # run indepedent sample t-test for each component.. tkae arctanh of correlation matrix
# # take each box (correlation value in the matrix) and create two vectors (patients and controls) and run t-test.
# # FDR multiple comparison correction.
#
#
#
# def make_meta_ica(workspace):
#
#     # Take 10 controls and 10 patients from each site at random for a total of 30 lists
#
#     def random_sample():
#
#         LZ_p = np.random.choice(Leipzig_patients,10)
#         LZ_c = np.random.choice(Leipzig_controls,10)
#
#         HA_p = np.random.choice(Hannover_a_patients,10)
#         HA_c = np.random.choice(Hannover_a_controls,10)
#
#         HB_p = np.random.choice(Hannover_b_patients,10)
#         HB_p = np.random.choice(Hannover_b_controls,10)
#
#         PA_p = np.random.choice(Paris_patients, 10)
#         PA_c = np.random.choice(Paris_controls, 10)
#
#         ica_population =
#
#
#     for ica_val, func_subject_list in enumerate(lists):
#         ica_out_dir = mkdir_path(os.path.join(workspace, 'meta_ICA', 'ICA_DIR_%s'% ica_val))
#
#         os.system(' '.join(['melodic',
#                             '--in=' + func_subject_list,
#                             '--mask=' + brain_mask,
#                             '-v',
#                             '-d 30',
#                             '--outdir=' +,
#                             '--Ostats --nobet --mmthresh=0.5 --report',
#                             '--tr=' + str(TR)]))
#
#
#
#
#
#
#
#
#
#



