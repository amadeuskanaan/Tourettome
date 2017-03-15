__author__ = 'kanaan_02.12.2016'

import os
from utilities.utils import mkdir_path
from variables.subject_list import *
import shutil
import sys
import nipype.interfaces.spm as spm

# Function to preprocess multi-site anatomical data (mprage and mp2rage)
# Needs FSL5, AFNI, SPM, FREESURFER, pyenv

# assert len(sys.argv)== 2
# subject_index=int(sys.argv[1])

def preprocess_anatomical(population, afs_dir, workspace, freesurfer_dir):
    count = 0
    for subject in population:
        # subject = population[subject_index]
        count += 1
        print '========================================================================================'
        print '%s-Preprocessing anatomical data for %s' %(subject, subject)

        # input
        afsdir = os.path.join(afs_dir, subject, 'NIFTI')
        #output
        anatdir = mkdir_path(os.path.join(workspace, subject, 'ANATOMICAL'))



        if not os.path.isfile(os.path.join(anatdir, 'ANATOMICAL_BRAIN.nii.gz')):
            if not os.path.isfile(os.path.join(anatdir, 'ANATOMICAL.nii.gz')):
                # Swapdim - Force to RPI
                shutil.copy(os.path.join(afsdir, 'ANATOMICAL.nii.gz'), os.path.join(anatdir, 'ANATOMICAL.nii.gz'))
		        #os.system('fslswapdim %s RL PA IS %s' %(os.path.join(afsdir,  'ANATOMICAL'), (os.path.join(anatdir, 'ANATOMICAL'))))
                #os.system('fslchfiletype NIFTI_GZ %s' % os.path.join(anatdir, 'ANATOMICAL'))
                # Deoblique
                # Replace transformation matrix in header with cardinal matrix.This option DOES NOT deoblique the volume.
                os.system('3drefit -deoblique %s' %os.path.join(anatdir, 'ANATOMICAL.nii.gz'))

            # Run SPM segmentation
            spmdir  = mkdir_path(os.path.join(anatdir, 'seg_spm'))
            if not os.path.isfile(os.path.join(spmdir, 'c1ANATOMICAL.nii')):
                print '.. Running SPM segmentation'
                if not os.path.isfile(os.path.join(spmdir, 'ANATOMICAL.nii')):
                    shutil.copy(os.path.join(anatdir, 'ANATOMICAL.nii.gz'), os.path.join(spmdir, 'ANATOMICAL.nii.gz'))
                    os.system('fslchfiletype NIFTI %s' % os.path.join(spmdir, 'ANATOMICAL'))

                seg = spm.NewSegment()
                seg.inputs.channel_files = os.path.join(spmdir, 'ANATOMICAL.nii')
                seg.inputs.channel_info = (0.0001, 60, (True, True))
                seg.base_dir = spmdir
                seg.run()

            # Use segmentation to deskull data
            if not os.path.isfile(os.path.join(spmdir, 'c1ANATOMICAL_bin.nii.gz')):
                print '.. Deskulling'
                os.system('fslmaths %s/c1ANATOMICAL -thr 0.1 -bin %s/c1ANATOMICAL_bin'%(spmdir,spmdir))
                os.system('fslmaths %s/c2ANATOMICAL -thr 0.1 -bin %s/c2ANATOMICAL_bin'%(spmdir,spmdir))
                os.system('fslmaths %s/c3ANATOMICAL -thr 0.9 -bin %s/c3ANATOMICAL_bin'%(spmdir,spmdir))
                os.system('fslmaths %s/c1ANATOMICAL -add %s/c2ANATOMICAL_bin -add %s/c3ANATOMICAL_bin -bin -fillh -s 3 -thr 0.4 -bin %s/ANATOMICAL_BRAIN_MASK'
                          %(spmdir, spmdir,spmdir,anatdir))
                os.system('fslmaths %s/ANATOMICAL -mas %s/ANATOMICAL_BRAIN_MASK %s/ANATOMICAL_BRAIN' %(anatdir, anatdir, anatdir))

        # Run FSL-FIRST subcortical segmentation
        if not os.path.isfile(os.path.join(anatdir, 'ANATOMICAL_GM.nii.gz')):
            print '.. Running FSL-FIRST segmentation'
            firstdir = mkdir_path(os.path.join(anatdir, 'seg_first'))
            os.chdir(firstdir)
            if not os.path.isfile(os.path.join(firstdir, 'FIRST_all_fast_firstseg.nii.gz')):
                os.system('flirt -in ../ANATOMICAL_BRAIN.nii.gz -ref %s -omat anat2mni.mat -out anat2mni -cost mutualinfo -dof 12'%(mni_brain_1mm)) # no skulls. brain to brain.
                os.system('run_first_all -d -i ../ANATOMICAL_BRAIN -b -a anat2mni.mat -o FIRST')

            # Optimize tissue masks - this is done in order to include the majority of BG voxels into the GM mask and remove them from WM and CSF.
            os.system('fslmaths FIRST_all_fast_firstseg -bin FIRST_all_fast_firstseg_bin')
            os.system('fslmaths ../seg_spm/c1ANATOMICAL -thr 0.5 -bin -add  FIRST_all_fast_firstseg_bin -bin ../ANATOMICAL_GM')
            os.system('fslmaths ../seg_spm/c2ANATOMICAL -thr 0.9 -bin -sub FIRST_all_fast_firstseg_bin -bin ../ANATOMICAL_WM')
            os.system('fslmaths ../seg_spm/c3ANATOMICAL -sub 0.9 -bin -sub FIRST_all_fast_firstseg_bin -bin ../ANATOMICAL_CSF')

# test_sample = ['HB003']
# test_sample = ['HA001']
#test_sample = ['LZ002']
# test_sample = ['PA010']
xall = ['HA001', 'HA002',]
# preprocess_anatomical(population = hannover_a, afs_dir = afs_dir, workspace = workspace_dir, freesurfer_dir= freesurfer_dir)
# preprocess_anatomical(population = hannover_b, afs_dir = afs_dir, workspace = workspace_dir, freesurfer_dir= freesurfer_dir)
# preprocess_anatomical(population = leipzig, afs_dir = afs_dir, workspace = workspace_dir, freesurfer_dir= freesurfer_dir)
preprocess_anatomical(population = paris[55:], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= tourettome_freesurfer)












