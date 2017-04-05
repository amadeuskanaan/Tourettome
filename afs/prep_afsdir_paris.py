__author__ = 'kanaan_07.10.2016'

import fnmatch
import os
import shutil

import dicom as pydcm
import numpy as np
import pandas as pd

from utilities.utils import mkdir_path
from variables.subject_list_original import *


def make_paris_afs(population, original_datadir, afs_dir):

    print '###########################################'
    print '  Creating clean folder for PARIS data'
    print '###########################################'

    count = 0
    PA_subjects = dict()
    for subject in population:
        count += 1
        subject_id           = 'PA0%s' % subject[5:7]
        PA_subjects[subject] = subject_id

        if subject[-1] == 'p' or subject[-1] == 'P':
            group_id = 'patients'
        elif subject[-1] == 't' or subject[-1] == 'T':
            group_id = 'controls'


        print '%s. Organizing data for PARIS %s %s [%s] in new afs dir' % (count, group_id[:-1], subject_id, subject)

        tar_file    = [os.path.join(original_datadir, file) for file in os.listdir(original_datadir) if fnmatch.fnmatch(file, '*%s*' % subject)][0]
        subject_dir = mkdir_path(os.path.join(afs_dir, subject_id))
        dicom_dir   = mkdir_path(os.path.join(subject_dir, 'DICOM'))
        param_file  = os.path.join(subject_dir, '%s_param.csv' % subject_id)

        # copy anat and rest dicom data to afs directory
        if not os.listdir(dicom_dir):
            print '....Copying dicom data to new afs'
            os.system('tar -xvf %s -C %s' % (tar_file, dicom_dir))
            for root, dirs, files in os.walk(dicom_dir):
                for i, file in enumerate(files):
                    shutil.move(os.path.join(root, file), dicom_dir)

            # clean folder
            for file in os.listdir(dicom_dir):
                if not file.endswith('IMA'):
                    shutil.rmtree(os.path.join(dicom_dir, file), ignore_errors=True)


        # if not os.path.isfile('x'):
        print '..extracting subject parameters'
        rest_all = [os.path.join(dicom_dir, i) for i in os.listdir(dicom_dir) if 'Resting' in pydcm.read_file(os.path.join(dicom_dir, i)).SeriesDescription]
        nvols = len(rest_all)
        reader = pydcm.read_file(rest_all[0])

        # create subject dataframe
        columns = ['Name', 'Site', 'Group', 'Age', 'Sex', 'ScanDate', 'Scanner', 'NCoils', 'Sequence', 'TR',
                   'TE', 'Resolution', 'NVols', 'FlipAngle']
        df = pd.DataFrame(index=['%s' % subject_id], columns=columns)
        df.loc['%s' % subject_id] = pd.Series({'Name': subject,
                                            'Group': group_id,
                                            'Age': reader.PatientAge,
                                            'Sex': reader.PatientSex,
                                            'ScanDate': reader.AcquisitionDate,
                                            'Scanner': '%sT-%s-%s' % (
                                                reader.MagneticFieldStrength,
                                                reader.Manufacturer,
                                                reader.ManufacturerModelName),
                                            'Sequence': reader.SeriesDescription,
                                            'NCoils': '12',
                                            'TR': str(reader.RepetitionTime),
                                            'TE': str(reader.EchoTime),
                                            'Resolution': '%sx%sx%s' % (
                                                str(reader.PixelSpacing[0])[0:4],
                                                str(reader.PixelSpacing[1])[0:4],
                                                np.round(reader.SpacingBetweenSlices, 3)),
                                            'NVols': nvols,
                                            'FlipAngle': reader.FlipAngle,
                                            'Site': 'PARIS'
                                            })
        df.to_csv(param_file)


    print PA_subjects

    # grab all header info into one df
    param_group = []
    for subject in population:
        param_subject = pd.read_csv(os.path.join(afs_dir, PA_subjects[subject], '%s_param.csv' % PA_subjects[subject]),
                                    index_col=0)
        param_group.append(param_subject)

    param_group = pd.concat(param_group, ignore_index=False)  # .sort(columns='Age')
    param_group.to_csv(os.path.join(tourettome_phenotypic, 'phenotypic_paris.csv'))

make_paris_afs(population = PARIS_orig_subject_list,
               original_datadir = PARIS_datadir_orig_datadir,
               afs_dir = tourettome_afs)

