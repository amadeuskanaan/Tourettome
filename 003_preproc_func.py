__author__ = 'kanaan_02.12.2016'

import os
import nibabel as nb
import shutil
import nibabel as nb
from utilities.utils import mkdir_path
from utilities.utils import create_fsl_mats
from variables.subject_list import *

def preprocess_functional(population, workspace):

    for subject in population:
        print '========================================================================================'
        print 'Preprocessing functional data for %s' %(subject)


        raw_dir   = mkdir_path(os.path.join(workspace, subject, 'RAW'))
        func_dir  = mkdir_path(os.path.join(workspace, subject, 'FUNCTIONAL'))
        moco_dir  = mkdir_path(os.path.join(func_dir, 'moco'))
        edit_dir  = mkdir_path(os.path.join(func_dir, 'edit'))


        ##### Minimal pre-processing

        if not os.path.isfile(os.path.join(func_dir, 'REST_EDIT.nii.gz')):

            print '-- Inital editing of functional image'

            # grab data
            shutil.copy(os.path.join(raw_dir, 'REST.nii.gz'), os.path.join(func_dir, 'REST.nii.gz'))

            # get params
            os.chdir(func_dir)
            img_hdr = nb.load('REST.nii.gz').header
            TR    = img_hdr['pixdim'][4]
            nvols = img_hdr['dim'][4]
            frames = '[%s..%s]' % (4, nvols -1)

            print 'TR =', TR
            print 'N-Vols=', nvols

            print '.......deoblique'
            os.system('3drefit -deoblique REST.nii.gz')

            print '.......slice time correction'
            os.chdir(edit_dir)
            os.system('3dTshift -TR %s -tzero 0 -tpattern alt+z -prefix REST_slc.nii.gz ../REST.nii.gz' %(TR))

            print '.......dropping TRs'

            os.system('3dcalc -a REST_slc.nii.gz%s -expr "a" -prefix REST_slc_drop.nii.gz' % frames)

            print '.......reorient'
            os.system('3dresample -orient RPI  -prefix REST_EDIT.nii.gz  -inset REST_slc_drop.nii.gz')


        ##### Generate Motion Paramters

        if not os.path.isfile(os.path.join(func_dir, 'REST_EDIT_MOCO.nii.gz')):

            print '.... Running two-step motion correction'

            os.chdir(moco_dir)
            # run No.1 - CORRATIO

            os.system('3dTstat -mean -prefix REST_EDIT_mean.nii.gz ../REST_EDIT.nii.gz')
            os.system('3dvolreg -Fourier -twopass -zpad 4  '
                      '-1Dfile          REST_EDIT_moco1.1D '
                      '-1Dmatrix_save   REST_EDIT_moco1_aff12.1D '
                      '-maxdisp1D       REST_EDIT_moco1_MX.1D '
                      '-base            REST_EDIT_mean.nii.gz '
                      '-prefix          REST_EDIT_moco1.nii.gz '
                      '../REST_EDIT.nii.gz')

            # run No.2 - BBR
            os.system('3dTstat -mean -prefix REST_EDIT_moco1_mean.nii.gz REST_EDIT_moco1.nii.gz')
            os.system('3dvolreg -Fourier -twopass -zpad 4  '
                      '-1Dfile          REST_EDIT_moco2.1D '
                      '-1Dmatrix_save   REST_EDIT_moco2_aff12.1D '
                      '-maxdisp1D       REST_EDIT_moco2_MX.1D '
                      '-base            REST_EDIT_moco1_mean.nii.gz '
                      '-prefix          REST_EDIT_moco2.nii.gz '
                      '../REST_EDIT.nii.gz')

            # mats = create_fsl_mats('%s/REST_EDIT_moco2_aff12.1D' % moco_dir)

        ###### Brain Extraction and Intensity normaliatuon

        if not os.path.isfile(os.path.join(func_dir, 'REST_EDIT_BRAIN_MEAN.nii.gz')):

            print '....Brain extraction and intensity normalization'

            os.chdir(func_dir)
            os.system('3dAutomask -prefix REST_EDIT_BRAIN_MASK.nii.gz REST_EDIT.nii.gz')
            os.system('3dcalc -a REST_EDIT.nii.gz -b REST_EDIT_BRAIN_MASK.nii.gz  -expr \'a*b\' -prefix REST_EDIT_BRAIN_.nii.gz')

            #print '....Intensity normalization'
            os.system('fslmaths REST_EDIT_BRAIN_ -ing 1000 REST_EDIT_BRAIN -odt float')
            os.system('rm -rf REST_EDIT_BRAIN_.nii.gz')

            #print '....get mean'
            os.system('3dTstat -mean -prefix REST_EDIT_BRAIN_MEAN.nii.gz REST_EDIT_BRAIN.nii.gz')


# paris.remove('PA049')
preprocess_functional(population = ['HA020'], afs_dir = tourettome_afs, workspace = tourettome_workspace)

