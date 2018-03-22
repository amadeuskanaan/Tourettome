import os, sys
import dicom as pydcm
import pandas as pd

afs_dir = '/data/pt_nmr093_gts'
population = ['LZ002', 'HA006', 'HB006'] #


def extract_params():

    for subject in population:

        dcm_dir  = os.path.join(afs_dir, subject,'DICOM')

        if subject[0:2] =='LZ':
            sequence_dict = {'T1':'mp2rage_p3_602B_UNI_Images', 'REST': 'cmrr_mbep2d_resting', 'DWI':'cmrr_mbep2d_diff'}
        elif subject[0:2] =='HA':
            sequence_dict = {'T1': 't1_mpr_sag_1iso_p2', 'REST': 'ep2d_bold_restingstate_2.3'}
        elif subject[0:2] == 'HB':
            sequence_dict = {'T1': 'HighResolutionMagdeburg', 'REST': 'REST', 'DWI':'DTI'}

        anat = [os.path.join(dcm_dir, i) for i in os.listdir(dcm_dir) if sequence_dict['T1'] in pydcm.read_file(os.path.join(dcm_dir, i), force=True).SeriesDescription][0]
        rest = [os.path.join(dcm_dir, i) for i in os.listdir(dcm_dir) if sequence_dict['REST'] in pydcm.read_file(os.path.join(dcm_dir, i), force=True).SeriesDescription][0]
        # diff = [os.path.join(dcm_dir, i) for i in os.listdir(dcm_dir) if sequence_dict['DWI'] in pydcm.read_file(os.path.join(dcm_dir, i), force=True).SeriesDescription][0]

        print anat
        print rest
        # print diff

        anat =  pydcm.read_file(anat, force=True)
        rest =  pydcm.read_file(rest, force=True)
        # diff =  pydcm.read_file(diff, force=True)


        T1_params   = ['Vendor', 'Field', 'Transmit_coil_type', 'Recieve_coil_type_nchannels', 'Pulse_Sequence', 'TR', 'TE', 'TI', 'alpha',  'BW', 'FOV','Matrix', 'Parallel_imgtype_AF',
                       'Partial_Fourier_Factor', 'Phase_resol', 'slice_resol', 'n_average', 'TA_min_sec']

        REST_params = ['Vendor', 'Field', 'Transmit_coil_type', 'Recieve_coil_type_nchannels', 'Pulse_Sequence', 'EYES_OC', 'TR', 'TE', 'alpha', 'BW', 'slice_thickness', 'FOV', 'Matrix',
                       'Parallel_fourier_factor', 'n_rep', 'TA']

        DWI_params = ['Vendor', 'Field', 'Max_grad_amp', 'Max_slew', 'transmit_coil_type','recieve_coil_type','pulse_sequence', 'b_factor','n_directions','n_b_0s',
                      'TR','TE','BW','slice_thick','FOV','Matrix','parallel_img_type_af', 'sms_af','partial_fourier_factor', 'n_averages', 'TA']



        df_t1 = pd.DataFrame(index=['T1'])
        df_t1.loc['T1','Vendor'] = '%s_%s' %(anat.Manufacturer, anat.ManufacturerModelName)
        df_t1.loc['T1','Field']  = anat.MagneticFieldStrength
        df_t1.loc['T1', 'Transmit_coil_type'] = anat.MagneticFieldStrength
        df_t1.loc['T1', 'TR'] = anat.RepetitionTime
        df_t1.loc['T1', 'TE'] = anat.EchoTime
        df_t1.loc['T1', 'Alpha'] = anat.FlipAngle
        df_t1.loc['T1', 'BW'] = anat.PixelBandwidth


        print df_t1

extract_params()