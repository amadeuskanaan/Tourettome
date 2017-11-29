__author__ = 'kanaan_29.11.2017'

import os, sys
import shutil
sys.path.append(os.path.expanduser('/scr/malta1/Github/Tourettome'))
from utilities.utils import *
from variables.subject_list_original import *

def check_nifti(population, afs_dir):

    for subject in population:

        if not os.path.join(afs_dir, subject, 'REST.nii.gz'):
            print 'Subject %s is missing REST data '% subject

        if not os.path.join(afs_dir, subject, 'ANATOMICAL.nii.gz'):
            print 'Subject %s is missing ANAT data ' %subject

all_subjects = sorted(LEIPZIG_subject_dict.values()) + \
                sorted(PARIS_subject_dict.values()) + \
                sorted(HANNOVER_A_subject_dict.values()) + \
                sorted(HANNOVER_B_subject_dict.values()) + \
                sorted(HAMBURG_subject_dict.values())

print all_subjects
print len(all_subjects)
check_nifti(all_subjects, tourettome_afs)
