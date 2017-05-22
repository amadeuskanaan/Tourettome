

tourettome_afs          = '/data/pt_nmr093_gts'
tourettome_workspace    = '/scr/malta4/workspace/project_TOURETTOME/preproc'
tourettome_phenotypic   = '/scr/malta4/workspace/project_TOURETTOME/phenotypic'
tourettome_freesurfer   = '/scr/malta2/TOURETTOME/FS_SUBJECTS'



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

leipzig = [ 'LZ002', 'LZ003', 'LZ004', 'LZ005', 'LZ006', 'LZ007', 'LZ008', 'LZ009', 'LZ010',
           'LZ011', 'LZ012', 'LZ013', 'LZ014', 'LZ015', 'LZ016', 'LZ017', 'LZ018', 'LZ019', 'LZ020',
           'LZ021', 'LZ022', 'LZ023', 'LZ024', 'LZ025', 'LZ026', 'LZ027', 'LZ028', 'LZ029', 'LZ030',
           'LZ031', 'LZ032', 'LZ033', 'LZ034', 'LZ035', 'LZ036', 'LZ037', 'LZ038', 'LZ039', 'LZ040',
           'LZ041', 'LZ042', 'LZ043', 'LZ044', 'LZ045', 'LZ046', 'LZ047', 'LZ048', 'LZ049', 'LZ050',
           'LZ051', 'LZ052', 'LZ053', 'LZ054', 'LZ055', 'LZ056', 'LZ057', 'LZ058', 'LZ059', 'LZ060',
           'LZ061', 'LZ062', 'LZ063', 'LZ064', 'LZ065', 'LZ066', 'LZ067', 'LZ068', 'LZ069', 'LZ070',
           'LZ071', 'LZ072', 'LZ073', 'LZ074', 'LZ075', 'LZ076'] # 'LZ001'

hannover_a  = ['HA001', 'HA002', 'HA003', 'HA004', 'HA005', 'HA006', 'HA007', 'HA008', 'HA009', 'HA010',
               'HA011', 'HA012', 'HA013', 'HA014', 'HA015', 'HA016', 'HA017', 'HA018', 'HA019', 'HA020',
               'HA021', 'HA022', 'HA023', 'HA024', 'HA025', 'HA026', 'HA027', 'HA028', 'HA029', 'HA030',
               'HA031', 'HA032', 'HA033', 'HA034', 'HA035', 'HA036', 'HA037', 'HA038', 'HA039', 'HA040',
               'HA041', 'HA042', 'HA043', 'HA044', 'HA045', 'HA046', 'HA047', 'HA048', 'HA049', 'HA050',
               'HA051', 'HA052', 'HA053', 'HA054']

hannover_b  = ['HB001', 'HB002', 'HB003', 'HB004', 'HB005', 'HB006', 'HB007', 'HB008', 'HB009', 'HB010',
               'HB011', 'HB012', 'HB013', 'HB014', 'HB015', 'HB016', 'HB017', 'HB018', 'HB019', 'HB020',
               'HB021', 'HB022', 'HB023', 'HB024', 'HB025', 'HB026', 'HB027', 'HB028', 'HB029', 'HB030',
               'HB031', 'HB032', 'HB033']

hamburg = []


paris1 = paris[:40]
paris2 = paris[40:]
leipzig1 = leipzig[:35]
leipzig2 = leipzig[35:]
hannover_a1 = hannover_a[:25]
hannover_a2 = hannover_a[25:]

tourettome_subjects = leipzig + paris + hannover_a + hannover_b

########################################################################################################################
mni_brain_1mm        = '/usr/share/fsl/5.0/data/standard/MNI152_T1_1mm_brain.nii.gz'
mni_brain_2mm        = '/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain.nii.gz'
mni_brain_2mm_mask   = '/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain_mask.nii.gz'
mni_HOLV_2mm         = '/scr/sambesi2/Github/Tourettome/resources/HarvardOxford-lateral-ventricles-thr25-2mm.nii.gz'
bbr_schedule         = '/usr/share/fsl/5.0/etc/flirtsch/bbr.sch'

fs_mni_reg = '/afs/cbs.mpg.de/software/freesurfer/6.0.0/ubuntu-xenial-amd64/average/mni152.register.dat'

rois = ['R_Caud', 'L_Caud', 'R_Puta', 'L_Puta', 'R_Pall', 'L_Pall', 'R_Amyg', 'L_Amyg', 'R_Hipp', 'L_Hipp', 'R_Accu', 'L_Accu',
        'R_Thal', 'L_Thal']

rois_bilateral = ['Caud', 'Puta', 'Pall',  'Amyg', 'Hipp', 'Accu', 'Thal']



##########################################################################
# META ICA LISTS
LEIPZIG_A_subject_dict =  {
 'AA8P': 'LZ001', 'BATP': 'LZ002', 'BE9P': 'LZ003', 'BM8X': 'LZ040', 'CB4P': 'LZ004', 'CF1P': 'LZ005', 'CM5P': 'LZ006', 'DF2P': 'LZ007',
 'EB2P': 'LZ008', 'EC9T': 'LZ041', 'EW3P': 'LZ009', 'FL3P': 'LZ010', 'FMEP': 'LZ011', 'GF3T': 'LZ042', 'GH4T': 'LZ043', 'GSAP': 'LZ012',
 'GSAT': 'LZ044', 'GSNT': 'LZ045', 'HCTT': 'LZ046', 'HHQP': 'LZ013', 'HJEP': 'LZ014', 'HM1X': 'LZ047', 'HM2X': 'LZ048', 'HMXP': 'LZ015',
 'HR8T': 'LZ049', 'HRPP': 'LZ016', 'HSPP': 'LZ017', 'KDDP': 'LZ018', 'KO4T': 'LZ050', 'LA9P': 'LZ019', 'LJ9P': 'LZ020', 'LL5T': 'LZ051',
 'LMIT': 'LZ052', 'LT5P': 'LZ021', 'MJBT': 'LZ053', 'NL2P': 'LZ022', 'NP4T': 'LZ054', 'NT6P': 'LZ023', 'PAHT': 'LZ055', 'PC5P': 'LZ024',
 'PU2T': 'LZ056', 'RA7T': 'LZ057', 'RA9P': 'LZ025', 'RB1T': 'LZ058', 'RJBT': 'LZ059', 'RJJT': 'LZ060', 'RL7P': 'LZ026', 'RMJP': 'LZ027',
 'RMNT': 'LZ061', 'RSIP': 'LZ028', 'SA5U': 'LZ029', 'SBQP': 'LZ030', 'SC1T': 'LZ062', 'SDCT': 'LZ063', 'SGKP': 'LZ031', 'SI5T': 'LZ064',
 'SJBT': 'LZ065', 'SJVT': 'LZ066', 'SM6U': 'LZ032', 'SMVX': 'LZ067', 'SS1X': 'LZ068', 'STDP': 'LZ033', 'STQT': 'LZ069', 'SULP': 'LZ034',
 'THCP': 'LZ035', 'TJ5T': 'LZ070', 'TR4T': 'LZ071', 'TSCT': 'LZ072', 'TSEP': 'LZ036', 'TT3P': 'LZ037', 'TV1T': 'LZ073', 'WJ3T': 'LZ074',
 'WO2P': 'LZ038', 'WSKT': 'LZ075', 'YU1P': 'LZ039', 'ZT5T': 'LZ076'}


PARIS_subject_dict ={'Sujet01p': 'PA001',  'sujet02p': 'PA002',  'sujet03p': 'PA003',  'Sujet04p': 'PA004',  'Sujet05p': 'PA005',
                     'Sujet06p': 'PA006',  'sujet07p': 'PA007',  'sujet08p': 'PA008',  'Sujet09p': 'PA009',  'sujet10p': 'PA010',
                     'sujet11p': 'PA011',  'sujet12p': 'PA012',  'sujet13p': 'PA013',  'sujet14p': 'PA014',  'sujet15p': 'PA015',
                     'sujet16p': 'PA016',  'sujet17t': 'PA017',  'Sujet18p': 'PA018',  'Sujet19p': 'PA019',  'sujet20t': 'PA020',
                     'sujet21t': 'PA021',  'sujet22t': 'PA022',  'sujet23t': 'PA023',  'sujet24t': 'PA024',  'sujet25p': 'PA025',
                     'sujet26p': 'PA026',  'sujet27p': 'PA027',  'sujet28p': 'PA028',  'sujet29p': 'PA029',  'sujet30t': 'PA030',
                     'sujet31p': 'PA031',  'sujet32p': 'PA032',  'sujet33t': 'PA033',  'sujet35p': 'PA035',  'sujet36t': 'PA036',
                     'sujet37p': 'PA037',  'sujet38p': 'PA038',  'sujet39p': 'PA039',  'sujet40p': 'PA040',  'sujet41t': 'PA041',
                     'sujet42t': 'PA042',  'sujet43t': 'PA043',  'sujet44t': 'PA044',  'sujet45p': 'PA045',  'sujet46p': 'PA046',
                     'sujet47p': 'PA047',  'sujet48p': 'PA048',  'sujet49p': 'PA049',  'sujet50t': 'PA050',  'sujet51p': 'PA051',
                     'sujet52p': 'PA052',  'sujet53p': 'PA053',  'sujet54t': 'PA054',  'sujet55p': 'PA055',  'sujet56t': 'PA056',
                     'sujet58p': 'PA058',  'sujet59t': 'PA059',  'sujet60p': 'PA060',  'sujet61p': 'PA061',  'sujet62t': 'PA062',
                     'sujet63t': 'PA063',  'sujet64t': 'PA064',  'sujet66p': 'PA066',  'sujet67t': 'PA067',  'sujet68t': 'PA068',
                     'sujet69p': 'PA069',  'sujet70t': 'PA070',  'sujet71p': 'PA071',  'sujet72t': 'PA072',  'sujet73t': 'PA073',
                     'sujet74p': 'PA074',  'sujet75t': 'PA075',  'sujet76p': 'PA076',  'sujet77p': 'PA077',  'sujet78p': 'PA078',
                     'sujet79p': 'PA079',  'sujet80p': 'PA080',  'sujet81p': 'PA081',  'sujet82p': 'PA082',  'sujet83t': 'PA083',
                     'sujet84t': 'PA084',  'sujet85p': 'PA085',  'sujet87p': 'PA087',  'sujet88t': 'PA088',  'sujet89t': 'PA089',
                     'sujet90p': 'PA090',  'sujet91p': 'PA091', 'sujet92p': 'PA092', 'sujet93p': 'PA093',  'sujet94p': 'PA094',
                     'sujet95p': 'PA095',  'sujet96p': 'PA096'}


HANNOVER_A_subject_dict = {'AAXP': 'HA001', 'BRXP': 'HA002', 'CSXP': 'HA003', 'DJXP': 'HA004', 'ETXP': 'HA005',
                           'FDXP': 'HA006', 'GSXP': 'HA007', 'GTXP': 'HA008', 'HHQP': 'HA009', 'HHXP': 'HA010',
                           'JJXP': 'HA011', 'JTXP': 'HA012', 'KCXP': 'HA013', 'KNXP': 'HA014', 'LFXP': 'HA015',
                           'LJXP': 'HA016', 'LLXP': 'HA017', 'LMXP': 'HA018', 'LNXP': 'HA019', 'LPXP': 'HA020',
                           'LT5P': 'HA021', 'MAXP': 'HA022', 'MLXP': 'HA023', 'MMXP': 'HA024', 'NSXP': 'HA025',
                           'SBXP': 'HA026', 'SDXP': 'HA027', 'TSXP': 'HA028', 'VHXP': 'HA029', 'WWXP': 'HA030',
                           'ZDXP': 'HA031', 'H151': 'HA032', 'H153': 'HA033', 'H155': 'HA034', 'H156': 'HA035',
                           'H157': 'HA036', 'H158': 'HA037', 'H162': 'HA038', 'H163': 'HA039', 'H165': 'HA040',
                           'H167': 'HA041', 'H168': 'HA042', 'H169': 'HA043', 'H171': 'HA044', 'H172': 'HA045',
                           'H173': 'HA046', 'H174': 'HA047', 'H175': 'HA048', 'H176': 'HA049', 'H178': 'HA050',
                           'H179': 'HA051', 'H180': 'HA052', 'H181': 'HA053', 'H182': 'HA054',
                           }


lz_patients = [i for i in LEIPZIG_A_subject_dict.keys() if i[-1] == 'P' or i[-1] == 'U']
lz_controls = [i for i in LEIPZIG_A_subject_dict.keys() if i[-1] == 'T' or i[-1] == 'X']

#print len(LEIPZIG_A_subject_dict.keys())
#print len(lz_controls + lz_controls)

pa_patients = [i for i in PARIS_subject_dict.keys() if i[-1] == 'p']
pa_controls = [i for i in PARIS_subject_dict.keys() if i[-1] == 't']

#print len(PARIS_subject_dict.keys())
#print len(pa_patients + pa_controls)

ha_patients = [i for i in HANNOVER_A_subject_dict.keys() if i[-1] == 'P']
ha_controls = [i for i in HANNOVER_A_subject_dict.keys() if i[-1] != 'P']

#print len(HANNOVER_A_subject_dict.keys())
#print len(ha_patients + ha_controls)