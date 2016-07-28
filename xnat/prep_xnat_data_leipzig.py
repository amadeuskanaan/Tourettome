__author__ = 'kanaan_28.07.2016'

import os
import pandas as pd
import numpy as np
import dicom as pydcm
import shutil
from variables.subject_list import *
from utilities.utils import *
import glob

def prep_mpi_data(population, original_datadir, out_dir):

    df_group = []
    count = 0
    LZ_subjects = dict()

    for subject in population:
        count += 1
        xnat_id = 'LZ%04d' % count
        LZ_subjects[subject] = xnat_id

        print 'Anonymizing Leipzig Data for subject: %s-%s' % (subject, xnat_id)

        zip_anon = os.path.join(out_dir, xnat_id, '%s' % xnat_id)
        param_file = os.path.join(out_dir, xnat_id, '%s_param.csv' % xnat_id)
        xnat_dir = os.path.join(out_dir, xnat_id, 'DICOM')
        mkdir_path(xnat_dir)

        #grab correct datadir

        if os.path.isdir(os.path.join(original_datadir, 'probands', subject)):
            afs_dir = os.path.join(original_datadir, 'probands', subject)
            group_id = 'controls'
            if subject is 'GF3T' or subject is 'ZT5T':
                afs_dir = os.path.join('/a/projects/nmr093b/', 'probands', subject)
                group_id = 'controls'
            elif subject is 'GSAP':
                afs_dir = os.path.join(original_datadir, 'patients', subject)
                group_id = 'patients'
        else:
            afs_dir = os.path.join(original_datadir, 'patients', subject)
            group_id = 'patients'

        if not os.path.isfile(os.path.join('%s.zip'%zip_anon)):

            # grab anat and rest dioom data
            scans = find('Scans.txt', afs_dir)
            rest_id = str([line for line in open(scans).readlines() if 'resting' in line])[2:6]
            se_id = str([line for line in open(scans).readlines() if 'cmrr_mbep2d_se' in line])[2:6]
            seinv_id = str([line for line in open(scans).readlines() if 'cmrr_mbep2d_se_invpol' in line])[2:6]
            uni_id  = str([line for line in open(scans).readlines() if 'UNI' in line and 'SLAB' not in line])[2:6]

            for id in [rest_id, se_id, seinv_id, uni_id]:
                for file in glob.glob(os.path.join(afs_dir, 'DICOM/%s*'%id)):
                    shutil.copy(file, xnat_dir)

            # remove subject name from header
            print '..anonymizing'
            dicoms = [os.path.join(xnat_dir, dicom) for dicom in os.listdir(xnat_dir)]
            for dicom in dicoms:
                img = pydcm.read_file(dicom)
                img.PatientID = subject
                img.save_as(os.path.join(xnat_dir, dicom))

            print '..extracting subject parameters'

            if not os.path.isfile(param_file):
                rest_all = [os.path.join(xnat_dir, i) for i in os.listdir(xnat_dir) if
                            'resting' in pydcm.read_file(os.path.join(xnat_dir, i)).SeriesDescription]
                nvols = len(rest_all)
                rest = rest_all[0]

                reader = pydcm.read_file(rest, force = True)
                # create subject dataframe
                columns = ['Name', 'Site', 'Group', 'Age', 'Sex', 'ScanDate', 'Scanner', 'Sequence', 'TR', 'TE',
                           'Resolution', 'NVols', 'FlipAngle' ]
                df = pd.DataFrame(index=['%s' % xnat_id], columns=columns)
                df.loc['%s' % xnat_id] = pd.Series({'Name': subject,
                                                    'Group': group_id,
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
                                                        np.round(reader.SpacingBetweenSlices,3)),
                                                    'NVols': nvols,
                                                    'FlipAngle': reader.FlipAngle,
                                                    'Site': 'Leipzig'
                                                    })

                df.to_csv(param_file)

            # rezipping
            print '..re-zipping'
            shutil.make_archive(zip_anon, 'zip', xnat_dir)
            shutil.rmtree(xnat_dir)

        df_group.append(pd.read_csv(param_file, index_col=0))

    group_dataframe = pd.concat(df_group, ignore_index=False)#.sort(columns='Age')
    group_dataframe.to_csv(os.path.join(phenotypic_dir, 'subject_list_LEIPZIG.csv'))

    print LZ_subjects

prep_mpi_data(population=LEIPZIG_subject_list,
              original_datadir=LEIPZIG_datadir_in,
              out_dir=LEIPZIG_datadir_out)