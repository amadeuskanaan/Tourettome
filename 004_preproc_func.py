__author__ = 'kanaan_02.12.2016'

import os
import shutil
import sys

import nibabel as nb

from utilities.utils import mkdir_path
from variables.subject_list import *

assert len(sys.argv)== 2
subject_index=int(sys.argv[1])

def preprocess_functional(population, workspace):

    # for subject in population:
        subject = population[subject_index]
        print '========================================================================================'
        print 'Preprocessing functional data for %s' %(subject)


        raw_dir   = mkdir_path(os.path.join(workspace, subject, 'RAW'))
        func_dir  = mkdir_path(os.path.join(workspace, subject, 'FUNCTIONAL'))
        moco_dir  = mkdir_path(os.path.join(func_dir, 'moco'))
        edit_dir  = mkdir_path(os.path.join(func_dir, 'edit'))

        ##### Minimal pre-processing

        if not os.path.isfile(os.path.join(func_dir, 'REST_EDIT.nii.gz')):

            print '.....Edit Functional Image (Slice-time-corr/Deoblique/Drop-TRs/Reorient) '

            os.chdir(func_dir)

            # get data
            shutil.copy(os.path.join(raw_dir, 'REST.nii.gz'), os.path.join(func_dir, 'REST.nii.gz'))

            # get params
            img_hdr = nb.load('REST.nii.gz').header
            TR    = img_hdr['pixdim'][4]
            nvols = img_hdr['dim'][4]
            frames = '[%s..%s]' % (4, nvols -1)

            print 'TR =', TR
            print 'N-Vols=', nvols

            # Deoblique
            os.system('3drefit -deoblique REST.nii.gz')

            # Slice time correction
            os.chdir(edit_dir)
            os.system('3dTshift -TR %s -tzero 0 -tpattern alt+z -prefix REST_slc.nii.gz ../REST.nii.gz' %(TR))

            # Dropping TRs
            os.system('3dcalc -a REST_slc.nii.gz%s -expr "a" -prefix REST_slc_drop.nii.gz' % frames)

            # Reorient to RPI
            os.system('3dresample -orient RPI  -prefix ../REST_EDIT.nii.gz -inset REST_slc_drop.nii.gz')


        ##### Generate Motion Paramters

        if not os.path.isfile(os.path.join(moco_dir, 'REST_EDIT_moco2.nii.gz')):

            print '.... Running two-step motion correction'

            os.chdir(moco_dir)
            # run No.1
            os.system('mcflirt -in ../REST_EDIT -out REST_EDIT_moco1 -mats -plots -stats -meanvol ')

            # run No.2
            os.system('mcflirt -in ../REST_EDIT -out REST_EDIT_moco2 -refvol REST_EDIT_moco1_meanvol -mats -plots -stats')

        ###### BET and Intensity normalization

        if not os.path.isfile(os.path.join(func_dir, 'REST_EDIT_BRAIN_MEAN.nii.gz')):

            print '....Brain extraction and intensity normalization'

            os.chdir(func_dir)

            # Create mask
            os.system('bet moco/REST_EDIT_moco2_meanvol.nii.gz moco/REST_EDIT_moco2_meanvol_brain -m -R -f 0.35' )
            os.system('cp moco/REST_EDIT_moco2_meanvol_brain_mask.nii.gz REST_BRAIN_MASK.nii.gz')

            # Extract Brain
            os.system('fslmaths REST_EDIT -mul REST_BRAIN_MASK')
            os.system('fslmaths moco/REST_EDIT_MOCO_BRAIN_ -mul REST_BRAIN_MASK .nii.gz')

            # Intensity Normalization'
            os.system('fslmaths REST_EDIT_BRAIN_ -ing 1000 REST_EDIT_BRAIN -odt float' )
            os.system('fslmaths REST_EDIT_MOCO_BRAIN_ -ing 1000 REST_EDIT_MOCO_BRAIN -odt float' )
            os.system('rm -rf REST*_.nii.gz')

            # Get Mean'
            os.system('fslmaths REST_EDIT_BRAIN -Tmean REST_EDIT_BRAIN_MEAN.nii' )
            os.system('fslmaths REST_EDIT_MOCO_BRAIN -Tmean REST_EDIT_MOCO_BRAIN_MEAN.nii' )


# preprocess_functional(population = leipzig, workspace = tourettome_workspace)
# preprocess_functional(population = paris, workspace = tourettome_workspace)
# preprocess_functional(population = hannover_a, workspace = tourettome_workspace)
# preprocess_functional(population = hannover_b, workspace = tourettome_workspace)
preprocess_functional(population = tourettome_subjects, workspace = tourettome_workspace)

