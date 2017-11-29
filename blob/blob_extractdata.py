import os

import dicom as pydcm
import pandas as pd


def concat_phenotypic_csv(population, afsdir, phenotypic_dir):

    count = 0
    df_group = []

    for subject in population:

        #convert dicom to nifti
        # nifti_dir = os.path.join(out_dir, 'NIFTI')
        # mkdir_path(nifti_dir)
        # convert_cmd = ['isisconv',
        #                '-in',
        #                '%s' % dcm_dir,
        #                '-out',
        #                '%s/%s_S{sequenceNumber}_{sequenceDescription}_{echoTime}.nii' % (nifti_dir, subject),
        #                '-rf',
        #                'dcm',
        #                '-wdialect',
        #                'fsl']

        # clean nifti DIR
        # if os.listdir(nifti_dir) == []:
        #     subprocess.call(convert_cmd)
        #     os.system('rm -rf %s/*AutoAlignHead_32ch* %s/*MPI* %s/*t2_spc*'%(nifti_dir,nifti_dir,nifti_dir))
        #     anat_files = sorted([os.path.join(nifti_dir, i) for i in os.listdir(nifti_dir) if 't1' in i])
        #     os.system('rm -rf %s'%anat_files[0])
        #     os.system('mv  %s/*rest* %s/rest.nii' % (nifti_dir, nifti_dir))
        #     os.system('mv  %s/*t1* %s/anat.nii' % (nifti_dir, nifti_dir))
        #
        #     os.system('rm -rf %s'%[os.path.join(out_dir, i) for i in os.listdir(out_dir) if 'DICOM' not in i and 'NIFTI' not in i][0])


        rest = [os.path.join(dcm_dir,i) for i in os.listdir(dcm_dir) if 'restingstate' in pydcm.read_file(os.path.join(dcm_dir, i)).SeriesDescription][0]
        reader = pydcm.read_file(rest)
        NAME = reader.PatientName

        columns = [ 'STUDYID', 'Name', 'Age', 'Sex', 'ScanDate', 'Scanner', 'Sequence', 'TR', 'TE', 'Resolution', 'NVols', 'FlipAngle', 'Site']
        df = pd.DataFrame(index = ['%s' % subject], columns = columns)
        df.loc['%s' % subject] = pd.Series({'STUDYID'    :   '10%02d'%count,
                                            'Name'     :   NAME,
                                            'Age'      :   reader.PatientAge,
                                            'Sex'      :   reader.PatientSex,
                                            'ScanDate' :   reader.AcquisitionDate,
                                            'Scanner'  :   '%sT-%s-%s'%(reader.MagneticFieldStrength, reader.Manufacturer, reader.ManufacturerModelName),
                                            'Sequence' :   reader.SeriesDescription,
                                            'TR'       :   reader.RepetitionTime,
                                            'TE'       :   reader.EchoTime,
                                            'Resolution':  '%sx%sx%s' %(str(reader.PixelSpacing[0])[0:3], str(reader.PixelSpacing[1])[0:3], reader.SpacingBetweenSlices),
                                            # 'NVols'    :   nb.load('%s/rest.nii'%nifti_dir).get_data().shape[3],
                                            'FlipAngle':   reader.FlipAngle,
                                            'Site'     :   'Hannover'
                                            })
        print df
        df_group.append(df)

    group_dataframe = pd.concat(df_group, ignore_index=False).sort(columns='Age')

    group_dataframe.to_csv(os.path.join(hannover_datadir, 'hannover1.csv'))


# extractdata_hannover(['TSXP'], hannover_original_datadir, hannover_datadir)
extractdata_hannover(hannover_subjects, hannover_original_datadir, hannover_datadir)

