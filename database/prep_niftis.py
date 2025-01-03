__author__ = 'kanaan_06.03.2017'

import os, sys
import shutil
sys.path.append(os.path.expanduser('/scr/malta1/Github/Tourettome'))
from utilities.utils import *
from variables.subject_list import *


def make_nifti(population, afs_dir):
    count = 0
    for subject in population:
        count += 1
        print '========================================================================================'
        print '%s-Converting dicom to Nifti for %s' %(count, subject)
        #input
        dicom_dir  = os.path.join(afs_dir, subject, 'DICOM')
        nifti_dir = mkdir_path(os.path.join(afs_dir, subject, 'NIFTI'))
        string = '%p_%t_%u_%s'

        if not os.path.isfile(os.path.join(nifti_dir, 'ANATOMICAL.nii.gz')):
            if subject[0:2] == 'LZ':
                os.system('dcm2niix -b n -o %s %s'%(nifti_dir, dicom_dir))
                anat    = [os.path.join(nifti_dir,fname) for fname in os.listdir(nifti_dir) if 'mp2rage' in fname][0]
                print anat

                rest    = [os.path.join(nifti_dir,fname) for fname in os.listdir(nifti_dir) if 'resting' in fname][0]
                se      = sorted([os.path.join(nifti_dir,fname) for fname in os.listdir(nifti_dir) if '_se_' in fname])
                shutil.move(anat,  os.path.join(nifti_dir, 'ANATOMICAL.nii.gz'))
                shutil.move(rest,  os.path.join(nifti_dir, 'REST.nii.gz'))
                shutil.move(se[0], os.path.join(nifti_dir, 'REST_SE.nii.gz'))
                shutil.move(se[1], os.path.join(nifti_dir, 'REST_SEINV.nii.gz'))

            if subject[0:2] == 'HA':
                os.system('dcm2niix  -b n -o %s %s' % (nifti_dir, dicom_dir))
                anat =  sorted([os.path.join(nifti_dir,fname) for fname in os.listdir(nifti_dir) if 't1_mpr' in fname])
                rest =  [os.path.join(nifti_dir,fname) for fname in os.listdir(nifti_dir) if 'resting' in fname]
                shutil.move(anat[1],  os.path.join(nifti_dir, 'ANATOMICAL.nii.gz'))
                shutil.move(rest[0],  os.path.join(nifti_dir, 'REST.nii.gz'))
                os.system('rm -rf %s' %anat[0])

            if subject[0:2] == 'HB':
                # os.system('rm -rf %s/*' % nifti_dir)
                os.system('dcm2niix -b n -o %s %s' % (nifti_dir, dicom_dir))
                anat = [os.path.join(nifti_dir, fname) for fname in os.listdir(nifti_dir) if 'HighResolution' in fname][0]
                rest = sorted([os.path.join(nifti_dir, fname) for fname in os.listdir(nifti_dir) if 'REST_AKTIVITY' in fname])[0]
                print rest
                dti_str = ['_12_', '12_', 'dti', 'DTI']
                dti  = [os.path.join(nifti_dir, fname) for fname in os.listdir(nifti_dir) if 'nii' in fname and any(x in fname  for x in dti_str)][0]
                bvc  = [os.path.join(nifti_dir, fname) for fname in os.listdir(nifti_dir) if 'bvec' in fname][0]
                bva  = [os.path.join(nifti_dir, fname) for fname in os.listdir(nifti_dir) if 'bval' in fname][0]
                shutil.move(anat, os.path.join(nifti_dir, 'ANATOMICAL.nii.gz'))
                shutil.move(rest, os.path.join(nifti_dir, 'REST.nii.gz'))
                shutil.move(dti, os.path.join(nifti_dir, 'DWI.nii.gz'))
                shutil.move(bvc, os.path.join(nifti_dir, 'DWI.bvec.gz'))
                shutil.move(bva, os.path.join(nifti_dir, 'DWI.bval.gz'))

            if subject[0:2] == 'PA':
                os.system('dcm2niix -b n -o %s %s' % (nifti_dir, dicom_dir))
                anat = sorted([os.path.join(nifti_dir, fname) for fname in os.listdir(nifti_dir) if 't1' in fname])[-1]

                if subject =='PA049':
                    rest = sorted([os.path.join(nifti_dir, fname) for fname in os.listdir(nifti_dir) if 'Rest' in fname])[0]
                else:
                    rest = sorted([os.path.join(nifti_dir, fname) for fname in os.listdir(nifti_dir) if 'Rest' in fname])[-1]

                shutil.move(anat, os.path.join(nifti_dir, 'ANATOMICAL.nii.gz'))
                shutil.move(rest, os.path.join(nifti_dir, 'REST.nii.gz'))


            # os.system('flirt -in %s/REST -ref %s/ANATOMICAL -dof 6 -cost corratio -out %s/test_func2anat'%(nifti_dir,nifti_dir,nifti_dir))

        # Get T1MAPS.... introduced 16-04-2017
        dicom_dir_t1 = os.path.join(afs_dir, subject, 'DICOM_T1MAPS')
        if subject[0:2] == 'LZ':
            if not os.path.isfile(os.path.join(nifti_dir, 'T1MAPS.nii.gz')):
                os.system('dcm2niix -b n -o %s %s' % (dicom_dir_t1, dicom_dir_t1))
                t1 = [os.path.join(dicom_dir_t1, fname) for fname in os.listdir(dicom_dir_t1) if 'mp2rage' in fname][0]
                shutil.move(t1, os.path.join(nifti_dir, 'T1MAPS.nii.gz'))

# make_nifti(population= leipzig,    afs_dir=tourettome_afs)
# make_nifti(population= hannover_a, afs_dir=tourettome_afs)
# make_nifti(population= hannover_b, afs_dir=tourettome_afs)
# make_nifti(population= paris,      afs_dir=tourettome_afs)
make_nifti(population= ['PA049'],      afs_dir=tourettome_afs)
