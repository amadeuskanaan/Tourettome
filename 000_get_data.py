
import os
from utilities.utils import mkdir_path
from variables.subject_list import *
import shutil

def preprocess_anatomical(population, afs_dir, workspace, freesurfer_dir):
    for subject in population:
        print '========================================================================================'
        print '-Preprocessing anatomical data for %s' %subject

        # input
        afsdir = os.path.join(afs_dir, subject, 'NIFTI')
        rawdir = mkdir_path(os.path.join(workspace, subject, 'RAW'))

        if not os.path.isfile(os.path.join(rawdir, 'ANATOMICAL.nii.gz')):
            shutil.copy(os.path.join(afsdir, 'ANATOMICAL.nii.gz'), os.path.join(rawdir, 'ANATOMICAL.nii.gz'))

        if not os.path.isfile(os.path.join(rawdir, 'REST.nii.gz')):
            shutil.copy(os.path.join(afsdir, 'REST.nii.gz'), os.path.join(rawdir, 'REST.nii.gz'))



preprocess_anatomical(population = ['HB004'], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)












