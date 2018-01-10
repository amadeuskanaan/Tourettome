__author__ = 'kanaan_02.12.2016'

import os
import sys
# from variables.subject_list import *


# assert len(sys.argv)== 2
# subject_index=int(sys.argv[1])

def preprocess_anatomical(population, afs_dir, workspace, freesurfer_dir):

    for subject in population:
        # subject = population[subject_index]
        print '========================================================================================'
        print '%s-Preprocessing anatomical data for %s' %(subject, subject)

        # input
        # anatdir = os.path.join(workspace, subject, 'ANATOMICAL')
        anatdir = os.path.join(afs_dir, subject, 'NIFTI')


        # Freesurfer Reconall
        ## For best results across the multi-site data, Reconall is run on skull stripped Anatomical data.
        ## This is mainly done since stripping out-of-head noise on MP2RAGE data usually fails with BET algorithms.
        ## Erroneous segmentation may also occur for MP2RAGE data with abnormal morphology

        if freesurfer_dir:
            if not os.path.isfile(os.path.join(freesurfer_dir, subject, 'mri', 'aparc.DKTatlas+aseg.mgz' )):
                print '... Running Freesurfer'
                from nipype.workflows.smri.freesurfer import create_skullstripped_recon_flow
                os.system('rm -rf %s' %(os.path.join(freesurfer_dir, subject)))
                recon_flow = create_skullstripped_recon_flow()
                recon_flow.inputs.inputspec.subject_id = subject
                recon_flow.inputs.inputspec.T1_files = os.path.join(anatdir, 'ANATOMICAL_BRAIN.nii.gz')
                recon_flow.inputs.inputspec.subjects_dir = freesurfer_dir
                recon_flow.run()

# recon_checker = [subject for subject in tourettome_subjects if subject not in missing]




paris = ['PA001', 'PA002', 'PA003', 'PA004', 'PA005', 'PA006', 'PA007', 'PA008', 'PA009', 'PA010',
         'PA011', 'PA012', 'PA013', 'PA014', 'PA015', 'PA016', 'PA017', 'PA018', 'PA019', 'PA020',
         'PA021', 'PA022', 'PA023', 'PA024', 'PA025', 'PA026', 'PA027', 'PA028', 'PA029', 'PA030',
         'PA031', 'PA032', 'PA033', 'PA035', 'PA036', 'PA037', 'PA038', 'PA039', 'PA040', 'PA041',
         'PA042', 'PA043', 'PA044', 'PA045', 'PA046', 'PA047', 'PA048', 'PA049', 'PA050', 'PA051',
         'PA052', 'PA053', 'PA054', 'PA055', 'PA056', 'PA058', 'PA059', 'PA060', 'PA061', 'PA062',
         'PA063', 'PA064', 'PA066', 'PA067', 'PA068', 'PA069', 'PA070', 'PA071', 'PA072', 'PA073',
         'PA074', 'PA075', 'PA076', 'PA077', 'PA078', 'PA079', 'PA080', 'PA081', 'PA082', 'PA083',
         'PA084', 'PA085', 'PA087', 'PA088', 'PA089', 'PA090', 'PA091', 'PA092', 'PA093', 'PA094',
         'PA095', 'PA096']

leipzig = ['LZ001', 'LZ002', 'LZ003', 'LZ004', 'LZ005', 'LZ006', 'LZ007', 'LZ008', 'LZ009', 'LZ010',
           'LZ011', 'LZ012', 'LZ013', 'LZ014', 'LZ015', 'LZ016', 'LZ017', 'LZ018', 'LZ019', 'LZ020',
           'LZ021', 'LZ022', 'LZ023', 'LZ024', 'LZ025', 'LZ026', 'LZ027', 'LZ028', 'LZ029', 'LZ030',
           'LZ031', 'LZ032', 'LZ033', 'LZ034', 'LZ035', 'LZ036', 'LZ037', 'LZ038', 'LZ039', 'LZ040',
           'LZ041', 'LZ042', 'LZ043', 'LZ044', 'LZ045', 'LZ046', 'LZ047', 'LZ048', 'LZ049', 'LZ050',
           'LZ051', 'LZ052', 'LZ053', 'LZ054', 'LZ055', 'LZ056', 'LZ057', 'LZ058', 'LZ059', 'LZ060',
           'LZ061', 'LZ062', 'LZ063', 'LZ064', 'LZ065', 'LZ066', 'LZ067', 'LZ068', 'LZ069', 'LZ070',
           'LZ071', 'LZ072', 'LZ073', 'LZ074', 'LZ075', 'LZ076']

hannover_a = ['HA001', 'HA002', 'HA003', 'HA004', 'HA005', 'HA006', 'HA007', 'HA008', 'HA009', 'HA010',
              'HA011', 'HA012', 'HA013', 'HA014', 'HA015', 'HA016', 'HA017', 'HA018', 'HA019', 'HA020',
              'HA021', 'HA022', 'HA023', 'HA024', 'HA025', 'HA026', 'HA027', 'HA028', 'HA029', 'HA030',
              'HA031', 'HA032', 'HA033', 'HA034', 'HA035', 'HA036', 'HA037', 'HA038', 'HA039', 'HA040',
              'HA041', 'HA042', 'HA043', 'HA044', 'HA045', 'HA046', 'HA047', 'HA048', 'HA049', 'HA050',
              'HA051', 'HA052', 'HA053', 'HA054']

hannover_b = ['HB001', 'HB002', 'HB003', 'HB004', 'HB005', 'HB006', 'HB007', 'HB008', 'HB009', 'HB010',
              'HB011', 'HB012', 'HB013', 'HB014', 'HB015', 'HB016', 'HB017', 'HB018', 'HB019', 'HB020',
              'HB021', 'HB022', 'HB023', 'HB024', 'HB025', 'HB026', 'HB027', 'HB028', 'HB029', 'HB030',
              'HB031', 'HB032', 'HB033']

hamburg = ['HM001', 'HM002', 'HM003', 'HM004', 'HM005', 'HM006', 'HM007', 'HM008', 'HM009', 'HM010',
           'HM011', 'HM012', 'HM014', 'HM015', 'HM017', 'HM019', 'HM020', 'HM022', 'HM023', 'HM024',
           'HM025', 'HM026', 'HM027', 'HM028', 'HM029', 'HM030', 'HM031', 'HM032', 'HM033']

fsdir = '/data/pt_nmr093_gts/freesurfer'
# os.system('export SUBJECTS_DIR=/data/pt_nmr093_gts/freesurfer')
# os.system('$SUBJECTS_DIR')

tourettome_afs         = '/data/pt_nmr093_gts'
tourettome_base        = '/scr/malta4/workspace/project_TOURETTOME'
tourettome_workspace   = '/scr/malta4/workspace/project_TOURETTOME/preproc'
tourettome_phenotypic  = '/scr/malta4/workspace/project_TOURETTOME/phenotypic'
tourettome_freesurfer  = '/scr/malta4/workspace/project_TOURETTOME/freesurfer'
tourettome_derivatives = '/scr/malta4/workspace/project_TOURETTOME/derivatives'

all_pops = leipzig+paris+hamburg+hannover_b+hannover_a

#preprocess_anatomical(population =hamburg[25:], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =hannover_a[0:35], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =hannover_a[35:40], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =hannover_a[40:45], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =hannover_a[45:50], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =hannover_a[50:], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)

#preprocess_anatomical(population =hannover_b[0:5], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =hannover_b[5:10], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =hannover_b[10:15], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =hannover_b[15:20], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =hannover_b[20:25], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =hannover_b[25:], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)

#preprocess_anatomical(population =leipzig[1:5], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[5:10], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[10:15], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[15:20], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[20:25], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[25:30], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[30:35], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[35:40], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[40:45], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[45:50], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[52:55], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[57:60], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[60:65], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[65:70], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =leipzig[70:], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)


#preprocess_anatomical(population =paris[0:5], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[5:10], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[10:15], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[15:20], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[20:25], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[25:30], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[30:35], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[35:40], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[40:45], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[45:50], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[50:55], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[55:60], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[60:65], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[65:70], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[70:75], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[75:80], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
# preprocess_anatomical(population =paris[80:85], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
# preprocess_anatomical(population =paris[85:90], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
# preprocess_anatomical(population =paris[90:], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)



preprocess_anatomical(population =paris[48:50], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[54:55], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[59:60], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[64:65], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[69:70], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[74:75], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[79:80], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[84:85], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)
#preprocess_anatomical(population =paris[88:90], afs_dir = tourettome_afs, workspace = tourettome_workspace, freesurfer_dir= fsdir)