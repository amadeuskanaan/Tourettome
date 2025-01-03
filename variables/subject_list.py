########################################################################################################################
#### Input/output

tourettome_afs         = '/data/pt_nmr093_gts'
tourettome_base        = '/scr/malta4/workspace/project_TOURETTOME'
tourettome_workspace   = '/scr/malta4/workspace/project_TOURETTOME/preproc'
tourettome_phenotypic  = '/scr/malta4/workspace/project_TOURETTOME/phenotypic'
tourettome_freesurfer  = '/scr/malta4/workspace/project_TOURETTOME/freesurfer'
tourettome_derivatives = '/scr/malta4/workspace/project_TOURETTOME/derivatives'

########################################################################################################################
#### Subject Lists

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

tourettome_subjects = leipzig + paris + hannover_a + hannover_b + hamburg
unsuable_datasets   = ['LZ001', 'LZ052']
# LZ052 stilll salvagable, but need to create a new dummy loop for brain extraction. try BET after thresholding INV or T1MAPS
tourettome_subjects = [subject for subject in tourettome_subjects if subject not in unsuable_datasets + hamburg]

########################################################################################################################
# Outliers
## Artifacts          --- Hamburg datasets..
## Missing Data       --- LZ001, LZ052 are missing data
## Segmentation Fault --- ['LZ057', 'LZ058', 'PA055', 'HB014', 'HB015', 'HB019', 'HM029']


# QC based on fd_max > 1.5 and fd_mu> 0.2
control_outliers = ['HM015', 'LZ061', 'LZ052', 'LZ057', 'LZ058',
                    'HB019',
                    #'HM001', 'HM004', 'HM006', 'HM012', 'HM014', 'HM017', 'HM019', 'HM022', 'HM025', 'HM027',
                    #'HM028', 'HM029', 'HM030', 'HM032'
                    ]

patient_outliers = ['HA009', 'HB005', 'HM015', 'HM023', 'HM026', 'LZ004', 'LZ006', 'LZ007', 'LZ013', 'LZ017',
                    'LZ018', 'LZ020', 'LZ025', 'LZ027', 'LZ028', 'LZ029', 'LZ030', 'LZ031', 'LZ035', 'LZ038',
                    'PA001', 'PA006', 'PA009', 'PA012', 'PA013', 'PA019', 'PA025', 'PA039', 'PA045', 'PA052',
                    'PA055', 'PA058', 'PA077', 'PA078', 'PA080', 'PA081', 'PA094', 'LZ001',
                    'PA055', 'HB014', 'HB015',
                    #'HM002', 'HM003', 'HM005', 'HM007', 'HM008', 'HM009', 'HM010', 'HM011', 'HM020', 'HM024',
                    #'HM031', 'HM033'
                    ]


########################################################################################################################
#### Resources

mni_head_1mm        = '/usr/share/fsl/5.0/data/standard/MNI152_T1_1mm.nii.gz'
mni_brain_1mm        = '/usr/share/fsl/5.0/data/standard/MNI152_T1_1mm_brain.nii.gz'
mni_brain_2mm        = '/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain.nii.gz'
mni_brain_2mm_mask   = '/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain_mask.nii.gz'
mni_brain_3mm        = '/usr/share/fsl/5.0/data/standard/MNI152_T1_3mm_symmetric.nii.gz'
mni_HOLV_2mm         = '/scr/malta1/Github/Tourettome/resources/HarvardOxford-lateral-ventricles-thr25-2mm.nii.gz'
mni_HOLV_3mm         = '/scr/malta1/Github/Tourettome/resources/HarvardOxford-lateral-ventricles-thr25-3mm.nii.gz'
bbr_schedule         = '/usr/share/fsl/5.0/etc/flirtsch/bbr.sch'
fs_mni_reg           = '/afs/cbs.mpg.de/software/freesurfer/6.0.0/ubuntu-xenial-amd64/average/mni152.register.dat'

mask_str        = '/scr/malta1/Github/Tourettome/atlases/STR.nii.gz'
mask_str_motor  = '/scr/malta1/Github/Tourettome/atlases/STR3_MOTOR.nii.gz'
mask_str_limbic = '/scr/malta1/Github/Tourettome/atlases/STR3_LIMBIC.nii.gz'
mask_str_exec   = '/scr/malta1/Github/Tourettome/atlases/STR3_EXEC.nii.gz'
mask_caud    = '/scr/malta1/Github/Tourettome/atlases/Caud.nii.gz'
mask_puta   = '/scr/malta1/Github/Tourettome/atlases/Puta.nii.gz'
mask_pall   = '/scr/malta1/Github/Tourettome/atlases/Pall.nii.gz'
mask_accu   = '/scr/malta1/Github/Tourettome/atlases/Accu.nii.gz'
mask_thal   = '/scr/malta1/Github/Tourettome/atlases/Thal.nii.gz'
mask_hipp   = '/scr/malta1/Github/Tourettome/atlases/Hipp.nii.gz'
mask_amyg   = '/scr/malta1/Github/Tourettome/atlases/Amyg.nii.gz'

nuclei_bilateral   = ['Caudate', 'Putamen', 'Accumbens-area', 'Pallidum', 'Hippocampus', 'Amygdala', 'Thalamus-Proper']
nuclei_left        = ['Left-' + nucleus for nucleus in nuclei_bilateral]
nuclei_right       = ['Right-' + nucleus for nucleus in nuclei_bilateral]
nuclei_subcortical = nuclei_left + nuclei_right


