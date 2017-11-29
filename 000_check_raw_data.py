import os
import shutil
from utilities.utils import mkdir_path
from variables.subject_list import *


def preprocess_anatomical(population, afs_dir, workspace):

    print '========================================================================================'
    print ''
    print '                          Tourettome - 000.Grab Raw Data                                '
    print ''
    print '========================================================================================'

    count = 0
    for subject in population:
        count +=1
        print '========================================================================================'
        print '-%s Preprocessing anatomical data for %s' %(count, subject)

        data_dir = os.path.join(afs_dir, subject, 'NIFTI')
        out_dir = mkdir_path(os.path.join(workspace, subject, 'RAW'))

        if not os.path.isfile(os.path.join(out_dir, 'ANATOMICAL.nii.gz')):
            shutil.copy(os.path.join(data_dir, 'ANATOMICAL.nii.gz'), os.path.join(out_dir, 'ANATOMICAL.nii.gz'))

        if not os.path.isfile(os.path.join(out_dir, 'REST.nii.gz')):
            shutil.copy(os.path.join(data_dir, 'REST.nii.gz'), os.path.join(out_dir, 'REST.nii.gz'))

        if subject[0:2] == 'LZ':
            if not os.path.isfile(os.path.join(out_dir, 'T1MAPS.nii.gz')):
                shutil.copy(os.path.join(data_dir, 'T1MAPS.nii.gz'), os.path.join(out_dir, 'T1MAPS.nii.gz'))

preprocess_anatomical(population = tourettome_subjects, afs_dir = tourettome_afs, workspace = tourettome_workspace)