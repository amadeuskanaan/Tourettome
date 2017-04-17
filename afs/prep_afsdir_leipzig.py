__author__ = 'kanaan_07.11.2016'
import glob
import os
import shutil

import dicom as pydcm
import numpy as np
import pandas as pd

from utilities.utils import *
from variables.subject_list_original import *


# Function to copy leipzig data from original datadir to new afs directory.
# Creates new project specific subject_ids


def make_leipzig_afs(population, original_datadir, afs_dir):

    print '###########################################'
    print '  Creating clean folder for Leipzig data'
    print '###########################################'

    count = 0
    LZ_subjects = dict()

    for subject in population:

        # create new subject id
        count += 1
        subject_id = 'LZ%03d' %count
        LZ_subjects[subject] = subject_id

        print '%s. Organizing data for LEIPZIG subject %s [%s] in new afs dir' % (count, subject_id, subject)

        #create output files and directories
        subject_dir = mkdir_path(os.path.join(afs_dir, subject_id))
        dicom_dir   = mkdir_path(os.path.join(subject_dir, 'DICOM'))
        param_file  = os.path.join(subject_dir, '%s_param.csv' % subject_id)

        # grab correct datadir from old afs
        if os.path.isdir(os.path.join(original_datadir, 'probands', subject)):
            data_dir = os.path.join(original_datadir, 'probands', subject)
            group_id = 'controls'
            if subject is 'GF3T' or subject is 'ZT5T':
                data_dir = os.path.join('/a/projects/nmr093b/', 'probands', subject)
                group_id = 'controls'
            elif subject is 'GSAP':
                data_dir = os.path.join(original_datadir, 'patients', subject)
                group_id = 'patients'
        else:
            data_dir = os.path.join(original_datadir, 'patients', subject)
            group_id = 'patients'

        # get scan number from 'Scans.txt' instead of wasting time and reading fileheader
        scans    = find('Scans.txt', data_dir)
        rest_id  = str([line for line in open(scans).readlines() if 'resting' in line])[2:6]
        se_id    = str([line for line in open(scans).readlines() if 'cmrr_mbep2d_se' in line])[2:6]
        seinv_id = str([line for line in open(scans).readlines() if 'cmrr_mbep2d_se_invpol' in line])[2:6]
        uni_id   = str([line for line in open(scans).readlines() if 'UNI' in line and 'SLAB' not in line])[2:6]


        # copy anat and rest dicom data to afs directory
        if not os.listdir(dicom_dir):
            for id in [rest_id, se_id, seinv_id, uni_id]:
                print id
                for file in glob.glob(os.path.join(data_dir, 'DICOM/%s*' % id)):
                    shutil.copy(file, dicom_dir)


        ######## GET T1MAPS .  introduced 16.04.2017
        dicom_dir_t1 = mkdir_path(os.path.join(subject_dir, 'DICOM_T1MAPS'))
        t1_id = str([line for line in open(scans).readlines() if 'T1_Images' in line and 'SLAB' not in line])[2:6]
        # copy anat and rest dicom data to afs directory
        if not os.listdir(dicom_dir_t1):
                for file in glob.glob(os.path.join(data_dir, 'DICOM/%s*' % t1_id)):
                    shutil.copy(file, dicom_dir_t1)


        #if not os.path.isfile(param_file):
        print '.... extracting subject paramters'

        rest_all = [os.path.join(dicom_dir, i) for i in os.listdir(dicom_dir) if 'resting' in pydcm.read_file(os.path.join(dicom_dir, i)).SeriesDescription]
        nvols    = len(rest_all)
        reader = pydcm.read_file(rest_all[0], force=True)

        if reader.PatientSex is 'F':
            sex = 'female'
        elif reader.PatientSex is 'M':
            sex = 'male'

        # create subject dataframe
        columns = ['Name', 'Site', 'Group', 'Age', 'Sex', 'ScanDate', 'Scanner', 'NCoils', 'Sequence', 'TR', 'TE',
                   'Resolution', 'NVols', 'FlipAngle']
        df = pd.DataFrame(index=['%s' % subject_id], columns=columns)
        df.loc['%s' % subject_id] = pd.Series({'Name': subject,
                                            'Group': group_id,
                                            'Age': reader.PatientAge[:-1],
                                            'Sex': sex,
                                            'ScanDate': reader.AcquisitionDate,
                                            'Scanner': '%sT-%s-%s' % (
                                                reader.MagneticFieldStrength,
                                                reader.Manufacturer,
                                                reader.ManufacturerModelName),
                                            'NCoils': '32',
                                            'Sequence': reader.SeriesDescription,
                                            'TR': str(reader.RepetitionTime),
                                            'TE': str(reader.EchoTime),
                                            'Resolution': '%sx%sx%s' % (
                                                str(reader.PixelSpacing[0])[0:4],
                                                str(reader.PixelSpacing[1])[0:4],
                                                np.round(reader.SpacingBetweenSlices, 3)),
                                            'NVols': nvols,
                                            'FlipAngle': reader.FlipAngle,
                                            'Site': 'Leipzig'
                                            })
        df.to_csv(param_file)

    print LZ_subjects

    # grab all header info into one df
    param_group = []
    for subject in population:
        param_subject = pd.read_csv(os.path.join(afs_dir, LZ_subjects[subject], '%s_param.csv' % LZ_subjects[subject]),
                                    index_col=0)
        param_group.append(param_subject)

    param_group = pd.concat(param_group, ignore_index=False)  # .sort(columns='Age')
    param_group.to_csv(os.path.join(tourettome_phenotypic, 'phenotypic_leipzig.csv'))

make_leipzig_afs(population = LEIPZIG_orig_subject_list,
                 original_datadir =LEIPZIG_orig_datadir,
                 afs_dir = tourettome_afs)

