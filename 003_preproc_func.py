__author__ = 'kanaan_02.12.2016'

import os
from utilities.utils import mkdir_path,create_fsl_mats
import nipype.interfaces.spm as spm
from variables.subject_list import *
import nibabel as nb


def preprocess_functional(population, afs_dir, workspace):
    count = 0
    for subject in population:
        count += 1
        print '========================================================================================'
        print '%s-Preprocessing functional data for %s' %(count, subject)

        # input
        afsdir  = os.path.join(afs_dir, subject, 'NIFTI')
        # output
        func_dir  = mkdir_path(os.path.join(workspace, subject, 'REST'))
        moco_dir = mkdir_path(os.path.join(func_dir, 'moco'))

        if not os.path.isfile(os.path.join(moco_dir, 'REST_moco_2.nii.gz')):

            print '....Dropping first 5 volumes'
            first_frame = '5'
            last_frame = nb.load(os.path.join(afsdir, 'REST.nii.gz')).get_data().shape[3] -1
            frames = '[%s..%s]'%(first_frame, last_frame)

            os.system('3dcalc -a %s/REST.nii.gz%s -expr "a" -prefix %s/_REST.nii.gz' % (afsdir, frames, func_dir))

            print '....Swapdim to RPI'
            os.system('fslswapdim %s RL PA IS %s' % (os.path.join(func_dir, '_REST'), (os.path.join(func_dir, 'REST'))))
            os.remove('%s/_REST.nii.gz'%func_dir)

            print '....Deoblique'
            ### Replace transformation matrix in header with cardinal matrix.This option DOES NOT deoblique the volume.
            os.system('3drefit -deoblique %s' % os.path.join(func_dir, 'REST.nii.gz'))

            # Run two step motion correction
            print 'Running two-step motion correction'
            os.system('fslmaths %s/REST -Tmean %s/REST_mean' %(func_dir, moco_dir))

            #### step 1
            os.chdir(moco_dir)
            os.system('3dvolreg -Fourier -twopass -1Dfile REST_moco_1.1D -1Dmatrix_save REST_moco_1_aff12.1D -zpad 4 -maxdisp1D REST_moco_1_MX.1D '
                      '-prefix REST_moco_1.nii.gz -base REST_mean.nii.gz ../REST.nii.gz')
            os.system('fslmaths REST_moco_1 -Tmean REST_moco_1_mean')

            #### step 2
            os.system('3dvolreg -Fourier -twopass -1Dfile REST_moco_2.1D -1Dmatrix_save REST_moco_2_aff12.1D -zpad 4 -maxdisp1D REST_moco_2_MX.1D '
                      '-prefix REST_moco_2.nii.gz -base REST_moco_1_mean.nii.gz ../REST.nii.gz')

            # create fsl style affine matrices
            mats = create_fsl_mats('%s/REST_moco_2_aff12.1D'%moco_dir)


        # Intensity Normalization
        print '.....Normalizing intensity to Mode 1000 and deskulling'
        os.chdir(func_dir)
        if not os.path.isfile('REST_PPROC_NATIVE_BRAIN.nii.gz'):
            os.system('fslmaths moco/REST_moco_2.nii.gz -ing 1000 REST_PPROC_NATIVE.nii.gz')
            os.system('bet REST_PPROC_NATIVE.nii.gz REST_PPROC_NATIVE_BRAIN.nii.gz -f 0.50 -F -m -t -g 0.00')
            os.system('3dTstat -mean -prefix REST_PPROC_NATIVE_BRAIN_mean.nii.gz  REST_PPROC_NATIVE_BRAIN.nii.gz ')
            # os.system('fslmaths REST_PPROC_NATIVE_BRAIN_mask.nii.gz -ero -ero REST_PPROC_NATIVE_BRAIN_mask_ero.nii.gz')

preprocess_functional(population = ['PA001'], afs_dir = tourettome_afs, workspace = tourettome_workspace )