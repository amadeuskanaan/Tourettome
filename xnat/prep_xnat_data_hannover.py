__author__ = 'kanaan_28.07.2016'

import os
import pandas as pd
import numpy as np
import dicom as pydcm
import shutil
import zipfile
from variables.subject_list import *

def prep_mhh_data(population, original_datadir, out_datadir):

    df_group = []
    count = 0
    HA_subjects = dict()
    for subject in population:
        count += 1
        xnat_id = 'HA%04d'%count
        HA_subjects[subject] = xnat_id


        print 'Anonymizing HANNOVER_A Data for subject: %s-%s'%(subject, xnat_id)
        zip_orig  = zipfile.ZipFile(os.path.join(original_datadir, '%s.zip' % subject), 'r')
        zip_anon  = os.path.join(out_datadir, xnat_id, '%s'%xnat_id)
        param_file = os.path.join(out_datadir, xnat_id, '%s_param.csv' % xnat_id)
        xnat_dir  = os.path.join(out_datadir, xnat_id, 'DICOM')

        # unzip all files into one directory

        if not os.path.isfile(os.path.join('%s.zip'%zip_anon)):
            print '..extracting'
            zip_orig.extractall(xnat_dir)
            for root, dirs, files in os.walk(xnat_dir):
                for i,file in enumerate(files):
                    shutil.move(os.path.join(root, file), xnat_dir)

            # clean folder
            print '..cleaning'
            for file in os.listdir(xnat_dir):
                if not file.endswith('IMA'):
                    shutil.rmtree(os.path.join(xnat_dir, file), ignore_errors=True)

            # removing patient name from filename
            print '..renaming'
            for i, file in enumerate(os.listdir(xnat_dir)):
                num = '%04d'%i
                shutil.move(os.path.join(xnat_dir, file),
                            os.path.join(xnat_dir, '%s_%s.IMA'%(subject,num)))

            # removing patient name from image header
            print '..anonymizing'
            dicoms = [os.path.join(xnat_dir,dicom) for dicom in os.listdir(xnat_dir) ]
            for dicom in dicoms:
                img = pydcm.read_file(dicom)
                img.PatientName = subject
                img.save_as(os.path.join(xnat_dir,dicom))

            print '..extracting subject parameters'
            rest_all= [os.path.join(xnat_dir, i) for i in os.listdir(xnat_dir) if 'restingstate' in pydcm.read_file(os.path.join(xnat_dir, i)).SeriesDescription]
            nvols = len(rest_all)
            rest = rest_all[0]
            reader = pydcm.read_file(rest)

            if not os.path.isfile(param_file):
                # create subject dataframe
                columns = ['Name', 'Site', 'Group', 'Age', 'Sex', 'ScanDate', 'Scanner', 'Sequence', 'TR', 'TE',
                           'Resolution', 'NVols', 'FlipAngle']
                df = pd.DataFrame(index=['%s' % xnat_id], columns=columns)
                df.loc['%s' % xnat_id] = pd.Series({'Name': subject,
                                                    'Group': [],
                                                    'Age': reader.PatientAge,
                                                    'Sex': reader.PatientSex,
                                                    'ScanDate': reader.AcquisitionDate,
                                                    'Scanner': '%sT-%s-%s' % (
                                                        reader.MagneticFieldStrength,
                                                        reader.Manufacturer,
                                                        reader.ManufacturerModelName),
                                                    'Sequence': reader.SeriesDescription,
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


            # rezipping
            shutil.make_archive(zip_anon, 'zip', xnat_dir)
            shutil.rmtree(xnat_dir)
        df_group.append(pd.read_csv(param_file, index_col=0))

    group_dataframe = pd.concat(df_group, ignore_index=False)#.sort(columns='Age')
    group_dataframe.to_csv(os.path.join(phenotypic_dir, 'subject_list_HANNOVER_A.csv'))

prep_mhh_data(population = HANNOVER_A_subject_list, original_datadir = HANNOVER_A_datadir_in, out_datadir =HANNOVER_A_datadir_out)
