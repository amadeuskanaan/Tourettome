__author__ = 'kanaan_07.11.2016'

import os, sys
import shutil
import zipfile
import dicom as pydcm
import numpy as np
import pandas as pd
sys.path.append(os.path.expanduser('/scr/malta1/Github/Tourettome'))
from utilities.utils import *
from variables.subject_list_original import *


def make_hannoverA_afs(population, original_datadir, afs_dir):

    print '###########################################'
    print ' Creating clean folder for Hannover_A data'
    print '###########################################'

    df_group = []
    count = 0
    HA_subjects = dict()

    for subject in population:
        count += 1
        subject_id = 'HA%03d' % count
        HA_subjects[subject] = subject_id

        print '%s. Organizing data for HANNOVER_A subject %s [%s] in new database dir' % (count, subject_id, subject)

        # create output files and directories
        subject_dir = mkdir_path(os.path.join(afs_dir, subject_id))
        dicom_dir   = mkdir_path(os.path.join(subject_dir, 'DICOM'))
        param_file  = os.path.join(subject_dir, '%s_param.csv' % subject_id)

        # unzip all files into one directory
        zip_orig = zipfile.ZipFile(os.path.join(original_datadir, '%s.zip' % subject), 'r')
        if not os.listdir(dicom_dir):
            print '....Copying dicom data to new database'
            zip_orig.extractall(dicom_dir)
            for root, dirs, files in os.walk(dicom_dir):
                for i, file in enumerate(files):
                    shutil.move(os.path.join(root, file), dicom_dir)
            # clean folder
            for file in os.listdir(dicom_dir):
                if not file.endswith('IMA'):
                    shutil.rmtree(os.path.join(dicom_dir, file), ignore_errors=True)

                if os.path.isfile(os.path.join(dicom_dir, file)):
                    SeriesDescriptions = pydcm.read_file(os.path.join(dicom_dir, file)).SeriesDescription
                    print 'deleting extra files'
                    if 'restingstate' not in SeriesDescriptions and 't1_mpr' not in SeriesDescriptions:
                        os.system('rm -rf %s'%(os.path.join(dicom_dir, file)))

            # removing patient name from filename
            for i, file in enumerate(os.listdir(dicom_dir)):
                num = '%04d' % i
                shutil.move(os.path.join(dicom_dir, file),
                            os.path.join(dicom_dir, '%s_%s.IMA' % (subject, num)))

        if subject[-1] == 'P':
            group_id = 'patients'
        else:
            group_id = 'controls'

        #if not os.path.isfile(param_file):

        print '..extracting subject parameters'



        rest_all = [os.path.join(dicom_dir, i) for i in os.listdir(dicom_dir) if 'restingstate' in pydcm.read_file(os.path.join(dicom_dir, i.decode('utf-8').strip())).SeriesDescription]
        nvols = len(rest_all)
        reader = pydcm.read_file(rest_all[0])

        if reader.PatientSex is 'F':
            sex = 'female'
        elif reader.PatientSex is 'M':
            sex = 'male'


        # create subject dataframe
        columns = ['Name', 'Site', 'Group', 'Age', 'Sex', 'ScanDate', 'Scanner', 'NCoils', 'Sequence', 'TR', 'TE',
                   'Resolution', 'NVols', 'FlipAngle']
        df = pd.DataFrame(index=['%s' % subject_id], columns=columns)
        df.loc['%s' % subject_id] = pd.Series({ 'Name': subject,
                                                'Group': group_id,
                                                'Age': reader.PatientAge[:-1],
                                                'Sex': sex,
                                                'ScanDate': reader.AcquisitionDate,
                                                'Scanner': '%sT-%s-%s' % (
                                                    reader.MagneticFieldStrength,
                                                    reader.Manufacturer,
                                                    reader.ManufacturerModelName),
                                                'Sequence': reader.SeriesDescription,
                                                'NCoils': '32',
                                                'TR': str(reader.RepetitionTime),
                                                'TE': str(reader.EchoTime),
                                                'Resolution': '%sx%sx%s' % (
                                                    str(reader.PixelSpacing[0])[0:4],
                                                    str(reader.PixelSpacing[1])[0:4],
                                                    np.round(reader.SpacingBetweenSlices, 3)),
                                                'NVols': nvols,
                                                'FlipAngle': reader.FlipAngle,
                                                'Site': 'HANNOVER_A'
                                                })
        df.to_csv(param_file)


    print HA_subjects

    #grab all header info into one df
    param_group = []
    for subject in population:
        param_subject = pd.read_csv(os.path.join(afs_dir, HA_subjects[subject], '%s_param.csv' %HA_subjects[subject]), index_col = 0)
        param_group.append(param_subject)

    param_group = pd.concat(param_group, ignore_index=False)#.sort(columns='Age')
    param_group.to_csv(os.path.join(tourettome_phenotypic, 'df_dcm/dicomhdr_hannover_a.csv'))


make_hannoverA_afs(population       = HANNOVER_A_orig_subject_list,
                   original_datadir = HANNOVER_A_orig_datadir,
                   afs_dir          = tourettome_afs)
